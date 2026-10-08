"""GPU-owned boundary regression for appended fields and optional CPU accents."""
from dataclasses import fields

from core.effects import Template, build_graph
from core.highlight_pulse import pulse_filters


def test_v597_positional_arguments_stay_in_place():
    template = Template(fog_enabled=True, montage_fx='dark',
                        scene_keyframes=[{'time': 0, 'yaw': 4}])
    new = {'smart_highlight_enabled', 'smart_highlight_style', 'highlight_pulse'}
    previous = [getattr(template, field.name) for field in fields(Template) if field.name not in new]
    restored = Template(*previous)
    assert restored.fog_enabled and restored.montage_fx == 'dark'
    assert restored.scene_keyframes == [{'time': 0, 'yaw': 4}]
    assert not restored.smart_highlight_enabled
    assert restored.smart_highlight_style == 'auto' and restored.highlight_pulse == 0


def test_enabling_planner_alone_does_not_change_filter_graph():
    template = Template()
    before = build_graph(template, 7, False, effect_events=[(4, 4.4)])
    template.smart_highlight_enabled = True
    assert build_graph(template, 7, False, effect_events=[(4, 4.4)]) == before
    template.highlight_pulse = .7
    assert build_graph(template, 7, False, effect_events=[(4, 4.4)]) != before
    assert build_graph(template, 7, False, effect_events=[]) == build_graph(Template(), 7, False, effect_events=[])


def test_expression_is_bounded_for_merged_events_and_strength():
    assert pulse_filters([(1, 1.4)], -1) == []
    assert pulse_filters([], 1) == []
    events = [(i, i + .4) for i in range(100)]
    graph = pulse_filters(events, 5)[0]
    assert graph == pulse_filters(events[:8], 1)[0]
    assert graph.count('exp(-22*abs(t-') == 16
