import pytest
from matplotlib.figure import Figure

from itmo_ics_printf.events import (
    Config,
    TaskCreate,
    TaskSwitchedIn,
    TaskSwitchedOut,
)
from itmo_ics_printf.tracelog import PRINTF_VERSION, TraceLog

DEFAULT_CONFIG = Config(version=PRINTF_VERSION, max_task_name_len=64)


@pytest.fixture
def tracelog_with_events() -> TraceLog:
    """Fixture to create a TraceLog with sample events."""
    events = [
        TaskCreate(timestamp=1, task_number=1, task_name="Task A"),
        TaskSwitchedIn(timestamp=2, task_number=1),
        TaskSwitchedOut(timestamp=5, task_number=1),
        TaskCreate(timestamp=3, task_number=2, task_name="Task B"),
        TaskSwitchedIn(timestamp=4, task_number=2),
        TaskSwitchedOut(timestamp=6, task_number=2),
    ]
    return TraceLog(DEFAULT_CONFIG, events)


@pytest.fixture
def empty_tracelog() -> TraceLog:
    """Fixture to create an empty TraceLog."""
    return TraceLog(DEFAULT_CONFIG, [])


def test_convert_with_events(tracelog_with_events: TraceLog) -> None:
    """Test the convert method with a TraceLog containing events."""
    fig, ax = tracelog_with_events.plot()
    assert isinstance(fig, Figure), "The result should be a Matplotlib Figure."
    assert len(fig.axes) == 1, "The figure should contain one Axes."
    assert ax.get_title() == "Task Execution Timeline", "The title of the plot is incorrect."
    assert ax.get_xlabel() == "Time (μs)", "The x-axis label is incorrect."
    assert ax.get_ylabel() == "Task", "The y-axis label is incorrect."


def test_convert_with_empty_tracelog(empty_tracelog: TraceLog) -> None:
    """Test the convert method with an empty TraceLog."""
    fig, ax = empty_tracelog.plot()
    assert isinstance(fig, Figure), "The result should be a Matplotlib Figure."
    assert len(fig.axes) == 1, "The figure should contain one Axes."
    assert ax.get_title() == "Task Execution Timeline", "The title of the plot is incorrect."
    assert ax.get_xlabel() == "Time (μs)", "The x-axis label is incorrect."
    assert ax.get_ylabel() == "Task", "The y-axis label is incorrect."
