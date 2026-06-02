# notchhide

[English](README.md)

`notchhide` 是一个 Codex skill，也可以作为独立 Python 脚本使用。它会在壁纸顶部增加一条黑色遮盖区域，让 MacBook 刘海和菜单栏融入黑色背景，达到类似 TopNotch 的静态壁纸效果。

脚本会计算壁纸在 macOS“填充屏幕”模式下的缩放和裁切，因此适合处理非标准尺寸图片，避免只画固定高度黑条导致遮盖过度或不足。

## 功能

- 给静态壁纸顶部增加黑色遮盖。
- 根据目标显示器尺寸估算菜单栏和刘海区域高度。
- 将屏幕上的遮盖高度换算回原图像素。
- 支持 macOS 常用的 Fill Screen 行为，对应 `--fit fill`。
- 支持用 `--display` 和 `--cover-height` 手动微调。

## 作为 Codex Skill 安装

将仓库克隆到 Codex skills 目录：

```bash
git clone https://github.com/im-xjh/notchhide.git ~/.codex/skills/notchhide
```

之后可以在 Codex 中这样调用：

```text
Use $notchhide to process this wallpaper and hide the MacBook notch.
```

## 直接运行脚本

脚本依赖 Pillow。建议使用项目级虚拟环境：

```bash
cd /path/to/notchhide
uv venv
uv pip install pillow
```

运行：

```bash
.venv/bin/python scripts/notchhide.py /path/to/wallpaper.png --display 2940x1912
```

也可以使用临时 `uv` 环境：

```bash
uv run --with pillow python scripts/notchhide.py /path/to/wallpaper.png --display 2940x1912
```

默认输出在原图旁边：

```text
wallpaper.png -> wallpaper.notch.png
```

## 示例

指定输出路径：

```bash
uv run --with pillow python scripts/notchhide.py \
  /path/to/wallpaper.png \
  --display 2940x1912 \
  --output /path/to/wallpaper.notch.png
```

微调可见遮盖高度：

```bash
uv run --with pillow python scripts/notchhide.py \
  /path/to/wallpaper.png \
  --display 2940x1912 \
  --cover-height 73
```

只查看计算结果，不写入文件：

```bash
uv run --with pillow python scripts/notchhide.py \
  /path/to/wallpaper.png \
  --display 2940x1912 \
  --dry-run
```

## 显示器尺寸

`--display` 需要传入显示器的物理像素尺寸：

```bash
--display WIDTHxHEIGHT
```

Retina 屏幕需要用逻辑尺寸乘以缩放倍率。例如逻辑尺寸是 `1470x956`，缩放倍率是 `2x`，则应传入：

```bash
--display 2940x1912
```

如果省略 `--display`，脚本会尝试自动读取当前 macOS 显示器尺寸。自动读取失败时再手动传入即可。

## 参数

```text
input                    输入壁纸图片
--output, -o PATH         输出图片路径
--display WIDTHxHEIGHT    目标显示器物理像素尺寸
--cover-height PIXELS     屏幕顶部遮盖高度，单位是显示器像素
--fit fill|stretch        壁纸适配模式，默认是 fill
--color "#000000"         遮盖颜色，默认黑色
--dry-run                 只输出计算结果，不写入文件
```

## 计算方式

在 `--fit fill` 模式下，notchhide 会模拟 macOS Fill Screen 的几何关系：

1. 将原图等比缩放到覆盖整个显示器。
2. 计算因为宽高比不一致产生的居中裁切。
3. 将菜单栏和刘海区域的屏幕像素高度换算回原图像素高度。
4. 只涂黑原图顶部对应区域。

这样设置为壁纸后，屏幕上实际可见的黑色区域会接近菜单栏和刘海高度。

## 仓库结构

```text
notchhide/
├── SKILL.md
├── README.md
├── README.zh-CN.md
├── agents/
│   └── openai.yaml
└── scripts/
    └── notchhide.py
```
