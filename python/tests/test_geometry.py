from notch_cover.geometry import Size, calculate_cover_plan, estimate_cover_height


def test_estimate_cover_height_is_bounded() -> None:
    assert estimate_cover_height(Size(1920, 1080)) == 48
    assert estimate_cover_height(Size(3024, 1964)) == 75
    assert estimate_cover_height(Size(6016, 3384)) == 96


def test_fill_same_aspect_ratio_uses_scaled_cover_height() -> None:
    plan = calculate_cover_plan(
        image=Size(1512, 982),
        display=Size(3024, 1964),
        screen_cover_height=74,
    )

    assert plan.source_cover_height == 37
    assert plan.crop_top == 0


def test_fill_wide_image_accounts_for_vertical_crop() -> None:
    plan = calculate_cover_plan(
        image=Size(2000, 4000),
        display=Size(3024, 1964),
        screen_cover_height=74,
    )

    assert plan.source_cover_height == 1400
    assert round(plan.crop_top, 2) == 1350.53


def test_stretch_ignores_crop() -> None:
    plan = calculate_cover_plan(
        image=Size(4000, 2000),
        display=Size(3024, 1964),
        screen_cover_height=74,
        fit="stretch",
    )

    assert plan.source_cover_height == 76
    assert plan.crop_top == 0
