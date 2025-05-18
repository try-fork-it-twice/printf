import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
from matplotlib.figure import Figure
import random
from typing import List, Tuple
from matplotlib.axes import Axes
from itmo_ics_printf.core.datatype import (
    TraceLog,
    TaskCreate,
    TaskSwitched,
    TASK_SWITCHED_IN,
)
from matplotlib.collections import PathCollection


class MatplotlibAdapter:
    def convert(self, tracelog: TraceLog) -> Figure:
        """Convert a TraceLog object to a Matplotlib figure."""
        fig: Figure
        ax: Axes
        fig, ax = plt.subplots()
        timestamps, task_numbers, event_types, creation_names = (
            self._extract_tracelog_data(tracelog)
        )

        tasks = sorted(set(task_numbers))
        if not tasks:
            return fig

        colors = {task: self._generate_vibrant_color() for task in tasks}
        lines: List[List[Tuple[int, int]]] = []
        line_colors: List[Tuple[float, float, float]] = []
        all_scatter: List[PathCollection] = []
        labels_dict = {}

        for task in tasks:
            task_events = [
                (ts, et)
                for ts, tn, et in zip(timestamps, task_numbers, event_types)
                if tn == task
            ]
            task_events.sort(key=lambda x: x[0])

            intervals: List[Tuple[int, int]] = self._calculate_intervals(task_events)

            color = colors[task]
            for start, end in intervals:
                lines.append([(start, task), (end, task)])
                line_colors.append(color)

            task_name = (
                creation_names[task - 1]
                if (task - 1) < len(creation_names)
                else f"Task {task}"
            )

            # Create separate scatter plots for each event type with labels
            create_ts = [ts for ts, et in task_events if et == "TaskCreate"]
            if create_ts:
                sc = ax.scatter(
                    create_ts,
                    [task] * len(create_ts),
                    color=color,
                    marker="o",
                    s=256,
                    linewidth=2,
                    zorder=3,
                )
                labels_dict[sc] = [f"TaskCreate: {task_name}"] * len(create_ts)
                all_scatter.append(sc)

            in_ts = [ts for ts, et in task_events if et == "TASK_SWITCHED_IN"]
            if in_ts:
                sc = ax.scatter(
                    in_ts,
                    [task] * len(in_ts),
                    color=color,
                    marker="|",
                    s=256,
                    linewidth=1,
                    zorder=3,
                )
                labels_dict[sc] = [f"TASK_SWITCHED_IN (Task {task})"] * len(in_ts)
                all_scatter.append(sc)

            out_ts = [ts for ts, et in task_events if et == "TASK_SWITCHED_OUT"]
            if out_ts:
                sc = ax.scatter(
                    out_ts,
                    [task] * len(out_ts),
                    color=color,
                    marker="|",
                    s=256,
                    linewidth=1,
                    zorder=3,
                )
                labels_dict[sc] = [f"TASK_SWITCHED_OUT (Task {task})"] * len(out_ts)
                all_scatter.append(sc)

        if lines:
            lc = LineCollection(lines, colors=line_colors, linewidths=28, zorder=2)
            ax.add_collection(lc)

        ax.set_title("Task Execution Timeline")
        ax.set_xlabel("Timestamp")
        ax.set_ylabel("Task Number")
        ax.invert_yaxis()
        ax.set_yticks(tasks)
        ax.set_xticks(sorted(set(timestamps)))
        ax.grid(True, axis="x", alpha=0.3)

        return fig

    def _calculate_intervals(
        self, task_events: List[Tuple[int, str]]
    ) -> List[Tuple[int, int]]:
        intervals: List[Tuple[int, int]] = []
        current_start = None
        for ts, et in task_events:
            if et == "TASK_SWITCHED_IN":
                if current_start is not None:
                    pass
                current_start = ts
            elif et == "TASK_SWITCHED_OUT" and current_start is not None:
                intervals.append((current_start, ts))
                current_start = None
        return intervals

    def _extract_tracelog_data(
        self, tracelog: TraceLog
    ) -> Tuple[List[int], List[int], List[str], List[str]]:
        timestamps: List[int] = []
        task_numbers: List[int] = []
        event_types: List[str] = []
        creation_names: List[str] = []
        for event in tracelog.events:
            if isinstance(event, TaskCreate):
                timestamps.append(event.timestamp)
                task_numbers.append(event.task_number)
                event_types.append("TaskCreate")
                creation_names.append(event.task_name)
            elif isinstance(event, TaskSwitched):
                timestamps.append(event.timestamp)
                task_numbers.append(event.task_number)
                event_type = (
                    "TASK_SWITCHED_IN"
                    if event.event_type == TASK_SWITCHED_IN
                    else "TASK_SWITCHED_OUT"
                )
                event_types.append(event_type)
        return timestamps, task_numbers, event_types, creation_names

    def _generate_vibrant_color(self) -> Tuple[float, float, float]:
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
