"""Sentimize.ai — image art transformation engine.

Each function takes a PIL Image and returns a transformed PIL Image (or string for ASCII).
All functions auto-constrain input size for performance.
"""

import numpy as np
from PIL import Image, ImageDraw, ImageEnhance, ImageFont

MAX_DIM = 800
WATERMARK_TEXT = "Powered by Economic Integrity LLC  •  sentimize.ai"
BRAND_HEX = (200, 168, 78)  # #c8a84e


def _constrain(image: Image.Image, max_dim: int = MAX_DIM) -> Image.Image:
    """Shrink image if its longest side exceeds *max_dim*, preserving aspect ratio."""
    if max(image.size) <= max_dim:
        return image.copy()
    ratio = max_dim / max(image.size)
    return image.resize(
        (int(image.width * ratio), int(image.height * ratio)),
        Image.LANCZOS,
    )


def watermark(image: Image.Image) -> Image.Image:
    """Append a branded footer strip to the bottom of an image."""
    img = image.convert("RGB")
    w = img.width
    bar_h = max(22, w // 30)
    font = _get_font(max(10, bar_h // 2))

    bar = Image.new("RGB", (w, bar_h), (17, 17, 17))
    draw = ImageDraw.Draw(bar)
    draw.text((w // 2, bar_h // 2), WATERMARK_TEXT,
              fill=BRAND_HEX, font=font, anchor="mm")

    combined = Image.new("RGB", (w, img.height + bar_h))
    combined.paste(img, (0, 0))
    combined.paste(bar, (0, img.height))
    return combined


def watermark_text(text: str) -> str:
    """Append a branded credit line to ASCII art text."""
    return text + "\n\n" + WATERMARK_TEXT


# ---------------------------------------------------------------------------
# 1. Pixel Art
# ---------------------------------------------------------------------------

def pixelate(image: Image.Image, block_size: int = 10, num_colors: int = 16) -> Image.Image:
    """Down-sample then nearest-neighbour up-sample for a chunky pixel-art look."""
    img = _constrain(image).convert("RGB")
    small_w = max(1, img.width // block_size)
    small_h = max(1, img.height // block_size)
    small = img.resize((small_w, small_h), Image.BILINEAR)
    if num_colors < 256:
        small = small.quantize(colors=num_colors).convert("RGB")
    return small.resize(img.size, Image.NEAREST)


# ---------------------------------------------------------------------------
# 2. ASCII Art
# ---------------------------------------------------------------------------

CHARSETS = {
    "standard": list("@%#*+=-:. "),
    "blocks": list("█▓▒░ "),
    "minimal": list("#=:. "),
    "detailed": list(
        "$@B%8&WM#*oahkbdpqwmZO0QLCJUYXzcvunxrjft/\\|()1{}[]?-_+~<>i!lI;:,\"^`'. "
    ),
}


def to_ascii(image: Image.Image, width: int = 100, charset: str = "standard") -> str:
    """Map pixel brightness to characters, producing a text-art string."""
    chars = np.array(CHARSETS.get(charset, CHARSETS["standard"]))
    n = len(chars)

    img = _constrain(image)
    aspect = img.height / img.width
    new_h = max(1, int(width * aspect * 0.45))
    img = img.resize((width, new_h)).convert("L")

    pixels = np.array(img, dtype=np.float64)
    indices = np.clip((pixels / 256 * n).astype(int), 0, n - 1)

    return "\n".join("".join(chars[row]) for row in indices)


# ---------------------------------------------------------------------------
# 3. Sketch (edge detection)
# ---------------------------------------------------------------------------

def sketch(image: Image.Image, sigma: float = 2.0, invert: bool = True) -> Image.Image:
    """Canny edge-detection sketch effect."""
    from skimage.feature import canny

    img = _constrain(image).convert("L")
    arr = np.array(img, dtype=np.float64) / 255.0
    edges = canny(arr, sigma=sigma)

    if invert:
        result = ((~edges).astype(np.float64) * 255).astype(np.uint8)
    else:
        result = (edges.astype(np.float64) * 255).astype(np.uint8)
    return Image.fromarray(result, mode="L")


# ---------------------------------------------------------------------------
# 4. Quadtree decomposition
# ---------------------------------------------------------------------------

def quadtree(
    image: Image.Image,
    max_depth: int = 6,
    threshold: float = 15.0,
    show_borders: bool = True,
) -> Image.Image:
    """Recursively subdivide image regions by colour variance."""
    img = _constrain(image, max_dim=600).convert("RGB")
    src = np.array(img)
    h, w = src.shape[:2]

    canvas = Image.new("RGB", (w, h))
    draw = ImageDraw.Draw(canvas)
    outline = (30, 30, 30) if show_borders else None

    def _split(x: int, y: int, bw: int, bh: int, depth: int) -> None:
        if bw < 1 or bh < 1:
            return
        region = src[y : y + bh, x : x + bw]
        if region.size == 0:
            return

        flat = region.reshape(-1, 3).astype(np.float64)
        std = float(np.mean(np.std(flat, axis=0)))

        if std < threshold or depth >= max_depth or min(bw, bh) < 4:
            avg = tuple(int(v) for v in flat.mean(axis=0))
            draw.rectangle([x, y, x + bw - 1, y + bh - 1], fill=avg, outline=outline)
        else:
            hw, hh = bw // 2, bh // 2
            _split(x, y, hw, hh, depth + 1)
            _split(x + hw, y, bw - hw, hh, depth + 1)
            _split(x, y + hh, hw, bh - hh, depth + 1)
            _split(x + hw, y + hh, bw - hw, bh - hh, depth + 1)

    _split(0, 0, w, h, 0)
    return canvas


# ---------------------------------------------------------------------------
# 5. Pop Art / Posterize
# ---------------------------------------------------------------------------

def posterize(
    image: Image.Image, levels: int = 4, saturation: float = 1.5
) -> Image.Image:
    """Reduce colour depth and optionally boost saturation for a pop-art look."""
    img = _constrain(image).convert("RGB")
    arr = np.array(img, dtype=np.float64)
    factor = 256.0 / levels
    arr = np.floor(arr / factor) * factor + factor / 2
    arr = np.clip(arr, 0, 255).astype(np.uint8)
    result = Image.fromarray(arr)
    if abs(saturation - 1.0) > 0.01:
        result = ImageEnhance.Color(result).enhance(saturation)
    return result


# ---------------------------------------------------------------------------
# 6. Colour palette extraction
# ---------------------------------------------------------------------------

def extract_palette(
    image: Image.Image, n_colors: int = 6
) -> list[tuple[tuple[int, int, int], int]]:
    """Return the *n_colors* most dominant colours as ((r,g,b), pixel_count) pairs."""
    img = _constrain(image, max_dim=200).convert("RGB")
    quantized = img.quantize(colors=n_colors)
    rgb = quantized.convert("RGB")

    counts: dict[tuple[int, int, int], int] = {}
    for pixel in rgb.getdata():
        counts[pixel] = counts.get(pixel, 0) + 1

    return sorted(counts.items(), key=lambda x: -x[1])[:n_colors]


# ---------------------------------------------------------------------------
# 7. Color-by-number generator
# ---------------------------------------------------------------------------

def _get_font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    """Best-effort font loader that works across platforms."""
    for name in ("arial.ttf", "Arial.ttf", "DejaVuSans.ttf", "LiberationSans-Regular.ttf"):
        try:
            return ImageFont.truetype(name, size)
        except (OSError, IOError):
            continue
    try:
        return ImageFont.load_default(size=size)
    except TypeError:
        return ImageFont.load_default()


def color_by_number(
    image: Image.Image,
    n_colors: int = 8,
    min_region_pct: float = 0.4,
) -> tuple[Image.Image, Image.Image, list[tuple[int, tuple[int, int, int]]]]:
    """Turn a photo into a color-by-number template.

    Returns (outline_image, filled_preview, palette) where palette is a list
    of (number, (r, g, b)) pairs.
    """
    from scipy import ndimage

    img = _constrain(image, max_dim=600).convert("RGB")
    h, w = img.height, img.width
    total_pixels = h * w
    min_size = max(20, int(total_pixels * min_region_pct / 100))

    quantized = img.quantize(colors=n_colors).convert("RGB")
    q_arr = np.array(quantized)

    flat = q_arr.reshape(-1, 3)
    unique_colors, inverse = np.unique(flat, axis=0, return_inverse=True)
    color_map = (inverse + 1).reshape(h, w)  # 1-indexed

    h_diff = np.pad(color_map[:, :-1] != color_map[:, 1:], ((0, 0), (0, 1)))
    v_diff = np.pad(color_map[:-1, :] != color_map[1:, :], ((0, 1), (0, 0)))
    boundary = h_diff | v_diff

    outline_arr = np.full((h, w, 3), 255, dtype=np.uint8)
    outline_arr[boundary] = [0, 0, 0]

    outline_img = Image.fromarray(outline_arr)
    draw = ImageDraw.Draw(outline_img)
    font_size = max(8, min(13, w // 45))
    font = _get_font(font_size)

    for cidx in range(1, len(unique_colors) + 1):
        mask = (color_map == cidx).astype(np.int32)
        labeled, num_features = ndimage.label(mask)

        for j in range(1, num_features + 1):
            region = labeled == j
            if np.sum(region) < min_size:
                continue

            ys, xs = np.where(region)
            cy, cx = int(np.mean(ys)), int(np.mean(xs))

            if not region[cy, cx]:
                closest = np.argmin((ys - cy) ** 2 + (xs - cx) ** 2)
                cy, cx = int(ys[closest]), int(xs[closest])

            txt = str(cidx)
            draw.text(
                (cx, cy), txt,
                fill=(130, 130, 130), font=font, anchor="mm",
            )

    palette = [(i + 1, tuple(int(v) for v in c)) for i, c in enumerate(unique_colors)]

    return outline_img, quantized, palette
