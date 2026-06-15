#!/usr/bin/env python3
"""Validate MinaFox logo/icon assets.

Requires Pillow for pixel checks. Run with:

    uv run --with pillow python3 scripts/validate-minafox-icons.py
"""
from __future__ import annotations

import sys
from pathlib import Path

try:
    from PIL import Image, ImageChops  # type: ignore[import-not-found]
except ModuleNotFoundError as exc:  # pragma: no cover - helpful CLI failure
    raise SystemExit(
        "Pillow is required. Run: uv run --with pillow python3 scripts/validate-minafox-icons.py"
    ) from exc

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"
ICONS = ASSETS / "icons"
SIZES = (16, 32, 48, 64, 128, 256, 512, 1024)


def require(path: Path) -> None:
    if not path.exists():
        raise AssertionError(f"missing required asset: {path.relative_to(ROOT)}")


def open_rgba(path: Path) -> Image.Image:
    require(path)
    image = Image.open(path)
    if image.mode != "RGBA":
        raise AssertionError(f"{path.relative_to(ROOT)} must be RGBA, got {image.mode}")
    return image


def assert_transparent_corners(path: Path, image: Image.Image) -> None:
    width, height = image.size
    corners = ((0, 0), (width - 1, 0), (0, height - 1), (width - 1, height - 1))
    bad = []
    for xy in corners:
        if image.getpixel(xy) != (0, 0, 0, 0):
            bad.append((xy, image.getpixel(xy)))
    if bad:
        raise AssertionError(f"{path.relative_to(ROOT)} corners are not transparent black: {bad}")


def assert_has_real_alpha(path: Path, image: Image.Image) -> None:
    alpha_min, alpha_max = image.getchannel("A").getextrema()
    if alpha_min != 0 or alpha_max != 255:
        raise AssertionError(
            f"{path.relative_to(ROOT)} expected alpha extrema (0, 255), got {(alpha_min, alpha_max)}"
        )


def assert_transparent_rgb_zero(path: Path, image: Image.Image) -> None:
    pixels = image.get_flattened_data() if hasattr(image, "get_flattened_data") else image.getdata()
    for index, (red, green, blue, alpha) in enumerate(pixels):
        if alpha == 0 and (red, green, blue) != (0, 0, 0):
            raise AssertionError(
                f"{path.relative_to(ROOT)} transparent pixel {index} has hidden RGB {(red, green, blue)}"
            )


def assert_same_pixels(left_path: Path, right_path: Path) -> None:
    left = open_rgba(left_path)
    right = open_rgba(right_path)
    if left.size != right.size:
        raise AssertionError(
            f"size mismatch: {left_path.relative_to(ROOT)} {left.size} != {right_path.relative_to(ROOT)} {right.size}"
        )
    if ImageChops.difference(left, right).getbbox() is not None:
        raise AssertionError(
            f"hicolor copy differs from flat icon: {right_path.relative_to(ROOT)}"
        )


def validate_png_assets() -> None:
    master = open_rgba(ASSETS / "minafox-logo-transparent.png")
    if master.size != (1024, 1024):
        raise AssertionError(f"master logo expected 1024x1024, got {master.size}")
    assert_has_real_alpha(ASSETS / "minafox-logo-transparent.png", master)
    assert_transparent_corners(ASSETS / "minafox-logo-transparent.png", master)
    assert_transparent_rgb_zero(ASSETS / "minafox-logo-transparent.png", master)

    for size in SIZES:
        icon_path = ICONS / f"minafox-{size}.png"
        image = open_rgba(icon_path)
        if image.size != (size, size):
            raise AssertionError(f"{icon_path.relative_to(ROOT)} expected {size}x{size}, got {image.size}")
        assert_has_real_alpha(icon_path, image)
        assert_transparent_corners(icon_path, image)
        assert_transparent_rgb_zero(icon_path, image)

        hicolor = ICONS / "hicolor" / f"{size}x{size}" / "apps" / "minafox.png"
        assert_same_pixels(icon_path, hicolor)


def validate_svg_wrapper() -> None:
    svg = ASSETS / "minafox-logo.svg"
    require(svg)
    text = svg.read_text(encoding="utf-8")
    required = [
        "MinaFox logo",
        "minafox-logo-transparent.png",
        "raster PNG wrapper",
    ]
    for marker in required:
        if marker not in text:
            raise AssertionError(f"{svg.relative_to(ROOT)} missing marker: {marker}")


def validate_ico() -> None:
    ico = ICONS / "minafox.ico"
    require(ico)
    with Image.open(ico) as image:
        sizes = getattr(image, "ico", None).sizes() if getattr(image, "ico", None) else {image.size}
    expected = {(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)}
    missing = expected - set(sizes)
    if missing:
        raise AssertionError(f"{ico.relative_to(ROOT)} missing ICO sizes: {sorted(missing)}; found {sorted(sizes)}")


def main() -> int:
    validate_png_assets()
    validate_svg_wrapper()
    validate_ico()
    print("validated MinaFox logo/icon assets")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
