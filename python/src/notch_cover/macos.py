from __future__ import annotations

import json
import re
import subprocess

from .geometry import Size


_RESOLUTION_RE = re.compile(r"(?P<width>\d+)\s*x\s*(?P<height>\d+)", re.I)


def current_display_size() -> Size | None:
    """Return the first display size reported by macOS, if available."""
    data = _system_profiler_displays()
    if not data:
        return None

    for item in data.get("SPDisplaysDataType", []):
        size = _size_from_display_item(item)
        if size:
            return size
        for display in item.get("spdisplays_ndrvs", []):
            size = _size_from_display_item(display)
            if size:
                return size

    return None


def _system_profiler_displays() -> dict | None:
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
        return json.loads(proc.stdout)
    except json.JSONDecodeError:
        return None


def _size_from_display_item(item: dict) -> Size | None:
    candidates: list[Size] = []
    # Newer macOS prefixes these keys with "_" and reports the logical
    # resolution separately; physical pixels are the larger value on Retina.
    for key in ("spdisplays_pixels", "_spdisplays_pixels", "spdisplays_resolution", "_spdisplays_resolution"):
        value = item.get(key)
        if not isinstance(value, str):
            continue
        match = _RESOLUTION_RE.search(value.replace(",", ""))
        if match:
            candidates.append(Size(int(match.group("width")), int(match.group("height"))))
    if not candidates:
        return None
    return max(candidates, key=lambda size: size.width * size.height)
