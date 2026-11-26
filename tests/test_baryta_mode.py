from negpy.desktop.view.sidebar.baryta_layout import ADVANCED_SETTING, set_advanced_mode
from negpy.desktop.view.sidebar.controls_panel import ControlsPanel
from conftest import FakeController, FakeRepo


def test_base_mode_hides_an_unedited_advanced_card_and_keeps_an_edited_one(qapp) -> None:
    panel = ControlsPanel(FakeController(FakeRepo(**{ADVANCED_SETTING: False})))
    paper, toning = panel.paper_section, panel.toning_section
    assert paper.isHidden() and toning.isHidden()

    paper.set_modified(1)
    panel.modified_synced.emit()
    assert not paper.isHidden() and toning.isHidden()

    set_advanced_mode(panel, True)
    assert not toning.isHidden()
    assert panel.controller.session.repo.get_global_setting(ADVANCED_SETTING) is True


def test_the_gate_keeps_negpy_hiding_a_card_that_does_not_apply(qapp) -> None:
    panel = ControlsPanel(FakeController(FakeRepo(**{ADVANCED_SETTING: True})))
    panel.fade_section.setVisible(False)
    assert panel.fade_section.isHidden()
    set_advanced_mode(panel, False)
    set_advanced_mode(panel, True)
    assert panel.fade_section.isHidden()


def test_the_scanner_setup_header_shows_only_over_a_visible_rig_card(qapp) -> None:
    from negpy.desktop.view.sidebar.right_panel import RightPanel

    panel = RightPanel(FakeController(FakeRepo(**{ADVANCED_SETTING: False}))).controls_panel
    assert panel.rig_header.isHidden()
    panel.optics_section.set_modified(1)
    panel.optics_section.setVisible(True)
    panel.modified_synced.emit()
    assert not panel.rig_header.isHidden()


def test_show_advanced_switches_the_mode_and_follows_the_shortcut(qapp) -> None:
    from negpy.desktop.view.sidebar.right_panel import RightPanel

    panel = RightPanel(FakeController(FakeRepo(**{ADVANCED_SETTING: False}))).controls_panel
    panel.advanced_btn.setChecked(True)
    assert panel.advanced_mode and not panel.toning_section.isHidden()
    set_advanced_mode(panel, False)
    assert not panel.advanced_btn.isChecked() and panel.toning_section.isHidden()


def test_convert_roll_runs_reanalyze_and_apply_to_roll_offers_every_frame_card(qapp, monkeypatch) -> None:
    from negpy.desktop.view.sidebar.right_panel import RightPanel

    panel = RightPanel(FakeController(FakeRepo())).controls_panel
    assert not panel.convert_btn.isEnabled(), "no roll open"
    panel.convert_btn.setEnabled(True)
    panel.convert_btn.click()
    assert panel.controller.request_batch_normalization.call_count == 1
    asked = []
    monkeypatch.setattr(panel, "_apply_tab", asked.append)
    panel.apply_roll_btn.click()
    assert set(asked[0]) >= {"color", "tone", "paper", "lab", "retouch", "local", "autocrop", "geometry"}


def test_the_top_bar_follows_the_panel_and_opens_its_tab(qapp) -> None:
    from types import SimpleNamespace

    from negpy.desktop.view.sidebar.baryta_column import apply_column_layout
    from negpy.desktop.view.sidebar.right_panel import RightPanel
    from negpy.desktop.view.widgets.baryta_top_bar import BarytaTopBar

    controller = FakeController(FakeRepo())
    right = RightPanel(controller)
    apply_column_layout(right)
    bar = BarytaTopBar(SimpleNamespace(controller=controller, right_panel=right))
    right.show_tab_by_key("roll")
    assert bar.phase.currentData() == "frame"
    bar.phase.setCurrentIndex(bar.phase.findData("scan"))
    assert right._group_keys[right.group_stack.currentIndex()] == "scan"
