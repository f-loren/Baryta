from dataclasses import replace

from conftest import FakeController, FakeRepo
from negpy.desktop.view.sidebar.baryta_combined import CARD_LAYOUT_SETTING
from negpy.desktop.view.sidebar.baryta_layout import set_advanced_mode
from negpy.desktop.view.sidebar.controls_panel import ControlsPanel


def _panel(layout: str = "combined") -> ControlsPanel:
    return ControlsPanel(FakeController(FakeRepo(**{CARD_LAYOUT_SETTING: layout})))


def _edited(panel: ControlsPanel) -> ControlsPanel:
    state = panel.controller.state
    alt = state.config.altproc
    state.config = replace(
        state.config, lab=replace(state.config.lab, saturation=1.5), altproc=replace(alt, lith_exposure=alt.lith_exposure + 0.5)
    )
    panel._sync_modified_dots()
    return panel


def _reset(panel: ControlsPanel, section):
    section.reset_requested.emit()
    return panel.controller.session.update_config.call_args.args[0]


def test_classic_keeps_each_control_in_its_own_card(qapp) -> None:
    panel = _panel("classic")
    assert panel.lab_section.isAncestorOf(panel.lab_sidebar.saturation_slider)
    assert panel.altproc_section.isAncestorOf(panel.altproc_sidebar)


def test_color_holds_saturation_and_print_look_holds_the_alternative_processes(qapp) -> None:
    panel = _panel()
    lab = panel.lab_sidebar
    for widget in (lab.saturation_slider, lab.skin_protection_slider, lab.chroma_denoise_slider):
        assert panel.color_sidebar.color_block.isAncestorOf(widget)
    assert panel.paper_section.isAncestorOf(panel.altproc_sidebar)
    set_advanced_mode(panel, True)
    panel.altproc_section.setVisible(True)
    assert panel.altproc_section.isHidden()


def test_a_moved_control_counts_on_the_card_that_shows_it(qapp) -> None:
    panel = _edited(_panel())
    assert panel.color_section.modified_count == 1
    assert panel.lab_section.modified_count == 0
    assert panel.paper_section.modified_count == 1


def test_reset_covers_the_controls_the_card_shows(qapp) -> None:
    panel = _edited(_panel())
    default = ControlsPanel(FakeController(FakeRepo())).controller.state.config
    assert _reset(panel, panel.lab_section).lab.saturation == 1.5
    assert _reset(panel, panel.color_section).lab.saturation == default.lab.saturation
    assert _reset(panel, panel.paper_section).altproc == default.altproc
