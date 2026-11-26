"""Baryta's grouping of the per-frame cards into Frame tabs, and its order inside them.

The cards stay NegPy's own; only this table says which tab holds which card, so an upstream merge
touches one place. A tab key keeps its upstream name where the tab keeps its job, because shortcuts
and the saved tab resolve by key. arrange_cards moves controls only inside their own card, so each
card's Reset, edited marks and roll values still cover what it shows.
"""

from PyQt6.QtCore import QEvent, QObject, Qt
from PyQt6.QtWidgets import QHBoxLayout, QLabel, QLayout, QVBoxLayout, QWidget

from negpy.desktop.view.styles.templates import labeled_action, labeled_toggle, section_subheader, tool_toggle_qss
from negpy.desktop.view.styles.theme import THEME
from negpy.desktop.view.widgets.fold import Fold
from negpy.kernel.system.i18n import tr


def frame_tabs() -> list[tuple[str, str, list[str]]]:
    """(key, title, card section attributes on ControlsPanel), in tab order."""
    return [
        ("geometry", tr("Geometry"), ["autocrop_section", "geometry_section"]),
        ("color", tr("Color"), ["color_section"]),
        ("tone", tr("Tone"), ["tone_section"]),
        ("finish", tr("Finish"), ["paper_section", "altproc_section", "lab_section", "toning_section", "finish_section"]),
        ("retouch", tr("Retouch"), ["retouch_section", "local_section"]),
    ]


