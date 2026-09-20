#!/usr/bin/env python3
"""批量为 Hexo 文章提取正文首图，写入 front-matter 的 index_img 字段。"""
import re
import sys
from pathlib import Path

POSTS_DIR = Path(sys.argv[1] if len(sys.argv) > 1 else "source/_posts")

# Markdown 图片 ![alt](url)、HTML <img src="url">、引用式定义 [1]: /images/xx.png
IMG_PATTERNS = [
    re.compile(r'!\[[^\]]*\]\(\s*["\']?([^\s"\'()]+)["\']?[^)]*\)'),
    re.compile(r'<img[^>]+src=["\']([^"\']+)["\']', re.IGNORECASE),
    re.compile(r'^\s*\[[^\]]+\]:\s*([^\s]+)\s*$', re.MULTILINE),
]
IMAGE_EXT = re.compile(r'\.(png|jpe?g|gif|webp|bmp|svg)(\?.*)?$', re.IGNORECASE)


def split_front_matter(text: str):
    """返回 (front_matter_lines, body, ending) 或 None（无 front-matter）。"""
    m = re.match(r'^(---\r?\n)(.*?)(\n---[ \t]*\r?\n)(.*)$', text, re.DOTALL)
    if not m:
        return None
    return m.group(2), m.group(4), m.group(3)


def first_image(body: str):
    candidates = []
    for pat in IMG_PATTERNS:
        for m in pat.finditer(body):
            url = m.group(1).strip()
            if IMAGE_EXT.search(url):
                candidates.append((m.start(), url))
    if not candidates:
        return None
    candidates.sort()
    # 优先站内图片，外链图床可能已失效
    local = [c for c in candidates if c[1].startswith('/')]
    return (local or candidates)[0][1]


def main():
    updated, skipped, noimg = 0, 0, 0
    for md in sorted(POSTS_DIR.glob('*.md')):
        text = md.read_text(encoding='utf-8')
        parts = split_front_matter(text)
        if not parts:
            print(f'[跳过] 无 front-matter: {md.name}')
            skipped += 1
            continue
        fm, body, closing = parts
        if re.search(r'^index_img\s*:', fm, re.MULTILINE):
            skipped += 1
            continue
        url = first_image(body)
        if not url:
            noimg += 1
            continue
        url = url.replace('"', '%22')
        new_fm = fm + f'\nindex_img: "{url}"'
        head = text[:text.index(fm)]
        md.write_text(head + new_fm + closing + body, encoding='utf-8')
        updated += 1
        print(f'[更新] {md.name} -> {url}')
    print(f'\n完成: 更新 {updated} 篇, 已有 index_img/跳过 {skipped} 篇, 正文无图 {noimg} 篇')


if __name__ == '__main__':
    main()
