"""Baryta's Combined card layout: a card holds controls from another config section.

Color holds Saturation and its rail, Print Look holds the Alternative Processes. A moved control
takes its section's Reset, edited count and held-eye compare to the card that shows it. Apply to
Frames and Copy Card Settings keep NegPy's sections.
"""

from dataclasses import replace

from PyQt6.QtWidgets import QSpacerItem, QVBoxLayout, QWidget

from negpy.desktop.settings_catalog import unused_in_mode
from negpy.desktop.view.sidebar.baryta_layout import _take
from negpy.desktop.view.widgets.fold import group_fold
from negpy.kernel.system.config import DEFAULT_WORKSPACE_CONFIG
from negpy.kernel.system.i18n import tr

CARD_LAYOUT_SETTING = "baryta_card_layout"
CARD_LAYOUTS = ("classic", "combined")
_LAB_FIELDS = ("saturation", "skin_protection", "chroma_denoise")


def is_combined(repo) -> bool:
    return repo.get_global_setting(CARD_LAYOUT_SETTING, "classic") == "combined"


def combine_cards(panel) -> None:
    _color_takes_saturation(panel)
    _print_look_takes_alt_process(panel)
    _move_reset_and_compare(panel)
    _move_counts(panel)


def _color_takes_saturation(panel) -> None:
    color, lab = panel.color_sidebar, panel.lab_sidebar
    column = QWidget.layout(color.color_block)
    at = column.indexOf(color.cast_removal_slider) + 1
    # The rail's chevron sits in Saturation's row, so the two move together.
    for offset, widget in enumerate((lab.saturation_slider, lab.chroma_fold)):
        _take(widget)
        column.insertWidget(at + offset, widget)
    filters = (color.cyan_slider, color.magenta_slider, color.yellow_slider)
    for slider in filters:
        _take(slider)
    header, fold = group_fold("baryta_color_balance", "Filtration", *filters)
    fold.bind(panel.controller.session.repo)
    column.addLayout(header)
    column.addWidget(fold)
    section = panel.color_section
    section._title_text = tr("Color")
    section.set_modified(section.modified_count)


def _print_look_takes_alt_process(panel) -> None:
    card = panel.altproc_section
    _take(panel.altproc_sidebar)
    header, fold = group_fold("baryta_alt_process", "Alternative Processes", panel.altproc_sidebar)
    fold.bind(panel.controller.session.repo)
    box = QWidget()
    rows = QVBoxLayout(box)
    rows.setContentsMargins(0, 0, 0, 0)
    rows.setSpacing(0)
    rows.addLayout(header)
    rows.addWidget(fold)
    layout = panel.paper_sidebar.layout
    end = layout.count() - (1 if isinstance(layout.itemAt(layout.count() - 1), QSpacerItem) else 0)
    layout.insertWidget(end, box)
    # NegPy's rules for when the card applies now show or hide the fold; the card stays hidden.
    card.native_set_visible = lambda _on: None
    card.setVisible = box.setVisible
    QWidget.setVisible(card, False)  # hide() would reach the instance's setVisible
    box.setVisible(getattr(card, "wanted_visible", True))


def _move_reset_and_compare(panel) -> None:
    """Reset gives the defaults the held eye shows, so both come from one place."""
    native = panel._card_off_config
    lab_default = DEFAULT_WORKSPACE_CONFIG.lab

    def card_off_config(key: str):
        cfg = native(key)
        if key == "color":
            return replace(cfg, lab=replace(cfg.lab, **{f: getattr(lab_default, f) for f in _LAB_FIELDS}))
        if key == "lab":
            now = panel.controller.state.config.lab
            return replace(cfg, lab=replace(cfg.lab, **{f: getattr(now, f) for f in _LAB_FIELDS}))
        if key == "paper":
            return replace(cfg, altproc=DEFAULT_WORKSPACE_CONFIG.altproc)
        return cfg

    panel._card_off_config = card_off_config
    session = panel.controller.session
    for key in ("color", "lab", "paper"):
        section = getattr(panel, f"{key}_section")
        section.reset_requested.disconnect()
        section.reset_requested.connect(lambda k=key: session.update_config(panel._card_off_config(k), persist=True))


def _lab_moved_count(cfg) -> int:
    """The Detail card's edited count for the fields Color took. Mirrors ControlsPanel._sync_modified_dots."""
    lab, base = cfg.lab, DEFAULT_WORKSPACE_CONFIG.lab
    saturated = lab.saturation != base.saturation
    return sum(
        [
            saturated and not unused_in_mode("lab", "saturation", cfg),
            lab.skin_protection != base.skin_protection and saturated and not unused_in_mode("lab", "skin_protection", cfg),
            lab.chroma_denoise != base.chroma_denoise and not unused_in_mode("lab", "chroma_denoise", cfg),
        ]
    )


def _move_counts(panel) -> None:
    color, lab, paper, alt = panel.color_section, panel.lab_section, panel.paper_section, panel.altproc_section
    native_color, native_lab, native_paper, native_alt = color.set_modified, lab.set_modified, paper.set_modified, alt.set_modified

    def moved() -> int:
        return _lab_moved_count(panel.controller.state.config)

    color.set_modified = lambda n: native_color(n + moved())
    lab.set_modified = lambda n: native_lab(max(0, n - moved()))
    # NegPy counts Print Look before the Alternative Processes, so each one sets the sum.
    paper.own_count = paper.modified_count

    def set_paper(n: int) -> None:
        paper.own_count = n
        native_paper(n + alt.modified_count)

    def set_alt(n: int) -> None:
        native_alt(n)
        native_paper(paper.own_count + n)

    paper.set_modified = set_paper
    alt.set_modified = set_alt
