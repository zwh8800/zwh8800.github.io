#!/usr/bin/env python3
"""生成 Caddy 教程缺失的配图：模拟 caddyserver.com 下载页面。"""
from PIL import Image, ImageDraw, ImageFont

W, H = 1200, 675
FONT_HELV = "/System/Library/Fonts/Helvetica.ttc"
FONT_PF = "/System/Library/Fonts/PingFang.ttc"


def font(path, size, index=0):
    try:
        return ImageFont.truetype(path, size, index=index)
    except Exception:
        return ImageFont.truetype(path, size)


def vgrad(draw, box, c1, c2):
    x0, y0, x1, y1 = box
    for y in range(y0, y1):
        t = (y - y0) / max(y1 - y0, 1)
        c = tuple(round(a + (b - a) * t) for a, b in zip(c1, c2))
        draw.line([(x0, y), (x1, y)], fill=c)


img = Image.new("RGB", (W, H))
d = ImageDraw.Draw(img)

# 页面背景：浅灰蓝
vgrad(d, (0, 0, W, H), (238, 242, 247), (214, 224, 235))

# 浏览器窗口
bx, by, bw, bh = 90, 70, W - 180, H - 130
d.rounded_rectangle([bx, by, bx + bw, by + bh], 18, fill=(255, 255, 255), outline=(200, 208, 218), width=2)

# 浏览器标题栏
d.rounded_rectangle([bx, by, bx + bw, by + 64], 18, fill=(236, 240, 245))
d.rectangle([bx, by + 40, bx + bw, by + 64], fill=(236, 240, 245))
for i, c in enumerate([(255, 95, 86), (255, 189, 46), (39, 201, 63)]):
    cx = bx + 34 + i * 36
    d.ellipse([cx - 10, by + 22, cx + 10, by + 42], fill=c)

# 地址栏
d.rounded_rectangle([bx + 140, by + 16, bx + bw - 140, by + 48], 16, fill=(255, 255, 255), outline=(210, 216, 224))
f_url = font(FONT_HELV, 22)
d.text((bx + 165, by + 22), "https://caddyserver.com/download", font=f_url, fill=(90, 100, 115))

# Caddy 标志区
f_logo = font(FONT_HELV, 72, 1)  # bold
d.text((bx + 70, by + 110), "CADDY", font=f_logo, fill=(30, 42, 56))
d.text((bx + 72, by + 200), "The HTTP/2 web server with automatic HTTPS", font=font(FONT_HELV, 26), fill=(110, 122, 138))

# 左侧平台选择面板
px, py = bx + 70, by + 255
d.rounded_rectangle([px, py, px + 430, py + 190], 14, fill=(246, 248, 251), outline=(214, 221, 230), width=2)
d.text((px + 28, py + 20), "PLATFORM", font=font(FONT_HELV, 22, 1), fill=(130, 140, 155))
chips = ["Linux 64-bit", "macOS 64-bit", "Windows 64-bit"]
for i, label in enumerate(chips):
    cy = py + 58 + i * 44
    if i == 0:
        d.rounded_rectangle([px + 24, cy, px + 406, cy + 34], 17, fill=(38, 132, 255))
        d.text((px + 44, cy + 4), label, font=font(FONT_HELV, 24, 1), fill=(255, 255, 255))
    else:
        d.rounded_rectangle([px + 24, cy, px + 406, cy + 34], 17, outline=(200, 208, 218), width=2)
        d.text((px + 44, cy + 4), label, font=font(FONT_HELV, 24), fill=(100, 112, 128))

# 右侧插件面板
qx = px + 470
d.rounded_rectangle([qx, py, qx + 430, py + 190], 14, fill=(246, 248, 251), outline=(214, 221, 230), width=2)
d.text((qx + 28, py + 20), "PLUGINS", font=font(FONT_HELV, 22, 1), fill=(130, 140, 155))
for i, label in enumerate(["http.cache", "http.git", "tls.dns.cloudflare"]):
    cy = py + 58 + i * 44
    d.rounded_rectangle([qx + 24, cy, qx + 40, cy + 16], 8, outline=(150, 160, 175), width=2)
    d.text((qx + 54, cy - 8), label, font=font(FONT_HELV, 24), fill=(100, 112, 128))

# 下载按钮
d.rounded_rectangle([bx + 70, by + bh - 95, bx + 330, by + bh - 30], 16, fill=(31, 176, 116))
f_btn = font(FONT_HELV, 30, 1)
tw = d.textlength("DOWNLOAD", font=f_btn)
d.text((bx + 70 + (260 - tw) / 2, by + bh - 80), "DOWNLOAD", font=f_btn, fill=(255, 255, 255))

img.save("source/images/f3ac2345c6df862838743d2dd0c02830.png", optimize=True)
print("saved")
