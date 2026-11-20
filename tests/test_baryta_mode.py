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
