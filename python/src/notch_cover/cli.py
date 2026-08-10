from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image, ImageColor, ImageDraw

from .geometry import Size, calculate_cover_plan
from .macos import current_display_size


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)

    input_path = args.input.expanduser().resolve()
    if not input_path.exists():
        raise SystemExit(f"Input file does not exist: {input_path}")

    display = _resolve_display(args.display)

    output_path = args.output
    if output_path is None:
        output_path = _default_output_path(input_path)
    else:
        output_path = output_path.expanduser().resolve()

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
        _draw_cover(result, plan.source_cover_height, args.color)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        result.save(output_path)
        print(f"Output: {output_path}")

    return 0


def _parse_args(argv: list[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Create a macOS wallpaper variant with a black notch/menu-bar cover.",
    )
    parser.add_argument("input", type=Path, help="input wallpaper image")
    parser.add_argument("--output", "-o", type=Path, help="output image path")
    parser.add_argument(
        "--display",
        help="target display size in physical pixels, for example 3024x1964",
    )
    parser.add_argument(
        "--cover-height",
        type=int,
        help="top cover height on the target display, in physical pixels",
    )
    parser.add_argument(
        "--fit",
        choices=("fill", "stretch"),
        default="fill",
        help="wallpaper fitting mode; use fill for macOS Fill Screen",
    )
    parser.add_argument("--color", default="#000000", help="cover color")
    parser.add_argument("--dry-run", action="store_true", help="print calculation only")
    return parser.parse_args(argv)


def _resolve_display(display_arg: str | None) -> Size:
    if display_arg:
        return _parse_size(display_arg)

    display = current_display_size()
    if display:
        return display

    raise SystemExit(
        "Could not detect display size. Pass --display WIDTHxHEIGHT, for example --display 3024x1964."
    )


def _parse_size(value: str) -> Size:
    normalized = value.lower().replace(" ", "")
    parts = normalized.split("x")
    if len(parts) != 2:
        raise argparse.ArgumentTypeError("display must look like WIDTHxHEIGHT")
    try:
        return Size(int(parts[0]), int(parts[1]))
    except ValueError as exc:
        raise argparse.ArgumentTypeError("display must contain integer pixels") from exc


def _default_output_path(input_path: Path) -> Path:
    return input_path.with_name(f"{input_path.stem}.notch{input_path.suffix}")


def _draw_cover(image: Image.Image, height: int, color: str) -> None:
    fill = ImageColor.getcolor(color, "RGBA" if image.mode == "RGBA" else "RGB")
    draw = ImageDraw.Draw(image)
    draw.rectangle((0, 0, image.width - 1, height - 1), fill=fill)


if __name__ == "__main__":
    raise SystemExit(main())
