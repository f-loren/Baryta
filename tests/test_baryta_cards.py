from dataclasses import replace

from conftest import FakeController, FakeRepo
from negpy.desktop.view.sidebar.baryta_layout import ADVANCED_SETTING, frame_tabs
from negpy.desktop.view.sidebar.controls_panel import ControlsPanel
from negpy.desktop.view.widgets.fold import Fold, FoldButton
from negpy.features.process.models import ProcessMode


def _panel(**settings) -> ControlsPanel:
    return ControlsPanel(FakeController(FakeRepo(**settings)))


def test_tone_shows_shadows_and_highlights_under_contrast_with_no_chevron(qapp) -> None:
    tone = _panel().tone_sidebar
    layout = tone.layout
    shadows, highlights = layout.indexOf(tone.shadow_density_slider), layout.indexOf(tone.highlight_density_slider)
    assert layout.indexOf(tone.split_grade_fold) < shadows and highlights == shadows + 1
    assert not tone.shadow_density_slider.isHidden() and not tone.highlight_density_slider.isHidden()
    for slider in (tone.density_slider, tone.grade_slider, tone.grade_trim_slider):
        assert not slider.findChildren(FoldButton)


def test_darkroom_holds_the_channel_choice_and_resets_it_on_close(qapp) -> None:
    tone = _panel().tone_sidebar
    fold = tone.darkroom_fold
    for widget in (
        tone.ch_btn,
        tone.preflash_slider,
        tone.diffusion_slider,
        tone.contrast_mask_slider,
        tone.shadow_grade_slider,
        tone.highlight_grade_slider,
    ):
        assert fold.content.isAncestorOf(widget)
    fold.set_open(True)
    tone.ch_btn.setCurrentIndex(1)
    fold.button.click()
    assert not fold.is_open() and tone.ch_btn.currentIndex() == 0


def test_on_a_slide_darkroom_keeps_the_channel_choice(qapp) -> None:
    panel = _panel()
    tone = panel.tone_sidebar
    cfg = panel.controller.state.config
    panel.controller.state.config = replace(cfg, process=replace(cfg.process, process_mode=ProcessMode.E6, positive_source=False))
    tone.sync_ui()
    assert tone.aids_fold.content.isHidden()
    assert not tone.ch_btn.isHidden() and not tone.darkroom_fold.button.isHidden()
    tone.ch_btn.hide()
    assert tone.darkroom_fold.button.isHidden(), "nothing left to fold"


def test_print_look_leads_the_finish_tab_in_base_mode(qapp) -> None:
    tabs = {key: attrs for key, _title, attrs in frame_tabs()}
    assert tabs["finish"][0] == "paper_section" and "paper_section" not in tabs["tone"]
    assert not _panel(**{ADVANCED_SETTING: False}).paper_section.isHidden()


def test_curve_shape_holds_the_paper_channel_choice_and_starts_closed(qapp) -> None:
    paper = _panel().paper_sidebar
    curve = next(f for f in paper.findChildren(Fold) if f.key == "paper_curve_shape")
    assert not curve.is_open()
    for widget in (paper.ch_btn, paper.paper_black_btn, paper.paper_dmin_btn):
        assert curve.content.isAncestorOf(widget)
    curve.set_open(True)
    paper.ch_btn.setCurrentIndex(2)
    curve.button.click()
    assert paper.ch_btn.currentIndex() == 0
    reopened = next(f for f in _panel(fold_paper_curve_shape=True).paper_sidebar.findChildren(Fold) if f.key == "paper_curve_shape")
    assert reopened.is_open(), "the user's choice wins"


def test_detail_keeps_its_sub_headers_hidden_after_a_sync(qapp) -> None:
    lab = _panel().lab_sidebar
    lab.sync_ui()
    assert lab.color_header.isHidden()


def test_tone_keeps_its_header_for_pick_better(qapp) -> None:
    panel = _panel()
    tone = next(page for page in panel.pages if page["key"] == "tone")
    assert tone["header"] is not None and tone["header"].isAncestorOf(panel.pick_better_btn)
