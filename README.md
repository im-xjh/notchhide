# notchhide

[中文说明](README.zh-CN.md)

`notchhide` is a Codex skill and small Python utility for creating TopNotch-like macOS wallpaper variants. It adds a black cover to the top of a wallpaper so the MacBook notch and menu-bar area blend into the background.

The script accounts for wallpaper scaling and crop behavior, so it works with nonstandard image sizes instead of drawing a fixed black strip.

## What It Does

- Adds a black top cover to static wallpaper images.
- Estimates the menu-bar/notch height from the target display size.
- Converts screen-space cover height back into source-image pixels.
- Supports macOS-style Fill Screen behavior via `--fit fill`.
- Allows manual tuning with `--display` and `--cover-height`.

## Install As A Codex Skill

Clone this repository into your Codex skills directory:

```bash
git clone https://github.com/im-xjh/notchhide.git ~/.codex/skills/notchhide
```

Then invoke it in Codex with prompts like:

```text
Use $notchhide to process this wallpaper and hide the MacBook notch.
```

## Use The Script Directly

The script requires Pillow. Use a project-local environment:

```bash
cd /path/to/notchhide
uv venv
uv pip install pillow
```

Run it:

```bash
.venv/bin/python scripts/notchhide.py /path/to/wallpaper.png --display 2940x1912
```

Or use a temporary `uv` environment:

```bash
uv run --with pillow python scripts/notchhide.py /path/to/wallpaper.png --display 2940x1912
```

By default, the output is written next to the input image:

```text
wallpaper.png -> wallpaper.notch.png
```

## Examples

Specify an output path:

```bash
uv run --with pillow python scripts/notchhide.py \
  /path/to/wallpaper.png \
  --display 2940x1912 \
  --output /path/to/wallpaper.notch.png
```

Fine-tune the visible cover height:

```bash
uv run --with pillow python scripts/notchhide.py \
  /path/to/wallpaper.png \
  --display 2940x1912 \
  --cover-height 73
```

Preview the calculation without writing a file:

```bash
uv run --with pillow python scripts/notchhide.py \
  /path/to/wallpaper.png \
  --display 2940x1912 \
  --dry-run
```

## Display Size

Pass the display size in physical pixels:

```bash
--display WIDTHxHEIGHT
```

For Retina displays, multiply the logical screen size by the backing scale. For example, a `1470x956` logical display at `2x` scale should use:

```bash
--display 2940x1912
```

If `--display` is omitted, the script tries to detect the current macOS display size automatically.

## Options

```text
input                    Input wallpaper image
--output, -o PATH         Output image path
--display WIDTHxHEIGHT    Target display physical pixels
--cover-height PIXELS     Top cover height in display pixels
--fit fill|stretch        Wallpaper fitting mode, default: fill
--color "#000000"         Cover color, default: black
--dry-run                 Print calculation without writing output
```

## How The Calculation Works

For `--fit fill`, notchhide mirrors macOS Fill Screen geometry:

1. Scale the image until it covers the full display.
2. Compute any centered crop caused by aspect-ratio mismatch.
3. Convert the desired menu-bar/notch cover height from display pixels back into source-image pixels.
4. Paint only that source-image top region.

This keeps the visible black area close to the actual menu-bar/notch height after macOS scales the wallpaper.

## Repository Layout

```text
notchhide/
├── SKILL.md
├── agents/
│   └── openai.yaml
└── scripts/
    └── notchhide.py
```
