import dataclasses

from PyQt6.QtGui import QColor

from negpy.desktop.view.styles.theme import DAY_COLORS, ThemeConfig


def _luminance(hex_color: str) -> float:
    def channel(c: int) -> float:
        c = c / 255
        return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4

    r, g, b = (int(hex_color[i : i + 2], 16) for i in (1, 3, 5))
    return 0.2126 * channel(r) + 0.7152 * channel(g) + 0.0722 * channel(b)


def _ratio(a: str, b: str) -> float:
    hi, lo = sorted((_luminance(a), _luminance(b)), reverse=True)
    return (hi + 0.05) / (lo + 0.05)


DAY = dataclasses.replace(ThemeConfig(), **DAY_COLORS)


def test_every_day_color_names_a_theme_token():
    assert set(DAY_COLORS) <= {f.name for f in dataclasses.fields(ThemeConfig)}


def test_day_text_reads_on_every_ground():
    texts = ("text_primary", "text_secondary", "text_hint", "error_text", "warn_amber", "status_success")
    texts += ("channel_red_text", "channel_green_text", "channel_blue_text")
    for text in texts:
        for ground in ("bg_panel", "bg_card", "bg_input", "bg_header"):
            assert _ratio(getattr(DAY, text), getattr(DAY, ground)) >= 4.5, (text, ground)


def test_day_accent_text_and_slider_fill_read():
    for fill in ("bg_primary", "bg_primary_hover", "bg_checked", "bg_checked_hover"):
        assert _ratio(DAY.text_on_accent, getattr(DAY, fill)) >= 4.5, fill
    assert _ratio(DAY.mark_photo, DAY.bg_reset) >= 4.5
    assert _ratio(DAY.slider_fill, DAY.bg_selected) >= 3.0


def test_no_day_color_is_a_bright_red_but_errors_and_the_red_channel():
    allowed = {"error", "error_text", "channel_red", "channel_red_text"}
    for name, value in DAY_COLORS.items():
        if name in allowed or not value.startswith("#"):
            continue
        color = QColor(value)
        hue = color.hslHueF()
        assert not ((hue < 0.05 or hue > 0.95) and color.hslSaturationF() > 0.5 and color.lightnessF() > 0.3), name
