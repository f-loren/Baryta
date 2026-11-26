"""Layout A: the top bar's phases pick the page, so the right panel shows one column and no tabs.

Develop holds the Roll tab's cards above the Frame tabs in one scroll: Setup leads as the film
card, the other roll cards fold into the Roll card, then Presets and the Frame tabs. The Roll tab
opens the top of that column. Export and Metadata open behind a back row. Every card stays
NegPy's own; this module only moves widgets after RightPanel builds them, so an upstream merge
keeps its own layout code.
"""

from PyQt6.QtCore import QSize
from PyQt6.QtWidgets import QHBoxLayout, QScrollArea, QStackedWidget, QVBoxLayout, QWidget

from negpy.desktop.view.styles.templates import icon_button
from negpy.desktop.view.styles.theme import THEME
from negpy.desktop.view.widgets.collapsible import make_section
from negpy.desktop.view.widgets.segmented_choice import SegmentedChoice
from negpy.kernel.system.i18n import tr

ROLL_KEY = "baryta_roll"
# Groups that open behind the back row, in its choice order.
VIEW_GROUPS = ("export", "metadata")


def apply_column_layout(right) -> None:
    keys = right._group_keys
    right.group_switcher.hide()
    _build_develop_column(right)
    header = _view_header(right)
    native_switch = right._switch_group

    def switch_group(index: int) -> None:
        if keys[index] == "roll":
            index = keys.index("frame")
            right.develop_scroll.verticalScrollBar().setValue(0)
        native_switch(index)
        key = keys[index]
        header.setVisible(key in VIEW_GROUPS)
        if key in VIEW_GROUPS:
            right.view_choice.blockSignals(True)
            right.view_choice.setCurrentIndex(right.view_choice.findData(key))
            right.view_choice.blockSignals(False)

    right._switch_group = switch_group
    switch_group(right._active_group)


def _build_develop_column(right) -> None:
    cp = right.controls_panel
    keys = right._group_keys
    roll_body = right.group_stack.widget(keys.index("roll")).takeWidget()
    roll_body.layout().removeWidget(cp.film_section)
    right.roll_section = make_section(right.controller.session.repo, tr("Roll"), ROLL_KEY, roll_body, "mdi6.filmstrip")

    page_layout = right.group_stack.widget(keys.index("frame")).layout()
    actions = page_layout.itemAt(0).widget()
    for widget in (actions, right.switcher, right.stack):
        page_layout.removeWidget(widget)
    _fit_stack(right)
    right._switch_tab(right._active_index)

    edit = QWidget()
    edit_layout = QVBoxLayout(edit)
    edit_layout.setContentsMargins(0, 0, 0, 0)
    edit_layout.setSpacing(0)
    edit_layout.addWidget(right.switcher)
    edit_layout.addWidget(right.stack)

    column = QWidget()
    col = QVBoxLayout(column)
    col.setContentsMargins(0, 0, 0, 0)
    col.setSpacing(THEME.space_lg)
    for widget in (cp.film_section, actions, right.roll_section, cp.presets_section, edit):
        col.addWidget(widget)
    col.addStretch(1)
    right.develop_scroll = QScrollArea()
    right.develop_scroll.setWidgetResizable(True)
    right.develop_scroll.setWidget(column)
    page_layout.addWidget(right.develop_scroll, 1)


class _FitStack(QStackedWidget):
    """Sized to the page in front. QStackedLayout sizes to its largest page, and its
    heightForWidth asks every page, so a short tab would scroll over the tallest one's height."""

    def _margins(self) -> QSize:
        m = self.contentsMargins()
        return QSize(m.left() + m.right(), m.top() + m.bottom())

    def sizeHint(self) -> QSize:  # noqa: N802
        page = self.currentWidget()
        return (page.sizeHint() if page else QSize(0, 0)) + self._margins()

    def minimumSizeHint(self) -> QSize:  # noqa: N802
        page = self.currentWidget()
        return (page.minimumSizeHint() if page else QSize(0, 0)) + self._margins()

    def hasHeightForWidth(self) -> bool:  # noqa: N802
        page = self.currentWidget()
        return page is not None and page.hasHeightForWidth()

    def heightForWidth(self, width: int) -> int:  # noqa: N802
        if not self.hasHeightForWidth():
            return -1
        margins = self._margins()
        return self.currentWidget().heightForWidth(width - margins.width()) + margins.height()


def _fit_stack(right) -> None:
    """Move each Frame tab out of its own scroll area into a _FitStack, since the column scrolls them all."""
    old = right.stack
    stack = _FitStack()
    stack.setContentsMargins(old.contentsMargins())
    while old.count():
        scroll = old.widget(0)
        old.removeWidget(scroll)
        stack.addWidget(scroll.takeWidget())
        scroll.deleteLater()
    old.deleteLater()
    stack.currentChanged.connect(lambda _i: stack.updateGeometry())
    right.stack = stack


def _view_header(right) -> QWidget:
    """Back to Develop, and the choice between Export and Metadata, over those two pages."""
    back = icon_button("fa5s.chevron-left", tr("Back to Develop"))
    back.clicked.connect(lambda: right.show_tab_by_key("frame"))
    right.view_choice = SegmentedChoice(
        (("mdi6.export-variant", tr("Export")), ("mdi6.tag-outline", tr("Metadata"))),
        tr("The export settings, or the metadata written with the frame"),
        data=VIEW_GROUPS,
    )
    right.view_choice.currentChanged.connect(lambda _i: right.show_tab_by_key(right.view_choice.currentData()))
    header = QWidget()
    row = QHBoxLayout(header)
    row.setContentsMargins(0, 0, 0, THEME.space_sm)
    row.setSpacing(THEME.space_sm)
    row.addWidget(back)
    row.addWidget(right.view_choice, 1)
    right.layout().insertWidget(1, header)
    return header
