---
name: notchhide
description: Generate TopNotch-like macOS wallpaper variants that hide the MacBook notch and menu-bar area. Use when Codex needs to process an image file or attached wallpaper by adding a precisely sized black top cover, replace TopNotch for static wallpapers, account for nonstandard image dimensions, fit/crop behavior, display pixel size, or tune notch/menu-bar cover height.
---

# Notchhide

## Workflow

1. Locate the input wallpaper image. For uploaded images, first find the actual file path in likely attachment, Downloads, or workspace locations and inspect dimensions before processing.
2. Determine the target display's physical pixel size. Prefer automatic detection via the script; if unavailable or slow, pass `--display WIDTHxHEIGHT`. For Retina displays, use logical size multiplied by backing scale.
3. Run `scripts/notchhide.py` from this skill. Use `--fit fill` for macOS Fill Screen behavior unless the user explicitly uses stretched wallpaper.
4. Verify the output by checking image dimensions and sample pixels: a pixel inside the top cover should be black, and a pixel below the calculated cover should retain original image color.
5. Give the user the absolute output path. If useful in Codex desktop, include a Markdown image preview with the absolute path.

## Script

Use:

```bash
python3 /path/to/notchhide/scripts/notchhide.py /path/to/wallpaper.png --display 2940x1912
```

Useful options:

- `--output /path/to/output.png`: explicit output path.
- `--display WIDTHxHEIGHT`: target display physical pixels.
- `--cover-height PIXELS`: screen-space top cover height. Use this for fine tuning if the default menu-bar estimate is too high or low.
- `--fit fill|stretch`: wallpaper scaling mode. Default is `fill`.
- `--color "#000000"`: cover color.
- `--dry-run`: print calculations without writing a file.

The script requires Pillow. If `import PIL` fails, create or reuse a project-local virtual environment and install Pillow there, preferably with `uv`, then run the script with that environment's Python.

## Calculation Rule

For `--fit fill`, the script mirrors macOS Fill Screen geometry: scale the image to cover the display, compute any centered crop, then convert the desired screen-space menu-bar/notch height back into source-image pixels. This prevents a fixed black strip from becoming too tall or too short when the wallpaper has nonstandard dimensions or aspect ratio.
