from dataclasses import dataclass

from itmo_ics_printf.errors import BadTraceLogError
from itmo_ics_printf.events import Microseconds, TaskCreate, TaskNumber, TaskSwitchedIn, TaskSwitchedOut, TraceEvent


@dataclass
class Task:
    name: str
    number: TaskNumber
    created_at: Microseconds  # int


@dataclass
class ExecutionStats:
    min_execution: tuple[TaskNumber, Microseconds]
    max_execution: tuple[TaskNumber, Microseconds]
    mean_execution: Microseconds
    min_idle: Microseconds
    max_idle: Microseconds


@dataclass
class ExecutionInfo:
    tasks: dict[TaskNumber, Task]
    executions: dict[TaskNumber, list[tuple[Microseconds, Microseconds]]]
    stats: ExecutionStats


def events_execution_info(events: list[TraceEvent]) -> ExecutionInfo:
    """Analyze tasks creation and execution statistics.

    Returns:
        Tasks creation and execution statistics.

    Raises:
        BadTraceLogError: If the sequence of TASK_SWITCHED_IN and TASK_SWITCHED_OUT events is invalid.
            E.g., two consecutive SWITCHED_IN, or a SWITCHED_OUT without a preceding SWITCHED_IN.
    """
    tasks: dict[TaskNumber, Task] = {}
    executions: dict[TaskNumber, list[tuple[Microseconds, Microseconds]]] = {}
    switch_ins: dict[TaskNumber, Microseconds] = {}

    for event in events:
        match event:
            case TaskCreate(timestamp, task_number, task_name):
                tasks[task_number] = Task(task_name, task_number, timestamp)
            case TaskSwitchedIn(timestamp, task_number):
                if task_number in switch_ins:
                    raise BadTraceLogError("Two consecutive TASK_SWITCHED_IN events was found.")

                switch_ins[task_number] = timestamp
            case TaskSwitchedOut(timestamp, task_number):
                if task_number not in switch_ins:
                    raise BadTraceLogError("TASK_SWITCHED_OUT event without preceding TASK_SWITCHED_IN event was found.")

                interval = (switch_ins.pop(task_number), timestamp)
                executions.setdefault(task_number, []).append(interval)

    stats = _events_execution_stats(tasks, executions)
    return ExecutionInfo(tasks, executions, stats)


def _events_execution_stats(
    tasks: dict[TaskNumber, Task],
    executions: dict[TaskNumber, list[tuple[Microseconds, Microseconds]]],
) -> ExecutionStats:
    if not executions:
        return ExecutionStats(min_execution=(0, 0), max_execution=(0, 0), mean_execution=0, min_idle=0, max_idle=0)

    execution_times: dict[TaskNumber, list[Microseconds]] = {}
    for task_num, intervals in executions.items():
        execution_times[task_num] = [end - start for start, end in intervals]

    min_exec_task = None
    min_exec_time = 10**100
    max_exec_task = None
    max_exec_time = 0
    total_exec_time = 0
    total_exec_count = 0

    for task_num, times in execution_times.items():
        for time in times:
            total_exec_time += time
            total_exec_count += 1

            if time < min_exec_time:
                min_exec_time = time
                min_exec_task = task_num

            if time > max_exec_time:
                max_exec_time = time
                max_exec_task = task_num

    mean_exec_time = total_exec_time // total_exec_count if total_exec_count > 0 else 0

    all_intervals = []
    for task_num, intervals in executions.items():
        task = tasks[task_num]
        if task.name != "IDLE":
            all_intervals.extend(intervals)

    all_intervals.sort()

    idle_times = []
    for i in range(1, len(all_intervals)):
        current_start = all_intervals[i][0]
        prev_end = all_intervals[i - 1][1]
        idle_times.append(current_start - prev_end)

    min_idle = min(idle_times) if idle_times else 0
    max_idle = max(idle_times) if idle_times else 0

    return ExecutionStats(
        min_execution=(min_exec_task, min_exec_time) if min_exec_task is not None else (0, 0),
        max_execution=(max_exec_task, max_exec_time) if max_exec_task is not None else (0, 0),
        mean_execution=mean_exec_time,
        min_idle=min_idle,
        max_idle=max_idle,
    )
