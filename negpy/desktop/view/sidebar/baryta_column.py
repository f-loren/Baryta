"""Layout A: the top bar's phases pick the page, so the right panel shows one column and no tabs.

Develop holds the Roll tab's cards above the Frame tabs in one scroll: Setup leads as the film
card, the other roll cards fold into the Roll card, then Presets and the Frame tabs. The Roll tab
opens the top of that column. Crop and Straighten, Export and Metadata open behind a back row.
Every card stays NegPy's own; this module only moves widgets after RightPanel builds them, so an upstream merge
keeps its own layout code.
"""

from PyQt6.QtCore import QEvent, QObject, QSize, pyqtSignal
from PyQt6.QtWidgets import (
    QAbstractButton,
    QGraphicsOpacityEffect,
    QHBoxLayout,
    QScrollArea,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from negpy.desktop.session import ToolMode
from negpy.desktop.view.styles.templates import icon_button, section_subheader
from negpy.desktop.view.styles.theme import THEME
from negpy.desktop.view.sidebar.scan_setup import ScanSetupSidebar
from negpy.desktop.view.widgets.collapsible import CollapsibleSection, make_section
from negpy.desktop.view.widgets.overflow_bar import OverflowBar
from negpy.desktop.view.widgets.segmented_choice import SegmentedChoice
from negpy.desktop.view.widgets.tab_header import TabHeader
from negpy.kernel.system.i18n import tr

ROLL_KEY = "baryta_roll"
# Groups that open behind the back row, in its choice order.
VIEW_GROUPS = ("export", "metadata")
# The panel's first width, before the user drags it; the cards fit down to RightPanel's minimum.
PANEL_WIDTH = 380
# The Frame tab that the top bar's Crop opens instead of a tab of its own.
CROP_TAB = "geometry"


def apply_column_layout(right) -> None:
    keys = right._group_keys
    right.group_switcher.hide()
    _build_develop_column(right)
    _cap_width(right)
    for section in right.findChildren(CollapsibleSection):
        # A tab's header row is a toolbar, so its tracks stay in view.
        if not isinstance(section, TabHeader):
            _quiet_header(section)
    for setup in right.findChildren(ScanSetupSidebar):
        # Its notes restate the choices above them; refresh() would show them again.
        setup.hint.hide()
        setup.hint.setVisible = lambda _visible: None
    header = _view_header(right)
    native_switch = right._switch_group

    def switch_group(index: int) -> None:
        if keys[index] == "roll":
            index = keys.index("frame")
            right.develop_scroll.verticalScrollBar().setValue(0)
        if keys[index] != "frame":
            right.crop_view.close()
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

    _drop_crop_tab(right)

    edit = QWidget()
    edit_layout = QVBoxLayout(edit)
    edit_layout.setContentsMargins(0, 0, 0, 0)
    edit_layout.setSpacing(0)
    edit_layout.addWidget(right.switcher)
    edit_layout.addWidget(right.stack)

    browse = QWidget()
    browse_layout = QVBoxLayout(browse)
    browse_layout.setContentsMargins(0, 0, 0, 0)
    browse_layout.setSpacing(THEME.space_lg)
    for widget in (cp.film_section, actions, right.roll_section, cp.presets_section):
        browse_layout.addWidget(widget)

    back = icon_button("fa5s.chevron-left", tr("Back to Develop"))
    crop_header = QWidget()
    row = QHBoxLayout(crop_header)
    row.setContentsMargins(0, 0, 0, 0)
    row.setSpacing(THEME.space_sm)
    row.addWidget(back)
    row.addWidget(section_subheader(tr("Crop and Straighten")), 1)

    column = QWidget()
    col = QVBoxLayout(column)
    col.setContentsMargins(0, 0, 0, 0)
    col.setSpacing(THEME.space_lg)
    for widget in (browse, crop_header, edit):
        col.addWidget(widget)
    col.addStretch(1)
    right.develop_scroll = QScrollArea()
    right.develop_scroll.setWidgetResizable(True)
    right.develop_scroll.setWidget(column)
    page_layout.addWidget(right.develop_scroll, 1)

    right.crop_view = _CropView(right, browse, crop_header)
    back.clicked.connect(right.crop_view.close)


class _CropFreeBar(OverflowBar):
    """The Frame tab bar without the crop tab. It takes the stack's indices, as RightPanel pins by them."""

    def __init__(self, crop: int, **kwargs) -> None:
        super().__init__(**kwargs)
        self._crop = crop

    def set_pinned(self, button_index: int) -> None:
        if button_index == self._crop:
            button_index = -1
        elif button_index > self._crop:
            button_index -= 1
        super().set_pinned(button_index)


def _drop_crop_tab(right) -> None:
    old = right.switcher
    crop = right._tab_keys.index(CROP_TAB)
    bar = _CropFreeBar(crop, height=old.height(), min_item=old.minimumSizeHint().width() - OverflowBar.OVERFLOW_W)
    for i, (button, label) in enumerate(zip(old.buttons, right._tab_tooltips)):
        if i == crop:
            # RightPanel still checks it on every switch.
            button.setParent(bar)
            button.hide()
        else:
            bar.add_button(button, label)
    old.deleteLater()
    right.switcher = bar


class _CropView(QObject):
    """Crop and Straighten in place of the column, opened by the top bar's Crop, Draw or a jump to
    one of its cards. It closes when Draw ends with no tool after it, on the back row, another tab
    or another page; closing ends Draw, and the top bar's Crop opens it with Draw on."""

    changed = pyqtSignal(bool)

    def __init__(self, right, browse: QWidget, header: QWidget) -> None:
        super().__init__(right)
        self._right = right
        self._browse, self._header = browse, header
        self._crop = right._tab_keys.index(CROP_TAB)
        self._return = right._active_index if right._active_index != self._crop else right._tab_keys.index("tone")
        self._draw = right.controls_panel.autocrop_sidebar.manual_crop_btn
        self.is_open = False
        native_tab = right._switch_tab

        def switch_tab(index: int) -> None:
            if index != self._crop:
                self._return = index
            native_tab(index)
            self._show(index == self._crop)

        right._switch_tab = switch_tab
        native_reveal = right.reveal_widget

        def reveal_widget(widget: QWidget) -> None:
            if browse.isAncestorOf(widget):
                self.close()
            native_reveal(widget)

        right.reveal_widget = reveal_widget
        self._draw.toggled.connect(self._follow_draw)
        self._show(False)
        if right._active_index == self._crop:
            switch_tab(self._return)

    def open(self) -> None:
        if not self.is_open:
            self._right.show_tab_by_key(CROP_TAB)

    def close(self) -> None:
        if self.is_open:
            self._right._switch_tab(self._return)

    def _follow_draw(self, _on: bool) -> None:
        # The button, not the argument: a refused crop unchecks it inside this same emission.
        # Draw also turns off when Level or Draw Lines takes over, and the view stays for them.
        if self._draw.isChecked():
            self.open()
        elif self._right.controller.state.active_tool == ToolMode.NONE:
            self.close()

    def toggle(self) -> None:
        """The top bar's Crop: the view with the crop tool on, or back to the tabs."""
        if self.is_open:
            self.close()
            return
        self.open()
        if not self._draw.isChecked():
            self._draw.toggle()

    def _show(self, on: bool) -> None:
        right = self._right
        self._browse.setVisible(not on)
        right.switcher.setVisible(not on)
        self._header.setVisible(on)
        if on == self.is_open:
            return
        self.is_open = on
        right.develop_scroll.verticalScrollBar().setValue(0)
        if not on and self._draw.isChecked():
            self._draw.toggle()
        self.changed.emit(on)


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


class _WidthHint(QWidget):
    """Holds the panel's body and asks for PANEL_WIDTH, so the widest page does not set the first width."""

    def sizeHint(self) -> QSize:  # noqa: N802
        return QSize(max(PANEL_WIDTH, self.minimumSizeHint().width()), super().sizeHint().height())


def _cap_width(right) -> None:
    holder = _WidthHint()
    box = QVBoxLayout(holder)
    box.setContentsMargins(0, 0, 0, 0)
    right.layout().replaceWidget(right.splitter, holder)
    box.addWidget(right.splitter)


class _HeaderHover(QObject):
    """Shows a card header's action icons while the pointer or focus is on the header. A checked
    toggle stays in view, as it reports a state; the scope pair's stripe already reports its own.
    Reset and the roll revert appear only on an edited card, so they stay as they are."""

    def __init__(self, section: CollapsibleSection) -> None:
        super().__init__(section)
        self._section = section
        self._header = section.toggle_button
        self._effects: dict[QAbstractButton, QGraphicsOpacityEffect] = {}
        self._header.installEventFilter(self)
        for button in self._header.findChildren(QAbstractButton):
            self._add(button)
        self.refresh()

    def _add(self, button: QAbstractButton) -> None:
        s = self._section
        if button in self._effects or button in (s.reset_btn, s.roll_revert_btn, s.select_box):
            return
        effect = QGraphicsOpacityEffect(button)
        button.setGraphicsEffect(effect)
        self._effects[button] = effect
        button.installEventFilter(self)
        button.toggled.connect(lambda _on: self.refresh())

    def refresh(self) -> None:
        shown = self._header.underMouse() or any(b.hasFocus() for b in self._effects)
        scope = (self._section.frame_btn, self._section.roll_btn)
        for button, effect in self._effects.items():
            lit = button.isChecked() and button not in scope
            effect.setOpacity(1.0 if shown or lit else 0.0)

    def eventFilter(self, obj, event) -> bool:  # noqa: N802
        # The garbage collector can clear this wrapper while Qt still sends it teardown events.
        if not self.__dict__:
            return False
        kind = event.type()
        if obj is self._header and kind == QEvent.Type.ChildAdded and isinstance(event.child(), QAbstractButton):
            # Header buttons a card adds after the build, such as the scope pair.
            self._add(event.child())
            self.refresh()
        elif kind in (QEvent.Type.Enter, QEvent.Type.Leave, QEvent.Type.FocusIn, QEvent.Type.FocusOut):
            self.refresh()
        return False


def _quiet_header(section: CollapsibleSection) -> None:
    """A card header shows its name and chevron; its action icons wait for the pointer."""
    if section.icon_label is not None:
        section.icon_label.hide()
    _HeaderHover(section)
