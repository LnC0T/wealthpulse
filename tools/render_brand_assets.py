import os
import math
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS = os.path.join(ROOT, "assets")
os.makedirs(ASSETS, exist_ok=True)

GOLD_INNER = (255, 248, 210)
GOLD_MID = (255, 214, 92)
GOLD_OUTER = (192, 122, 12)
NAVY_INNER = (17, 33, 66)
NAVY_OUTER = (13, 24, 49)


def load_font(size, bold=False):
    candidates = [
        "/System/Library/Fonts/Avenir Next.ttc",
        "/System/Library/Fonts/HelveticaNeue.ttc",
        "/System/Library/Fonts/Helvetica.ttc",
        "/System/Library/Fonts/ArialHB.ttc",
    ]
    for path in candidates:
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, size=size, index=1 if bold else 0)
            except Exception:
                try:
                    return ImageFont.truetype(path, size=size)
                except Exception:
                    continue
    return ImageFont.load_default()


def radial_gradient(size, inner, mid, outer):
    w, h = size
    y, x = np.ogrid[:h, :w]
    cx, cy = w / 2.0, h / 2.0
    r = min(w, h) / 2.0
    dist = np.sqrt((x - cx) ** 2 + (y - cy) ** 2) / r
    dist = np.clip(dist, 0, 1)

    t1 = np.clip(dist / 0.55, 0, 1)
    t2 = np.clip((dist - 0.55) / 0.45, 0, 1)

    inner = np.array(inner, dtype=np.float32)
    mid = np.array(mid, dtype=np.float32)
    outer = np.array(outer, dtype=np.float32)

    color = np.empty((h, w, 3), dtype=np.float32)
    mask = dist <= 0.55
    color[mask] = inner + (mid - inner) * t1[mask][..., None]
    color[~mask] = mid + (outer - mid) * t2[~mask][..., None]

    return Image.fromarray(np.uint8(color), mode="RGB")


def gold_coin(size):
    w = h = size
    base = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    grad = radial_gradient((w, h), GOLD_INNER, GOLD_MID, GOLD_OUTER)

    mask = Image.new("L", (w, h), 0)
    draw_mask = ImageDraw.Draw(mask)
    draw_mask.ellipse((0, 0, w, h), fill=255)
    base.paste(grad, (0, 0), mask)

    # Glossy highlight
    highlight = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(highlight)
    draw.ellipse((w * 0.05, h * 0.05, w * 0.85, h * 0.85), fill=(255, 255, 255, 55))
    highlight = highlight.filter(ImageFilter.GaussianBlur(radius=w * 0.03))
    base = Image.alpha_composite(base, highlight)

    # Specular band for metallic sheen
    band = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    band_draw = ImageDraw.Draw(band)
    band_draw.polygon(
        [
            (w * 0.05, h * 0.18),
            (w * 0.95, h * 0.36),
            (w * 0.9, h * 0.48),
            (w * 0.0, h * 0.3),
        ],
        fill=(255, 255, 255, 85),
    )
    band = band.filter(ImageFilter.GaussianBlur(radius=w * 0.02))
    base = Image.alpha_composite(base, band)

    sparkle = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    sparkle_draw = ImageDraw.Draw(sparkle)
    sparkle_draw.ellipse((w * 0.72, h * 0.18, w * 0.82, h * 0.28), fill=(255, 255, 255, 120))
    sparkle = sparkle.filter(ImageFilter.GaussianBlur(radius=w * 0.015))
    base = Image.alpha_composite(base, sparkle)

    # Rim
    rim = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    rim_draw = ImageDraw.Draw(rim)
    rim_draw.ellipse((w * 0.03, h * 0.03, w * 0.97, h * 0.97), outline=(255, 235, 160, 180), width=int(w * 0.02))
    base = Image.alpha_composite(base, rim)

    return base


def navy_badge(size):
    w = h = size
    badge = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    grad = radial_gradient((w, h), NAVY_INNER, NAVY_OUTER, (8, 16, 33))
    mask = Image.new("L", (w, h), 0)
    draw_mask = ImageDraw.Draw(mask)
    draw_mask.ellipse((0, 0, w, h), fill=255)
    badge.paste(grad, (0, 0), mask)
    return badge


