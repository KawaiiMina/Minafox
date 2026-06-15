#!/usr/bin/env python3
"""Export MinaFox SVG logo assets with Inkscape.

This keeps SVG as the source of truth and generates transparent PNG icon sizes plus
Linux hicolor layout copies.
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

ICON_SIZES = (16, 32, 48, 64, 128, 256, 512, 1024)


class ExportError(RuntimeError):
    pass


def require_tool(name: str) -> str:
    path = shutil.which(name)
    if not path:
        raise ExportError(f"required tool not found: {name}")
    return path


def validate_svg(svg_path: Path) -> None:
    try:
        root = ET.parse(svg_path).getroot()
    except ET.ParseError as exc:
        raise ExportError(f"invalid SVG XML: {exc}") from exc

    tag = root.tag.rsplit("}", 1)[-1].lower()
    if tag != "svg":
        raise ExportError("source file is not an SVG document")

    for element in root.iter():
        element_tag = element.tag.rsplit("}", 1)[-1].lower()
        if element_tag == "image":
            raise ExportError("SVG contains embedded raster image; use clean vector paths/shapes instead")


def run(cmd: list[str]) -> None:
    proc = subprocess.run(
        cmd,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    if proc.returncode != 0:
        raise ExportError("command failed:\n" + " ".join(cmd) + "\n" + proc.stdout)


def export_png(inkscape: str, source_svg: Path, output_png: Path, size: int) -> None:
    output_png.parent.mkdir(parents=True, exist_ok=True)
    run(
        [
            inkscape,
            str(source_svg),
            "--export-type=png",
            f"--export-filename={output_png}",
            f"--export-width={size}",
            f"--export-height={size}",
            "--export-background-opacity=0",
        ]
    )


def identify_png(identify: str, png: Path, size: int) -> None:
    proc = subprocess.run(
        [identify, "-format", "%w %h %[channels]", str(png)],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    if proc.returncode != 0:
        raise ExportError(f"identify failed for {png}: {proc.stdout}")
    expected_prefix = f"{size} {size} "
    if not proc.stdout.startswith(expected_prefix):
        raise ExportError(f"wrong PNG size for {png}: {proc.stdout!r}")
    if "a" not in proc.stdout.lower():
        raise ExportError(f"PNG lacks alpha channel: {png}: {proc.stdout!r}")


def export_assets(source_svg: Path, out_dir: Path, app_name: str) -> None:
    inkscape = require_tool("inkscape")
    identify = require_tool("identify")
    source_svg = source_svg.resolve()
    out_dir = out_dir.resolve()

    if not source_svg.exists():
        raise ExportError(f"source SVG not found: {source_svg}")
    validate_svg(source_svg)

    out_dir.mkdir(parents=True, exist_ok=True)
    copied_svg = out_dir / f"{app_name}-logo.svg"
    shutil.copy2(source_svg, copied_svg)

    icons_dir = out_dir / "icons"
    for size in ICON_SIZES:
        png = icons_dir / f"{app_name}-{size}.png"
        export_png(inkscape, source_svg, png, size)
        identify_png(identify, png, size)

        hicolor = icons_dir / "hicolor" / f"{size}x{size}" / "apps" / f"{app_name}.png"
        hicolor.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(png, hicolor)

    preview = out_dir / f"{app_name}-logo-preview-1024.png"
    shutil.copy2(icons_dir / f"{app_name}-1024.png", preview)


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-svg", type=Path, default=Path("assets/source/minafox-logo.svg"))
    parser.add_argument("--out-dir", type=Path, default=Path("build/minafox-logo-assets"))
    parser.add_argument("--app-name", default="minafox")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(sys.argv[1:] if argv is None else argv)
    try:
        export_assets(args.source_svg, args.out_dir, args.app_name)
    except ExportError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    print(f"EXPORTED {args.app_name} SVG logo assets to {args.out_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
