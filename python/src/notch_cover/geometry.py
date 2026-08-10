from __future__ import annotations

from dataclasses import dataclass
from math import ceil


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


def estimate_cover_height(display: Size) -> int:
    """Estimate the menu-bar/notch cover height in physical display pixels."""
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

    source_cover_height = max(1, min(image.height, source_cover_height))
    return CoverPlan(
        source_cover_height=source_cover_height,
        screen_cover_height=screen_cover_height,
        scale=scale,
        crop_top=crop_top,
        visible_source_height=visible_source_height,
    )
