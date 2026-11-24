#!/usr/bin/env python3
"""Apply public release policies to mirrored Pages output without private packages."""
import argparse
import hashlib
import json
import os
import re
import unicodedata
import urllib.request
from pathlib import Path

SOURCE = 'https://raw.githubusercontent.com/shiyuecheng34-hue/talent-supply-hub-public/main/src/data/'
INDUSTRY = ['行业大类', '推荐优先级', '是否补充推荐', '星图作者一级分类(T-3标签)', '星图作者二级分类(T-3标签)']
NODE = ['行业大类', '节点行业内排名', '推荐优先级', '是否重点推荐(行业千人池)', '星图作者一级分类(T-3标签)', '星图作者二级分类(T-3标签)', '节点推荐分', '入池逻辑', '是否补充入池', '行业自然命中', '商业行业命中', '内容标签命中', '画像Bench命中', '行业画像Bench', '最高视频报价(元)', '节点规则摘要']
MEDICAL_ID = '7575570461527015462'
MEDICAL_URL = 'https://p26.douyinpic.com/aweme/100x100/aweme-avatar/tos-cn-i-0813c001_oAvATvpFog7eBmAIAB7iAfCCPAgiE8rQ0c9GAA.jpeg?from=2956013662'
HD_AVATARS = {
    '6693777798747652109': {
        'secUid': 'MS4wLjABAAAAoKTnbntM_idIrpxp9AZE8n7t1K62vpANF0FENd0Tlbo',
        'url': 'https://p3.douyinpic.com/aweme/1080x1080/aweme-avatar/tos-cn-avt-0015_3fc594550bb958bf6e60cc61ef900111.jpeg?from=2956013662',
    },
    '6912341826695331854': {
        'secUid': 'MS4wLjABAAAArv9Tnk07YY0ZG1ZiF30PclmCfnPM3hBeluIJiIhfU2A',
        'url': 'https://p3.douyinpic.com/aweme/1080x1080/aweme-avatar/tos-cn-i-0813_ocB5EAY1g8mWEAAZVAAQdDAgiravBWIvDiuIP.jpeg?from=2956013662',
    },
    '6870163473385390093': {
        'secUid': 'MS4wLjABAAAAhAIMHZRI61dC4eivwuT99LAKz3VCH2P7u0RsvOQin7w',
        'url': 'https://p26.douyinpic.com/aweme/1080x1080/aweme-avatar/tos-cn-avt-0015_9af5133c68b9d3d4f4d9e9999ce83ace.jpeg?from=2956013662',
    },
}


HD_AVATAR_HASH_PREFIXES = {
    '6693777798747652109': '8abe1a673d97',
    '6912341826695331854': '5423a8fc5104',
    '6870163473385390093': '725169213832',
}


def read_cached_avatar(dist, star_id):
    hash_prefix = HD_AVATAR_HASH_PREFIXES[star_id]
    path = dist / 'avatars' / f'douyin-hd-{star_id}-{hash_prefix}.jpg'
    return path.read_bytes() if path.exists() else None


def read_source_asset(source_dir, filename):
    if source_dir:
        path = source_dir.parent / 'assets' / filename
        if path.exists():
            return path.read_bytes()
    return None


def cache_hd_avatars(dist, source_dir=None):
    result = {}
    for star_id, verified in HD_AVATARS.items():
        url = verified['url']
        data = None
        try:
            data = read_source_asset(source_dir, f'douyin-hd-{star_id}.jpg')
            if data is None:
                data = read_cached_avatar(dist, star_id)
            if data is None:
                endpoint = 'https://www.iesdouyin.com/web/api/v2/user/info/?sec_uid=' + verified['secUid']
                user = json.loads(get(endpoint)).get('user_info', {})
                if user.get('sec_uid') == verified['secUid']:
                    urls = user.get('avatar_medium', {}).get('url_list', [])
                    if urls and re.match(r'https://[^/]+\.douyinpic\.com/', urls[0]):
                        url = urls[0].replace('/aweme/100x100/', '/aweme/1080x1080/')
        except (OSError, ValueError):
            pass  # Use the previously identity-verified CDN asset, never a guessed person.
        try:
            if data is None:
                data = get(url)
            assert data.startswith(b'\xff\xd8'), 'HD avatar must be a JPEG'
            filename = f'douyin-hd-{star_id}-{hashlib.sha256(data).hexdigest()[:12]}.jpg'
            (dist / 'avatars' / filename).write_bytes(data)
            result[star_id] = {'avatarUrl': './avatars/' + filename,
                               'avatarPosition': '0px 0px', 'spriteSize': [54, 54]}
        except (OSError, ValueError, AssertionError) as error:
            print(json.dumps({'avatarWarning': star_id, 'reason': str(error)}))
    return result


