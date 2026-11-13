#!/usr/bin/env python3
"""离线规格计划、成图事实核对及公众号同源预览；不评价审美或发布权限。"""
import argparse
import hashlib
import json
from pathlib import Path

PROFILES = {
    'douyin': [('vertical', 1080, 1440), ('horizontal', 1440, 1080)],
    'xiaohongshu': [('cover', 1080, 1440)],
    'xiaohongshu-landscape': [('cover', 1440, 1080)],
    'bilibili': [('recommendation', 1440, 1080), ('space', 1920, 1080)],
    'channels': [('profile', 1080, 1440), ('share', 1440, 1080)],
    'x-article': [('article-header', 2000, 800)],
    'x-post': [('image', 1600, 900)],
    'wechat-article': [('main', 1880, 800), ('square-preview', 800, 800)],
    'wechat-square': [('square', 800, 800)],
    'full-portrait': [('cover', 1080, 1920)],
}


def plan(platforms):
    assets, placements, reusable = [], [], {}
    for platform in dict.fromkeys(platforms):
        for slot, width, height in PROFILES[platform]:
            crop = platform == 'wechat-article' and slot == 'square-preview'
            key = (width, height, 'wechat-crop' if crop else 'generated')
            if key not in reusable:
                asset_id = f'{platform}-{slot}'
                reusable[key] = asset_id
                asset = dict(id=asset_id, path=f'{asset_id}.png', width=width,
                             height=height, kind='crop-preview' if crop else 'generated',
                             visualCheck='pending', sha256=None)
                if crop:
                    asset.update(derivedFrom=reusable[(1880, 800, 'generated')],
                                 cropBox=[40, 0, 840, 800],
                                 cropNormalized=[40 / 1880, 0, 840 / 1880, 1])
                assets.append(asset)
            placements.append(dict(platform=platform, slot=slot, assetId=reusable[key],
                                   nativeCheck='pending', specEvidence='制作预设，待核当期入口'))
    return dict(schemaVersion=1, status='planned', assets=assets, placements=placements)


def verify(manifest, base):
    from PIL import Image, ImageChops
    errors, pending, facts = [], [], []
    assets = {a['id']: a for a in manifest['assets']}
    if len(assets) != len(manifest['assets']):
        errors.append('重复asset id')
    for a in assets.values():
        path = base / a['path']
        if not path.is_file():
            errors.append(f"missing: {a['id']}")
            continue
        try:
            with Image.open(path) as im:
                im.load()
                size = im.size
            if size != (a['width'], a['height']):
                errors.append(f"size: {a['id']} {size}")
            digest = hashlib.sha256(path.read_bytes()).hexdigest()
            if a.get('sha256') and digest != a['sha256']:
                errors.append(f"hash: {a['id']}")
            facts.append(dict(id=a['id'], size=size, sha256=digest))
            if a.get('kind') == 'crop-preview':
                source = assets[a['derivedFrom']]
                with Image.open(base / source['path']) as im:
                    box = a['cropBox']
                    x1, y1, x2, y2 = box
                    if not (0 <= x1 < x2 <= im.width and 0 <= y1 < y2 <= im.height):
                        raise ValueError('裁切框越界')
                    normalized = [x1/im.width, y1/im.height, x2/im.width, y2/im.height]
                    if len(a['cropNormalized']) != 4 or any(abs(x-y) > 1e-6 for x,y in zip(normalized,a['cropNormalized'])):
                        errors.append(f"cropNormalized: {a['id']}")
                    expected = im.convert('RGB').crop(box)
                    with Image.open(path) as actual:
                        actual = actual.convert('RGB')
                        if actual.size != expected.size or ImageChops.difference(actual, expected).getbbox():
                            errors.append(f"crop-source: {a['id']}")
        except (OSError, ValueError, KeyError, TypeError) as exc:
            errors.append(f"invalid: {a['id']}: {exc}")
        if a.get('visualCheck') != 'passed':
            pending.append(a['id'])
    if not assets or not manifest['placements']:
        errors.append('empty assets or placements')
    platforms = {p['platform'] for p in manifest['placements']}
    for platform in platforms:
        if platform in PROFILES:
            actual_slots = {p['slot'] for p in manifest['placements'] if p['platform'] == platform}
            for slot, _, _ in PROFILES[platform]:
                if slot not in actual_slots:
                    errors.append(f'missing slot: {platform}/{slot}')
    for p in manifest['placements']:
        if p['assetId'] not in assets:
            errors.append(f"placement missing asset: {p['assetId']}")
        profile = PROFILES.get(p['platform'])
        if profile is None:
            errors.append(f"unknown platform: {p['platform']}")
            continue
        slots = {slot:(w,h) for slot,w,h in profile}
        if p['slot'] not in slots:
            errors.append(f"unknown slot: {p['slot']}")
        elif p['assetId'] in assets:
            a = assets[p['assetId']]
            if (a['width'], a['height']) != slots[p['slot']]:
                errors.append(f"slot dimensions: {p['platform']}/{p['slot']}")
            if p['platform'] == 'wechat-article' and p['slot'] == 'square-preview' and a.get('kind') != 'crop-preview':
                errors.append('公众号同源方图不能用独立生成图冒充')
    return dict(fileChecksPassed=not errors, errors=errors, visualPending=pending,
                nativePending=[p for p in manifest['placements'] if p.get('nativeCheck') != 'passed'],
                facts=facts, note='文件事实不代表视觉、用户认可或发布验收')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    p = sub.add_parser('plan')
    p.add_argument('--platform', action='append', choices=PROFILES, required=True)
    p.add_argument('--out', type=Path, required=True)
    p = sub.add_parser('verify'); p.add_argument('manifest', type=Path)
    p = sub.add_parser('wechat-preview')
    p.add_argument('--image', type=Path, required=True); p.add_argument('--out', type=Path, required=True)
    p.add_argument('--crop', nargs=4, type=int, required=True)
    args = parser.parse_args()
    if args.command == 'plan':
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(json.dumps(plan(args.platform), ensure_ascii=False, indent=2))
    elif args.command == 'verify':
        result = verify(json.loads(args.manifest.read_text()), args.manifest.parent)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        raise SystemExit(0 if result['fileChecksPassed'] else 1)
    else:
        from PIL import Image
        with Image.open(args.image) as im:
            if im.size != (1880, 800): parser.error('公众号最终主图须为1880×800')
            x1,y1,x2,y2 = args.crop
            if not (0 <= x1 < x2 <= im.width and 0 <= y1 < y2 <= im.height and x2-x1 == y2-y1 == 800):
                parser.error('须为主图内完整800×800框')
            args.out.parent.mkdir(parents=True, exist_ok=True)
            if args.out.exists(): parser.error('保留已有版本，请换输出路径')
            im.crop(args.crop).save(args.out)


if __name__ == '__main__':
    main()
