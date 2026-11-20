from negpy.desktop.view.sidebar.baryta_layout import ADVANCED_SETTING, set_advanced_mode
from negpy.desktop.view.sidebar.controls_panel import ControlsPanel
from conftest import FakeController, FakeRepo


def test_base_mode_hides_an_unedited_advanced_card_and_keeps_an_edited_one(qapp) -> None:
    panel = ControlsPanel(FakeController(FakeRepo()))
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
