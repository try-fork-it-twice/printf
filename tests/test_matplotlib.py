import pytest
from itmo_ics_printf.adapters.matplotlib import MatplotlibAdapter
from itmo_ics_printf.core.datatype import TraceLog, TaskCreate, TaskSwitched, TASK_SWITCHED_IN, TASK_SWITCHED_OUT
from matplotlib.figure import Figure

@pytest.fixture
def tracelog_with_events():
    """Fixture to create a TraceLog with sample events."""
    events = [
        TaskCreate(timestamp=1, task_number=1, task_name="Task A"),
        TaskSwitched(timestamp=2, task_number=1, event_type=TASK_SWITCHED_IN),
        TaskSwitched(timestamp=5, task_number=1, event_type=TASK_SWITCHED_OUT),
        TaskCreate(timestamp=3, task_number=2, task_name="Task B"),
        TaskSwitched(timestamp=4, task_number=2, event_type=TASK_SWITCHED_IN),
        TaskSwitched(timestamp=6, task_number=2, event_type=TASK_SWITCHED_OUT),
    ]
    tracelog = TraceLog()
    tracelog.events = events
    return tracelog

@pytest.fixture
def empty_tracelog():
    """Fixture to create an empty TraceLog."""
    return TraceLog()

def test_convert_with_events(tracelog_with_events):
    """Test the convert method with a TraceLog containing events."""
    adapter = MatplotlibAdapter()
    fig = adapter.convert(tracelog_with_events)
    assert isinstance(fig, Figure), "The result should be a Matplotlib Figure."
    assert len(fig.axes) == 1, "The figure should contain one Axes."
    ax = fig.axes[0]
    assert ax.get_title() == "Task Execution Timeline", "The title of the plot is incorrect."
    assert ax.get_xlabel() == "Timestamp", "The x-axis label is incorrect."
    assert ax.get_ylabel() == "Task Number", "The y-axis label is incorrect."

def test_convert_with_empty_tracelog(empty_tracelog):
    """Test the convert method with an empty TraceLog."""
    adapter = MatplotlibAdapter()
    fig = adapter.convert(empty_tracelog)
    
    assert isinstance(fig, Figure), "The result should be a Matplotlib Figure."
    assert len(fig.axes) == 1, "The figure should contain one Axes."
    ax = fig.axes[0]
    assert ax.get_title() == "", "The title of the plot is incorrect."
    assert ax.get_xlabel() == "", "The x-axis label is incorrect."
    assert ax.get_ylabel() == "", "The y-axis label is incorrect."
    assert len(ax.collections) == 0, "There should be no data plotted for an empty TraceLog."
