#!/usr/bin/env python3
"""Tests for export-minafox-svg-logo.py."""

from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path


REPO = Path(__file__).resolve().parents[1]
SCRIPT = REPO / "scripts" / "export-minafox-svg-logo.py"
SAMPLE_SVG = REPO / "assets" / "source" / "sample-minafox-vector-logo.svg"


def run_export(out_dir: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--source-svg",
            str(SAMPLE_SVG),
            "--out-dir",
            str(out_dir),
            "--app-name",
            "minafox-test",
        ],
        cwd=REPO,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )


def test_exports_svg_to_png_icon_set_and_hicolor_layout() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        out_dir = Path(tmp) / "out"
        result = run_export(out_dir)
        assert result.returncode == 0, result.stdout
        for size in [16, 32, 48, 64, 128, 256, 512, 1024]:
            png = out_dir / "icons" / f"minafox-test-{size}.png"
            hicolor = out_dir / "icons" / "hicolor" / f"{size}x{size}" / "apps" / "minafox-test.png"
            assert png.exists(), f"missing {png}\n{result.stdout}"
            assert hicolor.exists(), f"missing {hicolor}\n{result.stdout}"
            identify = subprocess.run(
                ["identify", "-format", "%w %h %[channels]", str(png)],
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                check=True,
            )
            assert identify.stdout.startswith(f"{size} {size} "), identify.stdout
            assert "a" in identify.stdout.lower(), identify.stdout
        assert (out_dir / "minafox-test-logo.svg").exists()
        assert (out_dir / "minafox-test-logo-preview-1024.png").exists()


def test_rejects_svg_with_embedded_raster_image() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        bad_svg = tmp_path / "bad.svg"
        bad_svg.write_text(
            '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 10 10">'
            '<image href="data:image/png;base64,AAAA" width="10" height="10" />'
            '</svg>',
            encoding="utf-8",
        )
        out_dir = tmp_path / "out"
        result = subprocess.run(
            [
                sys.executable,
                str(SCRIPT),
                "--source-svg",
                str(bad_svg),
                "--out-dir",
                str(out_dir),
            ],
            cwd=REPO,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            check=False,
        )
        assert result.returncode != 0
        assert "embedded raster" in result.stdout.lower()


if __name__ == "__main__":
    tests = [
        test_exports_svg_to_png_icon_set_and_hicolor_layout,
        test_rejects_svg_with_embedded_raster_image,
    ]
    for test in tests:
        test()
        print(f"PASS {test.__name__}")
