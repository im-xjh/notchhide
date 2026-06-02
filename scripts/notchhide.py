#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import subprocess
from dataclasses import dataclass
from math import ceil
from pathlib import Path

try:
    from PIL import Image, ImageColor, ImageDraw
except ModuleNotFoundError as exc:
    raise SystemExit(
        "Pillow is required. Install it in a project-local environment, for example: "
        "uv venv && uv pip install pillow"
    ) from exc


@dataclass(frozen=True)
class Size:
    width: int
    height: int

    def __post_init__(self) -> None:
        if self.width <= 0 or self.height <= 0:
            raise ValueError("width and height must be positive")


@dataclass(frozen=True)
class CoverPlan:
    source_cover_height: int
    screen_cover_height: int
    scale: float
    crop_top: float
    visible_source_height: float


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    input_path = args.input.expanduser().resolve()
    if not input_path.exists():
        raise SystemExit(f"Input file does not exist: {input_path}")

    display = parse_size(args.display) if args.display else detect_display_size()
    if display is None:
        raise SystemExit(
            "Could not detect display size. Pass --display WIDTHxHEIGHT, for example --display 2940x1912."
        )

    output_path = (
        args.output.expanduser().resolve()
        if args.output
        else input_path.with_name(f"{input_path.stem}.notch{input_path.suffix}")
    )

    with Image.open(input_path) as image:
        image_size = Size(*image.size)
        plan = calculate_cover_plan(
            image=image_size,
            display=display,
            screen_cover_height=args.cover_height,
            fit=args.fit,
        )

        print(f"Input: {input_path}")
        print(f"Image: {image_size.width}x{image_size.height}px")
        print(f"Display: {display.width}x{display.height}px")
        print(f"Screen cover: {plan.screen_cover_height}px")
        print(f"Source cover: {plan.source_cover_height}px")
        print(f"Fit: {args.fit}")
        if args.fit == "fill":
            print(f"Scale: {plan.scale:.6f}")
            print(f"Top crop in source: {plan.crop_top:.2f}px")

        if args.dry_run:
            return 0

        result = image.copy()
        draw_cover(result, plan.source_cover_height, args.color)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        result.save(output_path)
        print(f"Output: {output_path}")

    return 0


def parse_args(argv: list[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Create a macOS wallpaper variant with a black notch/menu-bar cover."
    )
    parser.add_argument("input", type=Path, help="input wallpaper image")
    parser.add_argument("--output", "-o", type=Path, help="output image path")
    parser.add_argument("--display", help="target display size in physical pixels, such as 2940x1912")
    parser.add_argument("--cover-height", type=int, help="screen-space cover height in physical pixels")
    parser.add_argument("--fit", choices=("fill", "stretch"), default="fill", help="wallpaper fitting mode")
    parser.add_argument("--color", default="#000000", help="cover color")
    parser.add_argument("--dry-run", action="store_true", help="print calculation only")
    return parser.parse_args(argv)


def estimate_cover_height(display: Size) -> int:
    estimated = round(display.height * 0.038)
    return max(48, min(96, estimated))


def calculate_cover_plan(
    image: Size,
    display: Size,
    screen_cover_height: int | None = None,
    fit: str = "fill",
) -> CoverPlan:
    if screen_cover_height is None:
        screen_cover_height = estimate_cover_height(display)
    if screen_cover_height <= 0:
        raise ValueError("screen cover height must be positive")

    if fit == "fill":
        scale = max(display.width / image.width, display.height / image.height)
        visible_source_height = display.height / scale
        crop_top = max(0.0, (image.height - visible_source_height) / 2)
        source_cover_height = ceil(crop_top + screen_cover_height / scale)
    elif fit == "stretch":
        scale = display.height / image.height
        visible_source_height = float(image.height)
        crop_top = 0.0
        source_cover_height = ceil(screen_cover_height / scale)
    else:
        raise ValueError("fit must be 'fill' or 'stretch'")

    return CoverPlan(
        source_cover_height=max(1, min(image.height, source_cover_height)),
        screen_cover_height=screen_cover_height,
        scale=scale,
        crop_top=crop_top,
        visible_source_height=visible_source_height,
    )


def draw_cover(image: Image.Image, height: int, color: str) -> None:
    fill = ImageColor.getcolor(color, "RGBA" if image.mode == "RGBA" else "RGB")
    draw = ImageDraw.Draw(image)
    draw.rectangle((0, 0, image.width - 1, height - 1), fill=fill)


def parse_size(value: str) -> Size:
    match = re.fullmatch(r"\s*(\d+)\s*x\s*(\d+)\s*", value, re.I)
    if not match:
        raise argparse.ArgumentTypeError("size must look like WIDTHxHEIGHT")
    return Size(int(match.group(1)), int(match.group(2)))


def detect_display_size() -> Size | None:
    return detect_display_size_with_swift() or detect_display_size_with_system_profiler()


def detect_display_size_with_swift() -> Size | None:
    script = (
        "import AppKit; "
        "if let s = NSScreen.main { "
        "let scale = s.backingScaleFactor; "
        "print(\"\\(Int(s.frame.width * scale))x\\(Int(s.frame.height * scale))\") "
        "}"
    )
    try:
        proc = subprocess.run(
            ["swift", "-e", script],
            check=False,
            capture_output=True,
            text=True,
            timeout=25,
        )
    except (OSError, subprocess.TimeoutExpired):
        return None

    if proc.returncode != 0:
        return None

    for line in proc.stdout.splitlines():
        try:
            return parse_size(line)
        except argparse.ArgumentTypeError:
            continue
    return None


def detect_display_size_with_system_profiler() -> Size | None:
    try:
        proc = subprocess.run(
            ["system_profiler", "SPDisplaysDataType", "-json"],
            check=False,
            capture_output=True,
            text=True,
            timeout=10,
        )
    except (OSError, subprocess.TimeoutExpired):
        return None

    if proc.returncode != 0 or not proc.stdout.strip():
        return None

    try:
        data = json.loads(proc.stdout)
    except json.JSONDecodeError:
        return None

    for item in data.get("SPDisplaysDataType", []):
        size = size_from_display_item(item)
        if size:
            return size
        for display in item.get("spdisplays_ndrvs", []):
            size = size_from_display_item(display)
            if size:
                return size
    return None


def size_from_display_item(item: dict) -> Size | None:
    for key in ("spdisplays_resolution", "spdisplays_pixels"):
        value = item.get(key)
        if not isinstance(value, str):
            continue
        match = re.search(r"(\d+)\s*x\s*(\d+)", value.replace(",", ""), re.I)
        if match:
            return Size(int(match.group(1)), int(match.group(2)))
    return None


if __name__ == "__main__":
    raise SystemExit(main())
