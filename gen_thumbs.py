#!/usr/bin/env python3
"""为文章 index_img 封面图生成小尺寸缩略图（WebP, 最大宽度 600px）。"""
import re
from pathlib import Path
from PIL import Image

MAX_WIDTH = 600
QUALITY = 80
THUMB_DIR = Path('source/images/thumbs')
INDEX_PAT = re.compile(r'^(index_img:\s*["\']?)(/images/[^"\']+)(["\']?)$', re.MULTILINE)


def make_thumb(src: Path, name: str) -> Path:
    THUMB_DIR.mkdir(parents=True, exist_ok=True)
    dst = THUMB_DIR / f'{name}.webp'
    im = Image.open(src)
    if im.mode in ('RGBA', 'P', 'LA'):
        im = im.convert('RGBA')
        bg = Image.new('RGB', im.size, (255, 255, 255))
        bg.paste(im, mask=im.split()[-1] if im.mode == 'RGBA' else None)
        im = bg
    elif im.mode != 'RGB':
        im = im.convert('RGB')
    if im.width > MAX_WIDTH:
        im = im.resize((MAX_WIDTH, round(im.height * MAX_WIDTH / im.width)), Image.LANCZOS)
    im.save(dst, 'WEBP', quality=QUALITY)
    return dst


def main():
    changed = 0
    total_before = total_after = 0
    for md in sorted(Path('source/_posts').glob('*.md')):
        text = md.read_text(encoding='utf-8')
        m = INDEX_PAT.search(text)
        if not m:
            continue
        url = m.group(2)
        if url.startswith('/images/thumbs/'):
            continue
        src = Path('source') / url.lstrip('/')
        if not src.exists():
            print(f'[跳过] 源文件不存在: {url}')
            continue
        dst = make_thumb(src, src.stem)
        before, after = src.stat().st_size, dst.stat().st_size
        total_before += before
        total_after += after
        new_text = text[:m.start(2)] + f'/images/thumbs/{dst.name}' + text[m.end(2):]
        md.write_text(new_text, encoding='utf-8')
        changed += 1
    print(f'更新 {changed} 篇文章封面 -> 缩略图')
    print(f'总体积: {total_before/1024/1024:.1f} MB -> {total_after/1024:.0f} KB')

    # 默认封面兜底图
    default_src = Path('node_modules/hexo-theme-fluid/source/img/default.png')
    dst = make_thumb(default_src, 'default')
    print(f'默认封面: {default_src.stat().st_size//1024} KB -> {dst.stat().st_size//1024} KB -> /images/thumbs/{dst.name}')


if __name__ == '__main__':
    main()
