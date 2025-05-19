import pytest

from itmo_ics_printf.analyze import ExecutionInfo, Task, events_execution_info
from itmo_ics_printf.errors import BadTraceLogError
from itmo_ics_printf.events import TaskCreate, TaskSwitchedIn, TaskSwitchedOut, TraceEvent


def test_empty_events() -> None:
    result = events_execution_info([])
    assert isinstance(result, ExecutionInfo)
    assert result.tasks == {}
    assert result.executions == {}
    assert result.stats.min_execution == (0, 0)
    assert result.stats.max_execution == (0, 0)
    assert result.stats.mean_execution == 0
    assert result.stats.min_idle == 0
    assert result.stats.max_idle == 0


def test_basic_execution_flow() -> None:
    events: list[TraceEvent] = [
        TaskCreate(timestamp=100, task_number=1, task_name="Task1"),
        TaskSwitchedIn(timestamp=200, task_number=1),
        TaskSwitchedOut(timestamp=300, task_number=1),
    ]
    result = events_execution_info(events)

    assert result.tasks[1] == Task(name="Task1", number=1, created_at=100)
    assert result.executions[1] == [(200, 300)]
    assert result.stats.min_execution == (1, 100)
    assert result.stats.max_execution == (1, 100)
    assert result.stats.mean_execution == 100
    assert result.stats.min_idle == 0
    assert result.stats.max_idle == 0


def test_multiple_tasks() -> None:
    events: list[TraceEvent] = [
        TaskCreate(timestamp=100, task_number=1, task_name="Task1"),
        TaskCreate(timestamp=110, task_number=2, task_name="Task2"),
        TaskSwitchedIn(timestamp=200, task_number=1),
        TaskSwitchedOut(timestamp=300, task_number=1),
        TaskSwitchedIn(timestamp=350, task_number=2),
        TaskSwitchedOut(timestamp=500, task_number=2),
        TaskSwitchedIn(timestamp=550, task_number=1),
        TaskSwitchedOut(timestamp=600, task_number=1),
    ]
    result = events_execution_info(events)

    assert len(result.tasks) == 2
    assert result.tasks[1].name == "Task1"
    assert result.tasks[2].name == "Task2"

    assert result.executions[1] == [(200, 300), (550, 600)]
    assert result.executions[2] == [(350, 500)]

    assert result.stats.min_execution == (1, 50)
    assert result.stats.max_execution == (2, 150)
    assert result.stats.mean_execution == 100
    assert result.stats.min_idle == 50
    assert result.stats.max_idle == 50


def test_task_creation_only() -> None:
    events: list[TraceEvent] = [
        TaskCreate(timestamp=100, task_number=1, task_name="Task1"),
        TaskCreate(timestamp=200, task_number=2, task_name="Task2"),
    ]
    result = events_execution_info(events)

    assert len(result.tasks) == 2
    assert result.executions == {}
    assert result.stats.min_execution == (0, 0)
    assert result.stats.max_execution == (0, 0)
    assert result.stats.mean_execution == 0
    assert result.stats.min_idle == 0
    assert result.stats.max_idle == 0


def test_consecutive_switched_in_error() -> None:
    events: list[TraceEvent] = [
        TaskCreate(timestamp=100, task_number=1, task_name="Task1"),
        TaskSwitchedIn(timestamp=200, task_number=1),
        TaskSwitchedIn(timestamp=250, task_number=1),
    ]
    with pytest.raises(BadTraceLogError, match="Two consecutive TASK_SWITCHED_IN events was found."):
        events_execution_info(events)


def test_switched_out_without_in_error() -> None:
    events: list[TraceEvent] = [TaskCreate(timestamp=100, task_number=1, task_name="Task1"), TaskSwitchedOut(timestamp=300, task_number=1)]
    with pytest.raises(BadTraceLogError, match="TASK_SWITCHED_OUT event without preceding TASK_SWITCHED_IN event was found."):
        events_execution_info(events)


def test_overlapping_executions() -> None:
    events: list[TraceEvent] = [
        TaskCreate(timestamp=100, task_number=1, task_name="Task1"),
        TaskCreate(timestamp=110, task_number=2, task_name="Task2"),
        TaskCreate(timestamp=120, task_number=3, task_name="Task3"),
        TaskSwitchedIn(timestamp=200, task_number=1),
        TaskSwitchedOut(timestamp=300, task_number=1),
        TaskSwitchedIn(timestamp=300, task_number=2),
        TaskSwitchedOut(timestamp=500, task_number=2),
        TaskSwitchedIn(timestamp=500, task_number=3),
        TaskSwitchedOut(timestamp=700, task_number=3),
    ]
    result = events_execution_info(events)

    assert len(result.tasks) == 3
    assert result.executions[1] == [(200, 300)]
    assert result.executions[2] == [(300, 500)]
    assert result.executions[3] == [(500, 700)]

    assert result.stats.min_execution == (1, 100)
    assert result.stats.max_execution == (2, 200)
    assert result.stats.mean_execution == 166
    assert result.stats.min_idle == 0
    assert result.stats.max_idle == 0


def test_mean_execution_rounding() -> None:
    events: list[TraceEvent] = [
        TaskCreate(timestamp=100, task_number=1, task_name="Task1"),
        TaskSwitchedIn(timestamp=200, task_number=1),
        TaskSwitchedOut(timestamp=301, task_number=1),
        TaskSwitchedIn(timestamp=400, task_number=1),
        TaskSwitchedOut(timestamp=500, task_number=1),
    ]
    result = events_execution_info(events)

    assert result.stats.mean_execution == 100
