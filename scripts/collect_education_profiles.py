"""教育全量精确星图ID补充：inventory/fetch/generate/verify，不构建或发布。

python3 scripts/collect_education_profiles.py --mode inventory
python3 scripts/collect_education_profiles.py --mode fetch --workers 3
python3 scripts/collect_education_profiles.py --mode generate --mirror ../talent-supply-hub-public
python3 scripts/collect_education_profiles.py --mode verify --mirror ../talent-supply-hub-public

只使用映射中的 unique_id；short_id 仅供 displayId，不作为主页证据。
支持 --mapping-file 最新 dataset SQL rows JSON；不会调用或改动线上 DSL。
原图及逐ID请求证据仅存 workspace .cache/avatars/education_latest，不进入包。
"""
import argparse
import concurrent.futures as cf
import gzip
import hashlib
import json
import math
import re
import shutil
import threading
import time
from collections import Counter
from datetime import datetime, timezone
from io import BytesIO
from pathlib import Path

import requests
from PIL import Image, ImageOps

ROOT = Path(__file__).resolve().parents[1]
SEC = re.compile(r'^MS4wLj[A-Za-z0-9_-]{30,}$')
SID = re.compile(r'^(?:\d{19}|\d{16})$')
HEADERS = {'User-Agent': 'Mozilla/5.0', 'Referer': 'https://www.iesdouyin.com/'}
API = 'https://www.iesdouyin.com/web/api/v2/user/info/'


def load(path):
    b = path.read_bytes()
    return json.loads(gzip.decompress(b) if b[:2] == b'\x1f\x8b' else b)


