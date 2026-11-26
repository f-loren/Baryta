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


def test_the_top_bar_crop_opens_crop_and_straighten_in_place_of_the_column(qapp) -> None:
    from negpy.desktop.view.sidebar.baryta_column import CROP_TAB
    from negpy.desktop.view.widgets.baryta_top_bar import BarytaTopBar

    right = _column()
    crop = right.crop_view
    draw = right.controls_panel.autocrop_sidebar.manual_crop_btn
    bar = BarytaTopBar(SimpleNamespace(controller=right.controller, right_panel=right))
    assert right._tab_buttons[right._tab_keys.index(CROP_TAB)] not in right.switcher.buttons
    right.show_tab_by_key("frame")
    right._switch_tab(right._tab_keys.index("color"))
    bar.crop_btn.click()
    assert crop.is_open and bar.crop_btn.isChecked() and draw.isChecked()
    assert right.stack.currentIndex() == right._tab_keys.index(CROP_TAB)
    assert right.switcher.isHidden() and not right.controls_panel.film_section.isVisibleTo(right)
    draw.toggle()
    assert not crop.is_open and not bar.crop_btn.isChecked()
    assert right.stack.currentIndex() == right._tab_keys.index("color") and not right.switcher.isHidden()
    bar.crop_btn.click()
    bar.crop_btn.click()
    assert not crop.is_open and not bar.crop_btn.isChecked() and not draw.isChecked()


def test_a_crop_card_jump_or_the_draw_tool_opens_crop_and_another_tab_or_page_closes_it(qapp) -> None:
    right = _column()
    crop = right.crop_view
    right.show_tab_by_key("frame")
    right.reveal_widget(right.controls_panel.geometry_section)
    assert crop.is_open
    right.reveal_widget(right.controls_panel.presets_section)
    assert not crop.is_open
    right.controls_panel.autocrop_sidebar.manual_crop_btn.toggle()
    assert crop.is_open
    right.show_tab_by_key("scan")
    assert not crop.is_open and not right.controls_panel.autocrop_sidebar.manual_crop_btn.isChecked()


def test_crop_and_straighten_stay_open_when_level_takes_over_from_draw(qapp) -> None:
    from negpy.desktop.session import ToolMode

    right = _column()
    draw = right.controls_panel.autocrop_sidebar.manual_crop_btn
    right.show_tab_by_key("frame")
    draw.toggle()
    right.controller.state.active_tool = ToolMode.STRAIGHTEN
    draw.toggle()
    assert right.crop_view.is_open


def test_the_top_bar_crop_opens_develop_from_another_page(qapp) -> None:
    from negpy.desktop.view.widgets.baryta_top_bar import BarytaTopBar

    right = _column()
    bar = BarytaTopBar(SimpleNamespace(controller=right.controller, right_panel=right))
    bar.export_btn.click()
    bar.crop_btn.click()
    assert _shown_group(right) == "frame" and right.crop_view.is_open


def test_a_refused_crop_leaves_crop_and_straighten_closed(qapp) -> None:
    right = _column()
    draw = right.controls_panel.autocrop_sidebar.manual_crop_btn
    right.show_tab_by_key("frame")
    draw.toggled.connect(lambda on: on and draw.setChecked(False))
    draw.toggle()
    assert not right.crop_view.is_open
