# 刘海遮盖

一个替代 TopNotch 基础效果的小脚本：给壁纸顶部增加黑色遮盖，让 macOS 菜单栏和刘海区域融入黑色背景。

脚本默认按 macOS 的“填充屏幕”壁纸显示方式计算黑色遮盖高度。图片比例和屏幕比例不一致时，会把缩放和居中裁切计入计算，避免只按固定像素画条导致过高或过低。

## 安装

```bash
cd /Users/jhx/Documents/Code/刘海遮盖
uv sync
```

## 使用

自动读取当前显示器信息：

```bash
./bin/notch-cover /path/to/input.jpg
```

指定目标屏幕像素尺寸：

```bash
./bin/notch-cover /path/to/input.jpg --display 3024x1964
```

指定菜单栏遮盖高度：

```bash
./bin/notch-cover /path/to/input.jpg --display 3024x1964 --cover-height 74
```

输出文件默认保存在原图旁边，文件名加 `.notch`。例如：

```text
wallpaper.jpg -> wallpaper.notch.jpg
```

## 参数

- `input`：输入壁纸路径。
- `--output`：输出图片路径。
- `--display WIDTHxHEIGHT`：目标显示器像素尺寸。
- `--cover-height PIXELS`：屏幕上需要变黑的顶部高度，单位是目标显示器像素。默认按显示器高度估算。
- `--fit fill|stretch`：壁纸显示方式。默认 `fill`，对应 macOS 常用的“填充屏幕”。`stretch` 用于图片被拉伸到全屏的情况。
- `--color "#000000"`：遮盖颜色。
- `--dry-run`：只输出计算结果，不写文件。

## 高度估算

在没有明确传入 `--cover-height` 时，脚本会按显示器高度估算菜单栏区域高度。估算值会限制在合理范围内，避免黑条明显过大或不足。要达到最贴近当前机器的效果，建议第一次运行后按实际截图微调 `--cover-height`。
