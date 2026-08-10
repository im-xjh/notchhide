from notch_cover.geometry import Size
from notch_cover.macos import _size_from_display_item


def test_size_from_modern_display_item_uses_physical_pixels() -> None:
    item = {
        "_spdisplays_resolution": "1512 x 982 @ 120.00Hz",
        "_spdisplays_pixels": "3024 x 1964",
        "spdisplays_pixelresolution": "spdisplays_3024x1964Retina",
    }
    assert _size_from_display_item(item) == Size(3024, 1964)


def test_size_from_legacy_display_item() -> None:
    item = {
        "spdisplays_resolution": "3024 x 1964",
        "spdisplays_pixels": "3024 x 1964",
    }
    assert _size_from_display_item(item) == Size(3024, 1964)


def test_size_from_empty_item_returns_none() -> None:
    assert _size_from_display_item({}) is None