def norm(value):
    return re.sub(r'\s+', '', unicodedata.normalize('NFKC', str(value or ''))).lower()


def get(url):
    request = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0', 'Referer': 'https://www.iesdouyin.com/'})
    with urllib.request.urlopen(request, timeout=45) as response:
        return response.read()


def read_source_file(filename, source_dir):
    if source_dir:
        return (source_dir / filename).read_text()
    return get(SOURCE + filename).decode()


def load_node_sales_owner_policy(source_dir):
    try:
        policy = json.loads(read_source_file('nodeSalesOwnerRewrites.json', source_dir))
        assert policy['column'] and policy['replaceWith'] and policy['names']
        return policy
    except (OSError, ValueError, KeyError, AssertionError) as error:
        print(json.dumps({'ownerRewriteWarning': str(error)}))
        return None


def rewrite_node_sales_owners(data, policy):
    if not policy:
        return
    headers = data['headers']
    if policy['column'] not in headers:
        return
    index = headers.index(policy['column'])
    names = set(policy['names'])
    for row in data['rows']:
        if index < len(row) and str(row[index] or '').strip() in names:
            row[index] = policy['replaceWith']


def write_profile_link_bootstrap(dist, source_dir):
    profiles = json.loads(read_source_file('p0ProfileUrls.json', source_dir))['profiles']
    snapshot_ids = set()
    for path in (dist / 'downloads').glob('*.data'):
        data = json.loads(path.read_text())
        index = data['headers'].index('达人星图id')
        snapshot_ids.update(str(row[index]).strip().removesuffix('.0') for row in data['rows'])
    scoped = {star_id: sec_uid for star_id, sec_uid in profiles.items() if star_id in snapshot_ids}
    payload = 'window.__p0ProfileSecIds=' + json.dumps(scoped, separators=(',', ':')) + ';\n'
    (dist / 'profile-links.js').write_text(payload)
    (dist / 'profile-links.json').write_text(json.dumps(scoped, separators=(',', ':')))
    return len(scoped)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--dist', type=Path, default=Path('.'))
    parser.add_argument('--source-dir', type=Path)
    parser.add_argument('--basename', default='/' + os.environ.get('GITHUB_REPOSITORY', 'jingxuandaren/talent-supply-hub-v2').split('/')[-1])
    args = parser.parse_args()
    dist = args.dist
    ids = set()
    counts = {}
    owner_policy = load_node_sales_owner_policy(args.source_dir)
    assert owner_policy, 'Node sales owner rewrite policy is required'
    for path in (dist / 'downloads').glob('*.data'):
        if not path.stem.startswith(('industry-', 'node-')): continue
        data = json.loads(path.read_text())
        headers, rows = data['headers'], data['rows']
        assert rows and isinstance(rows, list), f'Empty snapshot: {path}'
        if path.stem.startswith('node-'):
            rewrite_node_sales_owners(data, owner_policy)
            assert len(rows) > 100, f'Truncated node snapshot: {path}'
            index = headers.index('达人星图id')
            ids.update(str(row[index]).strip().removesuffix('.0') for row in rows)
        blocked = set(map(norm, NODE if path.stem.startswith('node-') else INDUSTRY))
        indices = [i for i, value in enumerate(headers) if norm(value) not in blocked]
        data['headers'] = [headers[i] for i in indices]
        data['rows'] = [[row[i] if i < len(row) else None for i in indices] for row in rows]
        assert len(data['rows']) == len(rows)
        assert not blocked.intersection(map(norm, data['headers']))
        path.write_text(json.dumps(data, ensure_ascii=False, separators=(',', ':')))
        counts[path.stem] = len(rows)
    assert len([name for name in counts if name.startswith('node-')]) == 4
    sprites = {}
    for filename in ['agencyAvatarSprites.ts', 'p0AvatarSprites.ts', 'industryAvatarSprites.ts']:
        text = read_source_file(filename, args.source_dir)
        imports = dict(re.findall(r"import (sprite\d+) from '../assets/([^']+)';", text))
        for sid, symbol, position, width, height in re.findall(r"'(\d+)': \{ avatarUrl: (sprite\d+), avatarPosition: '([^']+)', spriteSize: \[(\d+), (\d+)\] \}", text):
            if sid not in ids: continue
            matches = list((dist / 'static/image').glob(Path(imports[symbol]).stem + '.*.jpg'))
            assert len(matches) == 1, f'Unavailable sprite: {filename} {symbol}'
            sprites[sid] = {'avatarUrl': './' + matches[0].relative_to(dist).as_posix(), 'avatarPosition': position, 'spriteSize': [int(width), int(height)]}
    medical = dist / 'avatars/node-medical.jpg'
    medical.parent.mkdir(exist_ok=True)
    medical_data = read_source_asset(args.source_dir, 'node-medical.jpg')
    if medical_data:
        medical.write_bytes(medical_data)
    elif not medical.exists():
        medical.write_bytes(get(MEDICAL_URL))
    assert medical.read_bytes()[:2] == b'\xff\xd8'
    profile_link_count = write_profile_link_bootstrap(dist, args.source_dir)
    # A single-image background uses the same content rendering path as sprites.
    sprites[MEDICAL_ID] = {'avatarUrl': './avatars/node-medical.jpg', 'avatarPosition': '0px 0px', 'spriteSize': [56, 56]}
    page_files = [p for p in (dist / 'static/js/async').glob('page.*.js')]
    assert len(page_files) == 1, 'Ambiguous page bundle'
    page = page_files[0]
    text = page.read_text()
    marker = '"6596677925234278408":{avatarUrl:'
    assert text.count(marker) == 1, 'Industry sprite map changed; update patch adapter'
    payload = json.dumps(sprites, ensure_ascii=False, separators=(',', ':'))[1:-1]
    # Earlier properties are overridden by the unchanged industry map, preserving
    # exactly the existing internal avatar for every already-covered author.
    text = text.replace(marker, payload + ',' + marker, 1)
    hd_avatars = cache_hd_avatars(dist, args.source_dir)
    for star_id, sprite in hd_avatars.items():
        # Replace the original industry entry, after the supplemental map, so the
        # verified full image takes precedence over both low-resolution atlases.
        pattern = r'("' + star_id + r'":)\{avatarUrl:[^}]+\}'
        text, replaced = re.subn(pattern, lambda match: match[1] + json.dumps(sprite, separators=(',', ':')), text, count=1)
        assert replaced == 1, f'HD avatar industry adapter changed for {star_id}'
    csv_anchor = 'arguments[3]:"\\u8FBE\\u4EBA\\u661F\\u56FEid",'
    assert text.count(csv_anchor) == 1, 'CSV export adapter changed'
    csv_anchor_position = text.index(csv_anchor)
    module_matches = [
        match
        for match in re.finditer(r'(?:^|[,{])(\d+)\(\w+,\w+,\w+\)\{', text)
        if match.start() < csv_anchor_position
    ]
    assert module_matches, 'Application module adapter changed'
    app = module_matches[-1]
    csv_start = text.rfind('function ', app.end(), csv_anchor_position)
    assert csv_start > app.end(), 'CSV function is outside application module'
    fn = re.match(r'function (\w+)\((\w+),(\w+),(\w+)\)\{let [\w,]+?(\w+)=arguments.length>3', text[csv_start:])
    assert fn, 'CSV export function not found'
    _, label, headers, rows, _default_export_label = fn.groups()
    prefix = f'function {fn[1]}({label},{headers},{rows})' + '{'
    policy = json.dumps({'industry': INDUSTRY, 'node': NODE}, ensure_ascii=False, separators=(',', ':'))
    injection = f'const __p={policy},__n=v=>String(v??" ").normalize("NFKC").replace(/\\s+/g,"").toLowerCase(),__b=new Set(({label}.startsWith("节点")?__p.node:{label}.startsWith("行业")?__p.industry:[]).map(__n)),__k={headers}.map((v,i)=>__b.has(__n(v))?-1:i).filter(i=>i>=0);{rows}={rows}.map(r=>__k.map(i=>r[i]));{headers}=__k.map(i=>{headers}[i]);'
    avatar_ids = json.dumps(list(sprites), separators=(',', ':'))
    text = text[:csv_start] + prefix + injection + text[csv_start + len(prefix):]
    node_export_pattern = r'let (\w+)=(\w+)\.trim\(\)\.toLowerCase\(\),(\w+)=!(\w+)&&\1\?(\w+)\.rows\.filter\('
    assert len(re.findall(node_export_pattern, text)) == 1, 'Node full-export adapter changed'
    avatar_sort_pattern = re.compile(
        r'return!!\(([\w.]+)\[(\w+)\]\|\|([\w.]+)\[\2\]\)\};return Number\(!(\w+)\((\w+)\)\)-Number\(!\4\(\2\)\)'
    )
    avatar_sort_matches = list(avatar_sort_pattern.finditer(text))
    assert len(avatar_sort_matches) == 1, 'Node preview ordering adapter changed'
    avatar_sort_match = avatar_sort_matches[0]
    avatar_modules = list(re.finditer(r'(?:^|[,{])(\d+)\(\w+,\w+,\w+\)\{', text[:avatar_sort_match.start()]))
    assert avatar_modules, 'Avatar module adapter changed'
    avatar_module = avatar_modules[-1]
    # Keep the avatar set in the module that consumes it, not the shared CSV chunk.
    text = text[:avatar_module.end()] + 'const __nodeAvatarIds=new Set(' + avatar_ids + ');' + text[avatar_module.end():]
    text = avatar_sort_pattern.sub(
        lambda match: (
            f'return!!({match[1]}[{match[2]}]||{match[3]}[{match[2]}]||__nodeAvatarIds.has({match[2]}))}};'
            f'return Number(!{match[4]}({match[5]}))-Number(!{match[4]}({match[2]}))'
        ),
        text,
        count=1,
    )
    profile_pattern = re.compile(
        r'(\w+)=(\w+)\[(\w+)\],(\w+)='
        r'\(null==(\w+)\?void 0:\5\.profileUrl\)\?\?'
        r'\((\w+)\?`https://www\.douyin\.com/user/\$\{\6\}`:null\)'
    )
    profile_matches = list(profile_pattern.finditer(text))
    assert len(profile_matches) == 1, 'Douyin profile link adapter changed'
    text = profile_pattern.sub(
        lambda match: (
            f'{match[1]}={match[2]}[{match[3]}]??window.__p0ProfileSecIds?.[{match[3]}],'
            f'{match[4]}=(null=={match[5]}?void 0:{match[5]}.profileUrl)??'
            f'({match[1]}?`https://www.douyin.com/user/${{{match[1]}}}`:null)'
        ),
        text,
        count=1,
    )
    text = re.sub(r'fetch\(`\./downloads/\$\{(\w+)\}\.data`\)', r'fetch(`./downloads/${\1}.data?release=policy-20261123`)', text)
    page.write_text(text)
    old_hash = page.name.split('.')[-2]
    new_hash = hashlib.sha256(text.encode()).hexdigest()[:10]
    assert old_hash != new_hash
    new_page = page.with_name(page.name.replace(old_hash, new_hash))
    page.rename(new_page)
    for path in dist.rglob('*'):
        if path.suffix not in {'.js', '.html', '.json'} or not path.is_file(): continue
        content = path.read_text()
        if old_hash in content: path.write_text(content.replace(old_hash, new_hash))
    # Keep the proven repository-path routing fix, discovering files by content
    # rather than pinning a build-specific chunk filename.
    basename_patches = 0
    for path in (dist / 'static/js').glob('*.js'):
        content = path.read_text()
        anchor = '{serverBase:["/"]},(J||{}).router'
        replacement = '{serverBase:["/"],basename:' + json.dumps(args.basename) + '},(J||{}).router'
        if anchor in content:
            content = content.replace(anchor, replacement, 1)
            path.write_text(content)
            basename_patches += 1
        elif replacement in content: basename_patches += 1
    assert basename_patches == 1, 'Router config adapter changed'
    release = hashlib.sha256((text + args.basename).encode()).hexdigest()[:12]
    for name in ['index.html', '404.html']:
        path = dist / name
        if path.exists():
            html = re.sub(r'(src="[^"?]+\.js)(?:\?[^" ]*)?"', lambda m: m[1] + '?release=' + release + '"', path.read_text())
            # Remove the superseded DOM supplement, if an older release used it.
            html = re.sub(r'<script[^>]*src="\./node-avatar-fix[^\"]*"[^>]*></script>', '', html)
            # Profile links load on demand in LiveTalentModule, never block the home page.
            html = re.sub(r'<script[^>]*src="(?:\./)?profile-links[^\"]*"[^>]*></script>', '', html)
            path.write_text(html)
    print(json.dumps({'rows': counts, 'nodeAvatarIds': len(sprites), 'hdAvatars': len(hd_avatars), 'profileLinks': profile_link_count, 'page': new_page.name, 'release': release}, ensure_ascii=False))


if __name__ == '__main__':
    main()
