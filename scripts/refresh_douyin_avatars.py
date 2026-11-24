#!/usr/bin/env python3
"""Resolve verified Douyin profile links to locally cached, larger avatars."""
import argparse
import hashlib
import json
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

# Select explicit IDs from the project's verified profile mapping.


def fetch(url):
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, timeout=15) as response:
        return response.read()


def jpeg_dimensions(data):
    position = 2
    while position + 9 < len(data):
        if data[position] != 255:
            raise ValueError('Invalid JPEG marker')
        marker = data[position + 1]
        position += 2
        if marker in (0xD8, 0xD9, 0x01):
            continue
        length = int.from_bytes(data[position:position + 2], 'big')
        if length < 2:
            raise ValueError('Invalid JPEG segment')
        if marker in (0xC0, 0xC1, 0xC2, 0xC3, 0xC5, 0xC6, 0xC7, 0xC9, 0xCA, 0xCB, 0xCD, 0xCE, 0xCF):
            return int.from_bytes(data[position + 5:position + 7], 'big'), int.from_bytes(data[position + 3:position + 5], 'big')
        position += length
    raise ValueError('JPEG dimensions were unavailable')


def resolve(profile_url):
    parsed = urllib.parse.urlparse(profile_url)
    if parsed.hostname != 'www.douyin.com' or not parsed.path.startswith('/user/'):
        raise ValueError('A verified Douyin /user/<sec_uid> profile is required')
    sec_uid = parsed.path.split('/user/', 1)[1].strip('/')
    api = 'https://www.iesdouyin.com/web/api/v2/user/info/?' + urllib.parse.urlencode({'sec_uid': sec_uid})
    result = json.loads(fetch(api))
    user = result.get('user_info', {})
    if result.get('status_code') != 0 or user.get('sec_uid') != sec_uid:
        raise ValueError('Profile identity verification failed')
    urls = []
    for field in ('avatar_larger', 'avatar_medium', 'avatar_thumb'):
        for url in user.get(field, {}).get('url_list', []):
            if (urllib.parse.urlparse(url).hostname or '').endswith('.douyinpic.com'):
                if '/aweme/100x100/' in url:
                    urls.append(url.replace('/aweme/100x100/', '/aweme/1080x1080/'))
                urls.append(url)
    for url in dict.fromkeys(urls):
        try:
            data = fetch(url)
            if not data.startswith(b'\xff\xd8'):
                continue
            width, height = jpeg_dimensions(data)
            return data, {
                'width': width,
                'height': height,
                'largerThanThumbnail': min(width, height) >= 256,
                'profileUrl': profile_url,
                'secUid': sec_uid,
                'nickname': user.get('nickname'),
                'sourceUrl': url,
                'sourceType': 'CDN-size-variant' if '/1080x1080/' in url else 'API-avatar',
                'sha256': hashlib.sha256(data).hexdigest(),
                'verifiedAt': datetime.now(timezone.utc).isoformat(),
            }
        except (OSError, ValueError):
            continue
    raise ValueError('No usable verified avatar was available')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--profiles', default='src/data/industryTalentProfiles.json')
    parser.add_argument('--ids', nargs='+', required=True)
    parser.add_argument('--output', default='src/assets')
    parser.add_argument('--manifest', default='src/data/douyinHdAvatars.json')
    args = parser.parse_args()
    profiles = json.loads(Path(args.profiles).read_text())
    entries = next(value for key, value in profiles.items() if key != 'meta' and isinstance(value, dict))
    output = Path(args.output)
    output.mkdir(parents=True, exist_ok=True)
    manifest_path = Path(args.manifest)
    manifest = json.loads(manifest_path.read_text()) if manifest_path.exists() else {}
    for star_id in args.ids:
        data, record = resolve(entries[star_id]['profileUrl'])
        filename = f'douyin-hd-{star_id}.jpg'
        (output / filename).write_bytes(data)
        record['file'] = filename
        manifest[star_id] = record
        print(json.dumps({'id': star_id, 'sha256': record['sha256'], 'sourceType': record['sourceType']}))
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n')


if __name__ == '__main__':
    main()