# Cards Base mode hides. A card that holds a setting stays in view, so Base never hides an edit.
# A one-card tab has no header; Tone keeps one for Pick Better.
HEADED_TABS = ("tone",)
ADVANCED_CARDS = (
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


def advanced_footer(panel) -> QWidget:
    """The Show Advanced toggle, pinned under the panel's tabs."""
    panel.advanced_btn = labeled_toggle(
        "fa5s.sliders-h", tr("Show Advanced"), panel.advanced_mode, tr("Show every card, not only the ones most rolls need")
    )
    panel.advanced_btn.toggled.connect(lambda on: set_advanced_mode(panel, on))
    footer = QWidget()
    row = QHBoxLayout(footer)
    row.setContentsMargins(THEME.space_sm, THEME.space_sm, THEME.space_sm, THEME.space_sm)
    row.addWidget(panel.advanced_btn)
    row.addStretch(1)
    return footer


def set_advanced_mode(panel, on: bool) -> None:
    panel.advanced_mode = on
    if btn := getattr(panel, "advanced_btn", None):
        btn.blockSignals(True)
        btn.setChecked(on)
        btn.blockSignals(False)
    panel.controller.session.repo.save_global_setting(ADVANCED_SETTING, on)
    apply_mode(panel)


def frame_actions(panel) -> QWidget:
    """Convert Roll and Apply to Roll over the Frame tabs: Roll Analysis's Reanalyze, and every
    Frame card in one Apply to Frames picker."""
    roll = panel.roll_sidebar
    panel.convert_btn = labeled_action(
        "fa5s.magic", tr("Convert Roll"), tr("Measure every frame and print the whole roll alike"), primary=True
    )
    panel.convert_btn.clicked.connect(panel.controller.request_batch_normalization)
    cards = tuple(attr.removesuffix("_section") for _key, _title, attrs in frame_tabs() for attr in attrs)
    panel.apply_roll_btn = labeled_action(
        "fa5s.clone", tr("Apply to Roll…"), tr("Copy this frame's settings to the selected frames or the whole roll")
    )
    panel.apply_roll_btn.clicked.connect(lambda: panel._apply_tab(cards))
    panel.convert_btn.setEnabled(roll.reanalyze_btn.isEnabled())
    panel.modified_synced.connect(lambda: panel.convert_btn.setEnabled(roll.reanalyze_btn.isEnabled()))
    row_widget = QWidget()
    row = QHBoxLayout(row_widget)
    row.setContentsMargins(0, 0, 0, THEME.space_sm)
    row.setSpacing(THEME.space_sm)
    row.addWidget(panel.convert_btn, 1)
    row.addWidget(panel.apply_roll_btn, 1)
    return row_widget


def arrange_cards(panel) -> None:
    _arrange_tone(panel.tone_sidebar)
    _arrange_paper(panel.paper_sidebar, panel.controller.session.repo)
    _quiet_lab(panel.lab_sidebar)


def _arrange_tone(tone) -> None:
    """Shadows and Highlights in view under Contrast; the channel choice and the split grades join
    Printing Aids behind one fold."""
    layout = tone.layout
    _drop_fold(_fold(tone, "tone_density"))
    at = layout.indexOf(tone.split_grade_fold)
    for offset, slider in enumerate((tone.shadow_density_slider, tone.highlight_density_slider), start=1):
        _take(slider)
        layout.insertWidget(at + offset, slider)
    _drop_fold(tone.split_grade_fold)
    aids = tone.aids_fold.content.layout()
    for slider in (tone.shadow_grade_slider, tone.highlight_grade_slider):
        _take(slider)
        aids.addWidget(slider)
    _take(tone.ch_btn)
    tone.darkroom_fold = _lead_fold(layout, tone.aids_fold, tone.ch_btn)
    auto = tone.auto_btn
    auto.setText(f" {tr('Auto')}")
    auto.setStyleSheet(tool_toggle_qss(icon_only=False))
    auto.setMinimumWidth(0)
    auto.setMaximumWidth(16777215)


def _arrange_paper(paper, repo) -> None:
    """Print Look shows the print stock and Dye Separation; the channel choice and the paper's ends
    join Curve Shape, which starts closed."""
    curve = _fold(paper, "paper_curve_shape")
    row = QHBoxLayout()
    for widget in (paper.ch_btn, paper.paper_black_btn, paper.paper_dmin_btn):
        _take(widget)
        row.addWidget(widget, 1 if widget is paper.ch_btn else 0)
    _drop_empty_rows(paper.layout)
    curve.content.layout().insertLayout(0, row)
    _reset_channel_on_close(curve, paper.ch_btn)
    if repo.get_global_setting(f"fold_{curve.key}") is None:
        curve.set_open(False)


def _quiet_lab(lab) -> None:
    """The card is Detail, so its COLOR and DETAIL sub-headers repeat what the title says."""
    detail = next(label for label in lab.findChildren(QLabel) if label.text() == tr("DETAIL"))
    for header in (lab.color_header, detail):
        header.hide()
        header.setVisible = lambda _visible: None


def _fold(sidebar, key: str) -> Fold:
    return next(fold for fold in sidebar.findChildren(Fold) if fold.key == key)


def _take(widget: QWidget) -> None:
    """Take widget out of whatever layout holds it, nested rows included."""

    def walk(layout: QLayout) -> bool:
        for i in range(layout.count()):
            item = layout.itemAt(i)
            if item.widget() is widget:
                layout.takeAt(i)
                return True
            if item.layout() is not None and walk(item.layout()):
                return True
        return False

    parent = widget.parentWidget()
    while parent is not None and not (QWidget.layout(parent) and walk(QWidget.layout(parent))):
        parent = parent.parentWidget()


def _drop_empty_rows(layout: QLayout) -> None:
    for i in reversed(range(layout.count())):
        row = layout.itemAt(i).layout()
        if row is not None and not any(row.itemAt(j).widget() for j in range(row.count())):
            layout.takeAt(i)


def _drop_fold(fold: Fold) -> None:
    """Retire a rail fold whose members moved out: its chevrons leave their rows and give the
    label its gutter back. The fold stays in its layout, hidden: a widget a layout lets go of is
    Python's to delete, and NegPy still holds this one."""
    for button in fold.buttons:
        anchor = button.parentWidget()
        _take(button)
        button.setParent(None)
        if anchor is not None:
            anchor.setProperty("fold_gutter", None)
    fold.buttons.clear()
    fold.content.removeEventFilter(fold)
    fold.hide()


def _lead_fold(layout: QLayout, fold: Fold, lead: QWidget) -> Fold:
    """fold again with lead above its content. NegPy hides the old content by mode (a slide), so the
    new fold shows while either part does."""
    body = QWidget()
    body.setObjectName("collapsible_content_body")
    col = QVBoxLayout(body)
    col.setContentsMargins(0, 0, 0, 0)
    col.setSpacing(THEME.space_xs)
    col.addWidget(lead)
    old = fold.content
    fold.content.removeEventFilter(fold)
    fold.button.toggled.disconnect(fold.set_open)
    fold.buttons.clear()
    fold.layout().removeWidget(old)
    col.addWidget(old)
    fold.hide()
    merged = Fold(fold.key, body, fold.button, default_open=fold._default_open)
    merged.set_open(fold.is_open())
    if fold._repo is not None:
        merged.bind(fold._repo)
    layout.insertWidget(layout.indexOf(fold), merged)
    _ShowWithParts(body, (lead, old))
    _reset_channel_on_close(merged, lead)
    return merged


class _ShowWithParts(QObject):
    """Shows body while any of parts shows, so an empty fold hides its chevron."""

    def __init__(self, body: QWidget, parts: tuple[QWidget, ...]) -> None:
        super().__init__(body)
        self._body, self._parts = body, parts
        for part in parts:
            part.installEventFilter(self)
        self._sync()

    def eventFilter(self, obj, event) -> bool:  # noqa: N802
        # The garbage collector can clear this wrapper while Qt still sends it teardown events.
        if not self.__dict__:
            return False
        if event.type() in (QEvent.Type.ShowToParent, QEvent.Type.HideToParent):
            self._sync()
        return False

    def _sync(self) -> None:
        self._body.setVisible(any(not part.isHidden() for part in self._parts))


def _reset_channel_on_close(fold: Fold, chooser) -> None:
    """A closed fold hides the channel choice, so the sliders in view go back to all channels."""
    for button in fold.buttons:
        button.toggled.connect(lambda open_: open_ or chooser.setCurrentIndex(0))
