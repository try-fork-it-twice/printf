from itmo_ics_printf.core.datatype import TaskCreate, TaskSwitched
import pytest

import plotly.graph_objects as go
from typing import Dict, Any
from unittest.mock import MagicMock


from itmo_ics_printf.adapters import create_adapter


def test_plotly_basic() -> None:
    tracelog = MagicMock()
    tracelog.load.return_value = tracelog

    adapter = create_adapter("plotly")
    plot_data: Dict[str, Any] = adapter.convert(tracelog)

    fig = go.Figure(data=plot_data["data"], layout=plot_data["layout"])

    assert isinstance(fig, go.Figure)


def test_plotly_no_events() -> None:
    tracelog = MagicMock()
    tracelog.events = []

    adapter = create_adapter("plotly")
    plot_data: Dict[str, Any] = adapter.convert(tracelog)

    fig = go.Figure(data=plot_data["data"], layout=plot_data["layout"])

    assert isinstance(fig, go.Figure)
    assert len(fig.data) == 0


def test_plotly_lonely_switch() -> None:
    tracelog = MagicMock()
    tracelog.events = [
        TaskSwitched(timestamp=15, task_number=2, event_type=2),
    ]

    with pytest.raises(Exception):
        adapter = create_adapter("plotly")
        plot_data: Dict[str, Any] = adapter.convert(tracelog)
        go.Figure(data=plot_data["data"], layout=plot_data["layout"])


def test_plotly_switch_without_create() -> None:
    tracelog = MagicMock()
    tracelog.events = [
        TaskSwitched(timestamp=5, task_number=1, event_type=1),
        TaskSwitched(timestamp=10, task_number=1, event_type=2),
    ]

    with pytest.raises(Exception):
        adapter = create_adapter("plotly")
        plot_data: Dict[str, Any] = adapter.convert(tracelog)
        go.Figure(data=plot_data["data"], layout=plot_data["layout"])


def test_plotly_double_switch_in() -> None:
    tracelog = MagicMock()
    tracelog.events = [
        TaskCreate(timestamp=5, task_number=1, task_name="Alpha"),
        TaskSwitched(timestamp=10, task_number=1, event_type=1),
        TaskSwitched(timestamp=15, task_number=1, event_type=1),
    ]

    with pytest.raises(Exception):
        adapter = create_adapter("plotly")
        plot_data: Dict[str, Any] = adapter.convert(tracelog)
        go.Figure(data=plot_data["data"], layout=plot_data["layout"])


def test_plotly_double_switch_out() -> None:
    tracelog = MagicMock()
    tracelog.events = [
        TaskCreate(timestamp=5, task_number=1, task_name="Alpha"),
        TaskSwitched(timestamp=10, task_number=1, event_type=2),
        TaskSwitched(timestamp=15, task_number=1, event_type=2),
    ]

    with pytest.raises(Exception):
        adapter = create_adapter("plotly")
        plot_data: Dict[str, Any] = adapter.convert(tracelog)
        go.Figure(data=plot_data["data"], layout=plot_data["layout"])


def test_plotly_invalid_timestamp() -> None:
    tracelog = MagicMock()
    tracelog.events = [
        TaskCreate(timestamp=5, task_number=1, task_name="Alpha"),
        TaskSwitched(timestamp=10, task_number=1, event_type=1),
        TaskSwitched(timestamp=10, task_number=1, event_type=2),
    ]

    with pytest.raises(Exception):
        adapter = create_adapter("plotly")
        plot_data: Dict[str, Any] = adapter.convert(tracelog)
        go.Figure(data=plot_data["data"], layout=plot_data["layout"])


def test_plotly_double_switch_out_after_in() -> None:
    tracelog = MagicMock()
    tracelog.events = [
        TaskCreate(timestamp=5, task_number=1, task_name="Alpha"),
        TaskSwitched(timestamp=10, task_number=1, event_type=1),
        TaskSwitched(timestamp=15, task_number=1, event_type=2),
        TaskSwitched(timestamp=20, task_number=1, event_type=2),
    ]

    with pytest.raises(Exception):
        adapter = create_adapter("plotly")
        plot_data: Dict[str, Any] = adapter.convert(tracelog)
        go.Figure(data=plot_data["data"], layout=plot_data["layout"])


def test_plotly_create_between_switches() -> None:
    tracelog = MagicMock()
    tracelog.events = [
        TaskCreate(timestamp=10, task_number=1, task_name="Alpha"),
        TaskSwitched(timestamp=9, task_number=1, event_type=1),
        TaskSwitched(timestamp=15, task_number=1, event_type=2),
    ]

    with pytest.raises(Exception):
        adapter = create_adapter("plotly")
        plot_data: Dict[str, Any] = adapter.convert(tracelog)
        go.Figure(data=plot_data["data"], layout=plot_data["layout"])
