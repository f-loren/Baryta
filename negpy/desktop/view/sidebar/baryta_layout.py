"""Baryta's grouping of the per-frame cards into Frame tabs.

The cards stay NegPy's own; only this table says which tab holds which card, so an upstream merge
touches one place. A tab key keeps its upstream name where the tab keeps its job, because shortcuts
and the saved tab resolve by key.
"""

from PyQt6.QtCore import Qt

from negpy.desktop.view.styles.templates import section_subheader
from negpy.kernel.system.i18n import tr


def frame_tabs() -> list[tuple[str, str, list[str]]]:
    """(key, title, card section attributes on ControlsPanel), in tab order."""
    return [
        ("geometry", tr("Geometry"), ["autocrop_section", "geometry_section"]),
        ("color", tr("Color"), ["color_section"]),
        ("tone", tr("Tone"), ["tone_section", "paper_section"]),
        ("finish", tr("Finish"), ["lab_section", "toning_section", "finish_section", "altproc_section"]),
        ("retouch", tr("Retouch"), ["retouch_section", "local_section"]),
    ]


# Cards Base mode hides. A card that holds a setting stays in view, so Base never hides an edit.
ADVANCED_CARDS = (
    "paper_section",
    "toning_section",
    "altproc_section",
    "process_section",
    "fade_section",
    "assembly_section",
    "demosaic_section",
    "optics_section",
    "sensor_section",
)
ADVANCED_SETTING = "baryta_advanced"
# The Roll tab's cards set once per scanning rig, under one sub-header at the bottom.
RIG_CARDS = ("demosaic_section", "optics_section", "sensor_section")


def add_rig_cards(panel, layout) -> None:
    """Add the sub-header and RIG_CARDS to the Roll tab; the sub-header shows while one card does."""
    panel.rig_header = section_subheader(tr("Scanner Setup"))
    layout.addWidget(panel.rig_header)
    for attr in RIG_CARDS:
        layout.addWidget(getattr(panel, attr))
    apply_mode(panel)


def install_mode_gate(panel) -> None:
    """Put Base mode in front of each Advanced card's setVisible. NegPy's own rules still decide when
    a card applies; the gate only adds Base mode on top, so it needs no copy of those rules."""
    panel.advanced_mode = bool(panel.controller.session.repo.get_global_setting(ADVANCED_SETTING, False))
    for attr in ADVANCED_CARDS:
        section = getattr(panel, attr)
        # A card not yet in a layout reads as hidden; only an explicit hide counts.
        explicit = section.testAttribute(Qt.WidgetAttribute.WA_WState_ExplicitShowHide)
        section.wanted_visible = not (explicit and section.isHidden())
        section.native_set_visible = section.setVisible

        def set_visible(on: bool, section=section) -> None:
            section.wanted_visible = on
            section.native_set_visible(on and _allowed(panel, section))

        section.setVisible = set_visible
    panel.modified_synced.connect(lambda: apply_mode(panel))
    apply_mode(panel)


def _allowed(panel, section) -> bool:
    return panel.advanced_mode or section.modified_count > 0


def _apply(panel, section) -> None:
    if section.parent() is None:
        return  # Showing a card outside a layout opens it as a window; it applies once placed.
    section.native_set_visible(section.wanted_visible and _allowed(panel, section))


def apply_mode(panel) -> None:
    for attr in ADVANCED_CARDS:
        _apply(panel, getattr(panel, attr))
    if header := getattr(panel, "rig_header", None):
        header.setVisible(any(not getattr(panel, a).isHidden() for a in RIG_CARDS))


def set_advanced_mode(panel, on: bool) -> None:
    panel.advanced_mode = on
    panel.controller.session.repo.save_global_setting(ADVANCED_SETTING, on)
    apply_mode(panel)
