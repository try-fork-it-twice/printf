import random
from typing import Tuple

import matplotlib.pyplot as plt
from matplotlib.axes import Axes
from matplotlib.figure import Figure
from matplotlib.lines import Line2D

from itmo_ics_printf.analyze import events_execution_info
from itmo_ics_printf.events import TraceEvent


def plot_events(events: list[TraceEvent]) -> tuple[Figure, Axes]:
    """Plot task events on a timeline.

    For each task:
    - Task creation shown as circles
    - Task execution intervals shown as continuous lines

    Returns:
        Matplotlib Figure and Axes objects
    """

    fig, ax = plt.subplots(figsize=(12, 8))

    execution_info = events_execution_info(events)
    tasks = execution_info.tasks
    executions = execution_info.executions

    task_numbers = sorted(tasks.keys())
    colors = {task_number: _generate_vibrant_color() for task_number in task_numbers}

    for _, task_number in enumerate(task_numbers):
        task = tasks[task_number]
        color = colors[task_number]
        y_position = task_number

        ax.scatter(
            [task.created_at],
            [y_position],
            s=100,
            color=color,
            edgecolors="black",
            linewidth=1,
            zorder=3,
        )

        if task_number in executions:
            for start, end in executions[task_number]:
                ax.plot(
                    [start, end],
                    [y_position, y_position],
                    linewidth=10,
                    solid_capstyle="butt",
                    color=color,
                    zorder=2,
                )

    ax.set_yticks(task_numbers)
    ax.set_yticklabels([f"{task_number}: {tasks[task_number].name}" for task_number in task_numbers])

    all_timestamps = []
    for task in tasks.values():
        all_timestamps.append(task.created_at)

    for intervals in executions.values():
        for start, end in intervals:
            all_timestamps.extend([start, end])

    unique_timestamps = sorted(set(all_timestamps))
    ax.set_xticks(unique_timestamps)

    ax.grid(axis="x", linestyle="--", alpha=0.7)
    ax.set_xlabel("Time (μs)")
    ax.set_ylabel("Task")
    ax.set_title("Task Execution Timeline")

    min_task, min_time = execution_info.stats.min_execution
    max_task, max_time = execution_info.stats.max_execution
    legend_elements = [
        Line2D([0], [0], color="none", label=f"Stats:"),
        Line2D([0], [0], color="none", label=f"Min exec: Task {min_task} ({min_time} μs)"),
        Line2D([0], [0], color="none", label=f"Max exec: Task {max_task} ({max_time} μs)"),
        Line2D([0], [0], color="none", label=f"Mean exec: {execution_info.stats.mean_execution} μs"),
        Line2D([0], [0], color="none", label=f"Min idle: {execution_info.stats.min_idle} μs"),
        Line2D([0], [0], color="none", label=f"Max idle: {execution_info.stats.max_idle} μs"),
    ]
    ax.legend(handles=legend_elements, loc="upper right")

    fig.tight_layout()

    return fig, ax


def _generate_vibrant_color() -> Tuple[float, float, float]:
    r = random.randint(50, 255)
    g = random.randint(50, 255)
    b = random.randint(50, 255)
    while abs(r - g) <= 50 and abs(r - b) <= 50 and abs(g - b) <= 50:
        r, g, b = (
            random.randint(50, 255),
            random.randint(50, 255),
            random.randint(50, 255),
        )

    return (r / 255, g / 255, b / 255)