def save(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n')


def sec_of(value):
    if isinstance(value, dict):
        value = value.get('profileUrl') or ''
    if not isinstance(value, str):
        return None
    sec = value.removeprefix('https://www.douyin.com/user/')
    return sec if SEC.fullmatch(sec) else None


def read_targets(root):
    # JSON .data + JSON sample：不使用昵称/行业样本TS regex推断目标。
    data = load(root / 'download-assets/industry-education.data')
    col = data['headers'].index('达人星图id')
    order = list(dict.fromkeys(str(row[col]) for row in data['rows']))
    assert len(order) == len(data['rows']) and all(SID.fullmatch(s) for s in order)
    sample_path = root / 'src/data/educationSample.json'
    sample = load(sample_path) if sample_path.exists() else {**data, 'rows': data['rows'][:100]}
    scol = sample['headers'].index('达人星图id')
    sample_ids = [str(r[scol]) for r in sample['rows']]
    assert set(sample_ids) <= set(order)
    return order, sample_ids


def mappings(root, cache_root, extras):
    out, conflicts = {}, []
    dirs = ['agency_latest', 'p0_latest', 'p0_mapping', 'industry_latest']
    paths = [p for d in dirs for p in sorted((cache_root / d).glob('mapping-*.json'))]
    paths += [Path(p).resolve() for p in extras]
    for path in paths:
        payload = load(path)
        rows = payload.get('rows', []) if isinstance(payload, dict) else payload
        if not isinstance(rows, list):
            continue
        for row in rows:
            if not isinstance(row, dict) or 'star_author_id' not in row:
                continue
            sid = str(row['star_author_id'])
            unique = str(row.get('aweme_unique_id') or row.get('unique_id') or '').strip()
            short = str(row.get('aweme_short_id') or row.get('short_id') or '').strip()
            if unique == '0':
                unique = ''
            if short == '0':
                short = ''
            rec = {'uniqueId': unique, 'shortId': short, 'source': str(path),
                   'partition': next(iter(re.findall(r'20\d{2}-\d{2}-\d{2}', path.name)), '')}
            prev = out.get(sid)
            if prev and prev['uniqueId'] and unique and prev['uniqueId'].casefold() != unique.casefold():
                conflicts.append(sid)
                # 不静默覆盖不同身份句柄，冻结此ID，待人工核验。
                out[sid] = {**prev, 'conflict': True}
                continue
            if prev and prev.get('conflict'):
                continue
            if not prev or unique or not prev['uniqueId']:
                out[sid] = rec
    return out, sorted(set(conflicts))


def baseline(root, order, mapping):
    targets = set(order)
    avatars = set()
    for name in ['p0AvatarSprites.ts', 'industryAvatarSprites.ts', 'agencyAvatarSprites.ts']:
        avatars.update(re.findall(r"'([0-9]{16,19})':\s*\{", (root / 'src/data' / name).read_text()))
    profiles, evidence, conflicts = {}, {}, []
    for name in ['agencyProfileUrls.json', 'industryTalentProfiles.json']:
        for sid, value in load(root / 'src/data' / name)['profiles'].items():
            if sid not in targets:
                continue
            sec = sec_of(value)
            if not sec:
                continue
            url = 'https://www.douyin.com/user/' + sec
            if sid in profiles and profiles[sid]['profileUrl'] != url:
                conflicts.append(sid)
                continue
            display = value.get('displayId', '') if isinstance(value, dict) else ''
            m = mapping.get(sid, {})
            profiles[sid] = {'profileUrl': url, 'displayId': display or m.get('uniqueId') or m.get('shortId') or ''}
            evidence[sid] = {'basis': 'existing verified sec_uid source', 'source': name}
    p0 = load(root / 'src/data/p0ProfileUrls.json')['profiles']
    p0sec = {sid: v for sid, v in p0.items() if sid in targets and isinstance(v, str) and SEC.fullmatch(v)}
    all_profiles = set(profiles) | set(p0sec)
    # 只交付P0未收录的教育资料，避免重复携带1500多条已可用主页。
    for sid in list(profiles):
        if sid in p0sec:
            del profiles[sid]
            evidence.pop(sid, None)
    return avatars & targets, profiles, evidence, p0sec, all_profiles, conflicts


def fetch(sid, m, cache, stop, breaker, lock):
    dst = cache / (sid + '.json')
    if dst.exists():
        return load(dst)
    status = {'id': sid, 'status': 'missing_unique_id', 'attempts': 0,
              'mapping': m, 'verifiedAt': datetime.now(timezone.utc).isoformat()}
    unique = m.get('uniqueId', '')
    if m.get('conflict'):
        status['status'] = 'mapping_conflict'
    elif unique:
        if stop.is_set():
            return {**status, 'status': 'source_stopped'}
        for attempt in range(2):
            if stop.is_set():
                return {**status, 'status': 'source_stopped'}
            status['attempts'] += 1
            try:
                res = requests.get(API, params={'unique_id': unique}, headers=HEADERS, timeout=(4, 8))
                res.raise_for_status()
                data = res.json()
                if data.get('status_code') != 0:
                    status['status'] = 'profile_status_' + str(data.get('status_code'))
                    if attempt == 0:
                        time.sleep(.3)
                        continue
                    break
                user = data.get('user_info') or {}
                returned = str(user.get('unique_id') or '')
                if returned.casefold() != unique.casefold():
                    status['status'] = 'identity_mismatch'
                    break
                sec = str(user.get('sec_uid') or '')
                record = {'uniqueId': returned, 'displayId': returned,
                          'secUid': sec if SEC.fullmatch(sec) else '',
                          'profileUrl': 'https://www.douyin.com/user/' + sec if SEC.fullmatch(sec) else None}
                status.update(record=record, identityVerified=True, api=API,
                              status='profile_ok_no_avatar', avatarSaved=False)
                urls = (user.get('avatar_medium') or user.get('avatar_thumb') or {}).get('url_list', [])
                if urls:
                    image = requests.get(urls[0], headers=HEADERS, timeout=(4, 8))
                    image.raise_for_status()
                    with Image.open(BytesIO(image.content)) as im:
                        assert min(im.size) > 1
                        im.convert('RGB').save(cache / (sid + '.jpg'), quality=85)
                    status.update(status='ok', avatarSaved=True)
                with lock:
                    breaker['consecutive'] = 0
                break
            except requests.Timeout:
                status['status'] = 'timeout'
            except requests.HTTPError as exc:
                status['status'] = 'http_' + str(exc.response.status_code)
            except (ValueError, OSError):
                status['status'] = 'non_json_or_invalid_image'
            except requests.RequestException as exc:
                status['status'] = type(exc).__name__
            # 仅阻断来源级故障；status5是账号级失败，不导致全来源停止。
            with lock:
                breaker['consecutive'] += 1
                if breaker['consecutive'] >= 6:
                    stop.set()
            time.sleep(.3)
    save(dst, status)
    return status


def generate(root, mirror, order, sample, mapping, cache, base):
    avatars, profiles, evidence, p0sec, base_profiles, source_conflicts = base
    extra_images, fresh_profiles, new_avatar_ids, conflicts = {}, set(), set(), list(source_conflicts)
    for sid in order:
        path = cache / (sid + '.json')
        if not path.exists():
            continue
        status = load(path)
        if not status.get('identityVerified'):
            continue
        rec = status.get('record', {})
        sec = rec.get('secUid')
        current = profiles.get(sid, {}).get('profileUrl') or ('https://www.douyin.com/user/' + p0sec[sid] if sid in p0sec else None)
        if sec and SEC.fullmatch(sec):
            url = 'https://www.douyin.com/user/' + sec
            if current and current != url:
                conflicts.append(sid)
                continue
            profiles[sid] = {'profileUrl': url, 'displayId': rec.get('displayId') or ''}
            evidence[sid] = {'basis': 'API status_code=0 and returned unique_id matches dataset mapping',
                             'source': API, 'partition': status['mapping'].get('partition'),
                             'verifiedAt': status['verifiedAt']}
            fresh_profiles.add(sid)
        elif sid not in profiles:
            profiles[sid] = {'profileUrl': None, 'displayId': rec.get('displayId') or ''}
        image = cache / (sid + '.jpg')
        if status.get('avatarSaved') and image.exists() and sid not in avatars:
            extra_images[sid] = image
            new_avatar_ids.add(sid)
    imports, entries, shards = [], [], []
    selected = [(sid, extra_images[sid]) for sid in order if sid in extra_images]
    for shard, start in enumerate(range(0, len(selected), 512)):
        chunk = selected[start:start + 512]
        cols, tile, display = 16, 72, 56
        rows = math.ceil(len(chunk) / cols)
        sprite = Image.new('RGB', (cols * tile, rows * tile), '#102744')
        name = f'education-avatars-{shard:02d}.jpg'
        rel = 'src/assets/' + name
        dst = root / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        imports.append(f"import sprite{shard} from '../assets/{name}';")
        for index, (sid, path) in enumerate(chunk):
            with Image.open(path) as im:
                sprite.paste(ImageOps.fit(im.convert('RGB'), (tile, tile), method=Image.Resampling.LANCZOS),
                             ((index % cols) * tile, (index // cols) * tile))
            entries.append(f"  '{sid}': {{ avatarUrl: sprite{shard}, avatarPosition: '-{index % cols * display}px -{index // cols * display}px', spriteSize: [{cols * display}, {rows * display}] }},")
        sprite.save(dst, 'JPEG', quality=78, optimize=True, progressive=True)
        shards.append({'file': rel, 'count': len(chunk), 'bytes': dst.stat().st_size})
    ts = '\n'.join(imports) + '\n\nexport type EducationAvatarSprite = { avatarUrl: string; avatarPosition: string; spriteSize: [number, number] };\nexport const educationAvatarSprites: Record<string, EducationAvatarSprite> = {\n' + '\n'.join(entries) + '\n};\n'
    (root / 'src/data/educationAvatarSprites.ts').write_text(ts)
    final_avatars = avatars | set(extra_images)
    final_profiles = base_profiles | {sid for sid, p in profiles.items() if p['profileUrl']}
    stats = {'total': len(order), 'baselineAvatar': len(avatars), 'avatarCovered': len(final_avatars),
             'newAvatars': len(new_avatar_ids), 'avatarUnresolved': len(order) - len(final_avatars),
             'baselineP0SecUid': len(p0sec), 'baselineUnionSecUid': len(base_profiles),
             'profileCovered': len(final_profiles), 'newProfiles': len(final_profiles - base_profiles),
             'profileUnresolved': len(order) - len(final_profiles), 'supplementProfiles': len(profiles),
             'supplementAvatars': len(extra_images), 'apiVerifiedProfiles': len(fresh_profiles),
             'sampleTotal': len(sample), 'sampleBaselineAvatar': len(set(sample) & avatars),
             'sampleAvatar': len(set(sample) & final_avatars),
             'sampleBaselineProfile': len(set(sample) & base_profiles),
             'sampleProfile': len(set(sample) & final_profiles),
             'first99BaselineAvatar': len(set(sample[:99]) & avatars),
             'first99Avatar': len(set(sample[:99]) & final_avatars),
             'first99BaselineProfile': len(set(sample[:99]) & base_profiles),
             'first99Profile': len(set(sample[:99]) & final_profiles),
             'legacy16DigitIds': [sid for sid in order if len(sid) == 16], 'shards': shards}
    meta = {**stats, 'generatedAt': datetime.now(timezone.utc).isoformat(),
            'note': '教育2000行按精确星图ID取并集（1998条19位、2条历史16位，均保持字符串）；只接受既有核验sec_uid或API unique_id身份核验后真实sec_uid。短ID与昵称不作为主页依据。原有映射不修改；冲突冻结。',
            'sources': ['agencyProfileUrls.json', 'industryTalentProfiles.json', API],
            'basisCounts': dict(Counter(v['basis'] for v in evidence.values()))}
    save(root / 'src/data/educationTalentProfiles.json', {'meta': meta, 'profiles': dict(sorted(profiles.items()))})
    audit = {**stats, 'evidence': evidence, 'conflicts': sorted(set(conflicts)),
             'unresolvedAvatarIds': [sid for sid in order if sid not in final_avatars],
             'unresolvedProfileIds': [sid for sid in order if sid not in final_profiles],
             'sampleUnresolvedAvatarIds': [sid for sid in sample if sid not in final_avatars],
             'sampleUnresolvedProfileIds': [sid for sid in sample if sid not in final_profiles]}
    save(root / 'src/data/educationAvatarAudit.json', audit)
    files = ['scripts/collect_education_profiles.py', 'src/data/educationTalentProfiles.json',
             'src/data/educationAvatarSprites.ts', 'src/data/educationAvatarAudit.json'] + [s['file'] for s in shards]
    if mirror:
        for rel in files:
            target = mirror / rel
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(root / rel, target)
    print(json.dumps(stats, ensure_ascii=False), flush=True)
    return files


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--mode', choices=['inventory', 'fetch', 'generate', 'verify'], required=True)
    parser.add_argument('--root', type=Path, default=ROOT)
    parser.add_argument('--cache-root', type=Path, default=ROOT.parent / '.cache/avatars')
    parser.add_argument('--workers', type=int, choices=[2, 3], default=3)
    parser.add_argument('--max-seconds', type=float, default=300, help='批次间整体限时；在途请求仍受4/8秒连接/读取超时约束')
    parser.add_argument('--mapping-file', action='append', default=[])
    parser.add_argument('--mirror', type=Path)
    args = parser.parse_args()
    root = args.root.resolve()
    mirror = args.mirror.resolve() if args.mirror else None
    order, sample = read_targets(root)
    mapping, mapping_conflicts = mappings(root, args.cache_root, args.mapping_file)
    base = baseline(root, order, mapping)
    cache = args.cache_root / 'education_latest'
    cache.mkdir(parents=True, exist_ok=True)
    gap = [sid for sid in order if sid not in base[0] or sid not in base[4]]
    print(json.dumps({'mode': args.mode, 'total': len(order), 'sample': len(sample),
                      'baselineAvatar': len(base[0]), 'baselineProfiles': len(base[4]),
                      'gap': len(gap), 'uniqueFetchable': sum(bool(mapping.get(s, {}).get('uniqueId')) for s in gap),
                      'missingMapping': sum(s not in mapping for s in gap),
                      'sampleGap': [s for s in sample if s in gap],
                      'mappingConflictsInGap': sorted(set(gap) & set(mapping_conflicts))}, ensure_ascii=False), flush=True)
    save(cache / 'missing-mapping.json', [s for s in gap if s not in mapping])
    if args.mode == 'fetch':
        counts, stop, breaker, lock = Counter(), threading.Event(), {'consecutive': 0}, threading.Lock()
        # 先sample；pool.map虽保序，但网络实际并发，禁止一次排队所有目标。
        todo = list(dict.fromkeys([s for s in sample if s in gap] + gap))
        started = time.monotonic()
        with cf.ThreadPoolExecutor(max_workers=args.workers) as pool:
            for start in range(0, len(todo), args.workers):
                if time.monotonic() - started >= args.max_seconds:
                    counts['timebox_unattempted'] += len(todo) - start
                    break
                if stop.is_set():
                    counts['source_stopped'] += len(todo) - start
                    break
                futures = [pool.submit(fetch, s, mapping.get(s, {}), cache, stop, breaker, lock)
                           for s in todo[start:start + args.workers]]
                for future in futures:
                    status = future.result()
                    counts[status['status']] += 1
                if start % 30 == 0:
                    print(json.dumps({'processed': min(start + args.workers, len(todo)), 'counts': dict(counts)}), flush=True)
        save(cache / 'fetch-summary.json', {'counts': dict(counts), 'sourceStopped': stop.is_set()})
        print(json.dumps({'counts': dict(counts), 'sourceStopped': stop.is_set()}), flush=True)
    elif args.mode == 'generate':
        generate(root, mirror, order, sample, mapping, cache, base)
    elif args.mode == 'verify':
        payload = load(root / 'src/data/educationTalentProfiles.json')
        assert set(payload['profiles']) <= set(order)
        for sid, rec in payload['profiles'].items():
            assert SID.fullmatch(sid) and set(rec) == {'profileUrl', 'displayId'}
            assert isinstance(rec['displayId'], str)
            assert rec['profileUrl'] is None or sec_of(rec)
        ts = (root / 'src/data/educationAvatarSprites.ts').read_text()
        ids = re.findall(r"'([0-9]{16,19})':", ts)
        assert len(ids) == len(set(ids)) and set(ids) <= set(order)
        for url in re.findall(r"from '([^']+)'", ts):
            with Image.open(root / 'src/data' / url) as im:
                im.verify()
        audit = load(root / 'src/data/educationAvatarAudit.json')
        assert len(ids) == audit['supplementAvatars']
        assert audit['avatarCovered'] + len(audit['unresolvedAvatarIds']) == len(order)
        files = ['scripts/collect_education_profiles.py', 'src/data/educationTalentProfiles.json',
                 'src/data/educationAvatarSprites.ts', 'src/data/educationAvatarAudit.json'] + [s['file'] for s in audit['shards']]
        if mirror:
            mirror_data = load(mirror / 'download-assets/industry-education.data')
            col = mirror_data['headers'].index('达人星图id')
            assert list(dict.fromkeys(str(r[col]) for r in mirror_data['rows'])) == order
            for rel in files:
                assert hashlib.sha256((root / rel).read_bytes()).digest() == hashlib.sha256((mirror / rel).read_bytes()).digest(), rel
        print(json.dumps({'verified': True, 'mirrorIdentical': bool(mirror), 'files': files}), flush=True)


if __name__ == '__main__':
    main()
