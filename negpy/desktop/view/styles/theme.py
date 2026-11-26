from dataclasses import dataclass, field
from typing import Dict


@dataclass(frozen=True)
class ThemeConfig:
    """
    Centralized UI styling constants.
    """

    # Fonts (families are resolved at runtime in styles/fonts.py). Four roles, in px:
    # small = caption/hint, base = body (also the QSS global), header = section, title = dialog.
    font_size_small: int = 12
    font_size_base: int = 13
    font_size_header: int = 14
    font_size_title: int = 16
    # Chart axis and swatch captions only: the one size below the reading scale.
    font_size_micro: int = 9

    # Colors. Surfaces, darkest first.
    # bg_dark is also the macOS window background (view/mac_window.py): an alternate theme updates that fix.
    bg_dark: str = "#1C1E20"
    bg_panel: str = "#1C1E20"
    bg_input: str = "#16181A"
    bg_card: str = "#222427"
    bg_header: str = "#2A2C2F"
    bg_selected: str = "#343639"
    bg_hover: str = "#383A3D"
    bg_menu_selected: str = "#404245"
    # A checked toggle and a segmented control's current choice; also the Scan button's tint
    # while it cannot start or while it reads Stop.
    bg_checked: str = "#3A372F"
    bg_checked_hover: str = "#433F37"
    border_checked: str = "#8C8678"
    border_checked_hover: str = "#ECE6D6"
    # The primary action: the strongest button on a panel. A light fill, so its text is text_on_accent.
    bg_primary: str = "#ECE6D6"
    bg_primary_hover: str = "#D9D2C0"
    # The top bar's Reset: a dark safelight red, under the lightness of a bright red.
    bg_reset: str = "#7A241C"
    bg_reset_hover: str = "#6B2019"
    # An edited card's frame-scope stripe and lit Frame icon; a roll-scope card takes border_checked_hover.
    border_scope_frame: str = "#5D4B24"
    # The dot on an edited control. A warning takes a sign in warn_amber, never a dot.
    mark_edited: str = "#C79A3A"
    # The canvas strip's job bar, in the accent.
    progress_fill: str = "#ECE6D6"
    bg_accent_muted: str = "#2A2925"
    border_input: str = "#2C2E31"
    border_primary: str = "#36383B"
    border_color: str = "#46484C"
    border_hover: str = "#56585C"
    # Keyboard focus: a neutral edge, as hover and the arrow-key row are neutral.
    border_focus: str = "#898989"
    border_indicator: str = "#696969"
    slider_disabled: str = "#6E6A62"
    # The slider handle's ring and the track's fill from the default.
    slider_handle: str = "#ECE6D6"
    slider_fill: str = "#ECE6D6"
    text_on_accent: str = "#151515"
    text_primary: str = "#ECE6D6"
    text_secondary: str = "#BDB7A8"
    # hint = readable secondary copy (6.2:1 on bg_panel); muted = disabled widgets only, and
    # too dim (2.5:1) for text a user must read.
    text_hint: str = "#A39D8F"
    text_muted: str = "#5F5B53"
    text_unit: str = "#948E81"
    warn_amber: str = "#C79A3A"
    # Marks drawn over the photo: white on a dark edge or plate, which reads on any picture.
    mark_photo: str = "#FFFFFF"
    # The dark edge or plate under a photo mark; each site sets its own alpha (templates.with_alpha).
    mark_shadow: str = "#000000"
    # Errors and invalid input. Error copy takes the lighter tier, as the channel colors do: error
    # falls under 4.5:1 on a card, and a lighter error would dim the white mark on a failed-frame badge.
    error: str = "#D32F2F"
    error_text: str = "#FF6868"

    # Spacing scale (px)
    space_xs: int = 2
    space_sm: int = 4
    space_md: int = 6
    space_lg: int = 8
    space_xl: int = 12
    space_2xl: int = 16

    # Radius scale (px)
    radius_sm: int = 3
    radius_md: int = 4
    radius_lg: int = 6

    # Surface overlay tokens (rgba). Integer alpha where a widget sheet reads it.
    surface_scrim: str = "rgba(5, 5, 5, 115)"
    surface_pill: str = "rgba(0, 0, 0, 140)"
    surface_reveal_flash: str = "rgba(236, 230, 214, 0.35)"  # border_checked_hover, faint
    surface_hover_faint: str = "#0CFFFFFF"  # #AARRGGBB: QColor reads it, not rgba()
    surface_overlay: str = "rgba(28,30,32,0.88)"
    # A card header over its chart: light enough for the chart to read through.
    header_veil: str = "rgba(42,44,47,0.55)"
    header_veil_hover: str = "rgba(52,54,57,0.62)"
    surface_overlay_hover: str = "rgba(52,54,57,0.88)"

    # Font weight scale
    weight_regular: int = 400
    weight_medium: int = 500
    weight_semibold: int = 600
    weight_bold: int = 700

    # Channel colors: fills (histogram, chart bands) and a lighter tier for text, dots and
    # slider handles, where the fill tier falls under 4.5:1 on the panel.
    channel_red: str = "#D32F2F"
    channel_green: str = "#388E3C"
    channel_blue: str = "#1976D2"
    channel_red_text: str = "#FF6868"
    channel_green_text: str = "#5ADC78"
    channel_blue_text: str = "#6398FF"
    # Subtractive filtration sliders.
    filter_cyan: str = "#00B1B1"
    filter_magenta: str = "#B100B1"
    filter_yellow: str = "#B1B100"
    # Dodge & Burn: the same amber and blue on the overlay, the mask list and the printing notes.
    dodge: str = "#E8C84A"
    burn: str = "#4A8FE8"
    # Contrast Mask band on the Analysis chart.
    chart_mask: str = "#AF8CFF"
    # Film-mode chips: orange mask, silver grey, slide blue.
    mode_c41: str = "#E08A3C"
    mode_bw: str = "#8C8C8C"
    mode_e6: str = "#4FB0D8"

    # Canvas background swatches, equal CIE L* steps from black to white.
    canvas_bg_black: str = "#070707"
    canvas_bg_dark_grey: str = "#3A3A3A"
    canvas_bg_mid_grey: str = "#6F6F6F"
    canvas_bg_light_grey: str = "#AAAAAA"
    canvas_bg_white: str = "#E8E8E8"
    # The swatch a new user starts on, an index into canvas/toolbar.CANVAS_COLORS: Dark Gray, Light Gray by day.
    canvas_bg_default: int = 1

    # Status semantic
    status_success: str = "#33AD83"

    sidebar_expanded_defaults: Dict[str, bool] = field(
        default_factory=lambda: {
            "analysis": True,
            "baseline": True,
            "process": False,
            "color": True,
            "tone": True,
            "paper": True,
            "geometry": True,
            "autocrop": True,
            "optics": False,
            "assembly": False,
            "lab": True,
            "retouch": True,
        }
    )