def render_logo(size):
    canvas = Image.new("RGBA", (size, size), (0, 0, 0, 0))

    coin = gold_coin(int(size * 0.74))
    coin_pos = ((size - coin.size[0]) // 2, (size - coin.size[1]) // 2)
    shadow = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    shadow_draw = ImageDraw.Draw(shadow)
    shadow_draw.ellipse(
        (
            coin_pos[0] + size * 0.08,
            coin_pos[1] + size * 0.08,
            coin_pos[0] + coin.size[0] - size * 0.08,
            coin_pos[1] + coin.size[1] - size * 0.08,
        ),
        fill=(0, 0, 0, 60),
    )
    shadow = shadow.filter(ImageFilter.GaussianBlur(radius=size * 0.03))
    canvas = Image.alpha_composite(canvas, shadow)

    canvas.paste(coin, coin_pos, coin)

    badge = navy_badge(int(size * 0.46))
    badge_pos = ((size - badge.size[0]) // 2, (size - badge.size[1]) // 2)
    canvas.paste(badge, badge_pos, badge)

    draw = ImageDraw.Draw(canvas)
    font_main = load_font(int(size * 0.22), bold=True)
    font_p = load_font(int(size * 0.22), bold=True)

    draw.text((size * 0.36, size * 0.47), "W", font=font_main, fill=(255, 237, 190, 255))
    draw.text((size * 0.47, size * 0.47), "P", font=font_p, fill=(255, 255, 255, 255))

    # Pulse line
    pulse_points = [
        (size * 0.28, size * 0.64),
        (size * 0.38, size * 0.64),
        (size * 0.41, size * 0.59),
        (size * 0.45, size * 0.69),
        (size * 0.49, size * 0.62),
        (size * 0.54, size * 0.62),
    ]
    draw.line(pulse_points, fill=(255, 237, 190, 255), width=int(size * 0.012), joint="curve")

    # Growth bars
    bar_width = int(size * 0.065)
    bars = [
        (size * 0.62, size * 0.57, size * 0.62 + bar_width, size * 0.75, (255, 214, 92, 255)),
        (size * 0.69, size * 0.53, size * 0.69 + bar_width, size * 0.78, (234, 182, 72, 255)),
        (size * 0.76, size * 0.49, size * 0.76 + bar_width, size * 0.82, (192, 122, 12, 255)),
    ]
    for x1, y1, x2, y2, color in bars:
        draw.rounded_rectangle((x1, y1, x2, y2), radius=int(size * 0.02), fill=color)

    return canvas


def render_header(width, height):
    bg = Image.new("RGB", (width, height), (249, 251, 255))
    gradient = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(gradient)
    for i in range(width):
        ratio = i / max(1, width - 1)
        r = int(249 + (238 - 249) * ratio)
        g = int(251 + (242 - 251) * ratio)
        b = int(255 + (249 - 255) * ratio)
        draw.line([(i, 0), (i, height)], fill=(r, g, b, 255))
    bg = Image.alpha_composite(bg.convert("RGBA"), gradient)

    logo = render_logo(int(height * 0.8))
    logo = logo.resize((int(height * 0.8), int(height * 0.8)), Image.LANCZOS)
    logo_x = int(height * 0.15)
    logo_y = (height - logo.size[1]) // 2
    bg.paste(logo, (logo_x, logo_y), logo)

    draw = ImageDraw.Draw(bg)
    title_font = load_font(int(height * 0.32), bold=True)
    subtitle_font = load_font(int(height * 0.12), bold=False)

    title_x = logo_x + logo.size[0] + int(height * 0.15)
    title_y = int(height * 0.38)
    draw.text((title_x, title_y), "WealthPulse", font=title_font, fill=(29, 43, 79, 255))

    subtitle = "Portfolio Intelligence & Community Market"
    subtitle_y = title_y + int(height * 0.28)
    draw.text((title_x, subtitle_y), subtitle, font=subtitle_font, fill=(93, 107, 130, 255))

    # Accent line
    line_y = subtitle_y + int(height * 0.18)
    draw.rounded_rectangle(
        (title_x, line_y, title_x + int(width * 0.38), line_y + int(height * 0.02)),
        radius=int(height * 0.02),
        fill=(255, 214, 92, 255)
    )

    return bg.convert("RGBA")


def save_variants(base_image, name, sizes):
    for size in sizes:
        if isinstance(size, tuple):
            img = base_image.resize(size, Image.LANCZOS)
            suffix = f"{size[0]}x{size[1]}"
        else:
            img = base_image.resize((size, size), Image.LANCZOS)
            suffix = f"{size}"
        filename = os.path.join(ASSETS, f"{name}_{suffix}.png")
        img.save(filename)


if __name__ == "__main__":
    logo_base = render_logo(2048)
    logo_base.save(os.path.join(ASSETS, "wealthpulse_logo.png"))
    logo_base.save(os.path.join(ASSETS, "wealthpulse_logo_transparent.png"))
    logo_base.resize((1024, 1024), Image.LANCZOS).save(os.path.join(ASSETS, "wealthpulse_logo_1024.png"))
    logo_base.resize((1024, 1024), Image.LANCZOS).save(os.path.join(ASSETS, "wealthpulse_logo_transparent_1024.png"))
    logo_base.resize((512, 512), Image.LANCZOS).save(os.path.join(ASSETS, "wealthpulse_logo_512.png"))

    header_base = render_header(3600, 1000)
    header_base.save(os.path.join(ASSETS, "wealthpulse_header.png"))
    header_base.resize((1800, 500), Image.LANCZOS).save(os.path.join(ASSETS, "wealthpulse_header_1800.png"))
    header_base.resize((1200, 333), Image.LANCZOS).save(os.path.join(ASSETS, "wealthpulse_header_1200.png"))

    print("Rendered logo and header assets to", ASSETS)
