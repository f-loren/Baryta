from types import SimpleNamespace

from conftest import FakeController, FakeRepo
from negpy.desktop.view.sidebar.baryta_column import apply_column_layout


def _column():
    from negpy.desktop.view.sidebar.right_panel import RightPanel

    right = RightPanel(FakeController(FakeRepo()))
    apply_column_layout(right)
    return right


def _shown_group(right) -> str:
    return right._group_keys[right.group_stack.currentIndex()]


def test_develop_holds_setup_and_roll_settings_over_the_frame_tabs(qapp) -> None:
    right = _column()
    cp = right.controls_panel
    assert right.group_switcher.isHidden()
    develop = right.group_stack.widget(right._group_keys.index("frame"))
    for widget in (cp.film_section, right.roll_section, cp.presets_section, right.switcher, right.stack):
        assert develop.isAncestorOf(widget)
    for card in (cp.baseline_section, cp.process_section, cp.fade_section, cp.assembly_section, cp.optics_section):
        assert right.roll_section.isAncestorOf(card)
    assert not right.roll_section.isAncestorOf(cp.film_section)


def test_the_roll_tab_and_a_roll_card_open_develop(qapp) -> None:
    right = _column()
    right.show_tab_by_key("scan")
    right.show_tab_by_key("roll")
    assert _shown_group(right) == "frame"
    right.roll_section.set_expanded(False)
    right.show_tab_by_key("scan")
    right.reveal_widget(right.controls_panel.fade_section)
    assert _shown_group(right) == "frame" and right.roll_section.toggle_button.isChecked()


def test_export_and_metadata_open_behind_the_back_row(qapp) -> None:
    from negpy.desktop.view.widgets.baryta_top_bar import BarytaTopBar

    right = _column()
    header = right.view_choice.parentWidget()
    right.show_tab_by_key("frame")
    assert header.isHidden()
    bar = BarytaTopBar(SimpleNamespace(controller=right.controller, right_panel=right))
    bar.export_btn.click()
    assert _shown_group(right) == "export" and not header.isHidden()
    right.view_choice.setCurrentIndex(right.view_choice.findData("metadata"))
    assert _shown_group(right) == "metadata"


def _height(widget, width: int = 400) -> int:
    return widget.heightForWidth(width) if widget.hasHeightForWidth() else widget.sizeHint().height()


def test_the_frame_tabs_take_the_height_of_the_tab_in_front(qapp) -> None:
    right = _column()
    heights = set()
    for i in range(right.stack.count()):
        right._switch_tab(i)
        heights.add(_height(right.stack))
        assert _height(right.stack) == _height(right.stack.currentWidget()) + right.stack.contentsMargins().top()
    assert len(heights) > 1


def test_card_headers_keep_only_name_and_chevron_until_pointed_at(qapp) -> None:
    from negpy.desktop.view.sidebar.baryta_column import PANEL_WIDTH

    right = _column()
    section = right.controls_panel.film_section
    assert section.icon_label is None or section.icon_label.isHidden()
    assert section.info_btn.graphicsEffect().opacity() == 0.0
    assert section.reset_btn.graphicsEffect() is None
    toggle = section.add_header_toggle("fa5s.eye", "A tool")
    toggle.setChecked(True)
    assert toggle.graphicsEffect().opacity() == 1.0
    assert right.sizeHint().width() == max(PANEL_WIDTH, right.minimumSizeHint().width())


def test_setup_shows_its_choices_without_the_notes(qapp) -> None:
    from negpy.desktop.view.sidebar.scan_setup import ScanSetupSidebar

    setup = _column().findChild(ScanSetupSidebar)
    setup.hint.setVisible(True)
    assert setup.hint.isHidden()