THEME = ThemeConfig()

# Day: a cream ground, a film-base orange accent and black text. Semantic text colors go darker to
# keep 4.5:1 on cream; the slider takes a darker orange to keep 3:1 against its track.
DAY_COLORS: Dict[str, str] = {
    "bg_dark": "#F3EDE0",
    "bg_panel": "#F3EDE0",
    "bg_input": "#E9E1D0",
    "bg_card": "#FBF7EE",
    "bg_header": "#E6DECC",
    "bg_selected": "#D6CCB6",
    "bg_hover": "#DCD3BF",
    "bg_menu_selected": "#CFC4AC",
    "bg_checked": "#EBD6BC",
    "bg_checked_hover": "#E3C8A6",
    "border_checked": "#A65A26",
    "border_checked_hover": "#C8743A",
    "bg_primary": "#C8743A",
    "bg_primary_hover": "#D4844C",
    "border_scope_frame": "#B08A4A",
    "mark_edited": "#A87A1E",
    "progress_fill": "#C8743A",
    "bg_accent_muted": "#E2D6C2",
    "border_input": "#DDD3BF",
    "border_primary": "#D3C8B2",
    "border_color": "#C4B8A0",
    "border_hover": "#B0A48C",
    "border_focus": "#6F675A",
    "border_indicator": "#8E8676",
    "slider_disabled": "#B4AA96",
    "slider_handle": "#A65A26",
    "slider_fill": "#A65A26",
    "text_on_accent": "#141210",
    "text_primary": "#141210",
    "text_secondary": "#3B362E",
    "text_hint": "#5F574B",
    "text_muted": "#A39A88",
    "text_unit": "#6F675A",
    "warn_amber": "#7C5913",
    "error": "#C62828",
    "error_text": "#B3261E",
    "status_success": "#1A6D50",
    "channel_red_text": "#BA2525",
    "channel_green_text": "#286D2B",
    "channel_blue_text": "#1460B8",
    "surface_reveal_flash": "rgba(200, 116, 58, 0.30)",
    "surface_hover_faint": "#0C000000",
    "surface_overlay": "rgba(243,237,224,0.92)",
    "header_veil": "rgba(230,222,204,0.55)",
    "header_veil_hover": "rgba(214,204,182,0.62)",
    "surface_overlay_hover": "rgba(214,204,182,0.92)",
}
APPEARANCES = ("night", "day")


def apply_appearance(name: str) -> None:
    """Sets THEME to the saved appearance ("night" or "day"). Call it before any view module
    imports: modules read THEME into stylesheets and constants at import."""
    if name == "day":
        for key, value in DAY_COLORS.items():
            # THEME is frozen against stray edits; this is the one sanctioned change, at startup.
            object.__setattr__(THEME, key, value)
        object.__setattr__(THEME, "canvas_bg_default", 4)


# Scene marks cycle through existing tokens; red is left out because it reads as an error or the selection mat.
SCENE_COLORS = (THEME.channel_blue, THEME.status_success, THEME.warn_amber, THEME.filter_magenta, THEME.filter_cyan, THEME.mode_c41)


def scene_color(ordinal: int) -> str:
    return SCENE_COLORS[(ordinal - 1) % len(SCENE_COLORS)]
