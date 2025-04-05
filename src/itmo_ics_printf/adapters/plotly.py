from itmo_ics_printf.adapters.base import TraceLogAdapter
from itmo_ics_printf.core.datatype import TraceLog, TaskCreate
from typing import List, Dict, Any
import random

from icecream import ic


class PlotlyAdapter(TraceLogAdapter):
    def convert(self, tracelog: TraceLog) -> Dict[str, Any]:
        """
        Convert a TraceLog object to a Plotly figure.
        """

        timestamps: List[int] = [event.timestamp for event in tracelog.events]
        task_numbers: List[int] = [event.task_number for event in tracelog.events]
        event_types: List[str] = [type(event).__name__ for event in tracelog.events]

        creation_names: List[str] = []
        for event in tracelog.events:
            if isinstance(event, TaskCreate):
                creation_names.append(event.task_name)

        plot_data: List[Dict[str, Any]] = []
        layout: Dict[str, Any] = {
            "title": "Task Execution Timeline",
            "xaxis_title": "Timestamp",
            "yaxis_title": "Task Number",
            "yaxis": {"tickmode": "linear", "autorange": "reversed"},
        }

        for task_number in sorted(set(task_numbers)):
            task_events = [
                (ts, tn, et)
                for ts, tn, et in zip(timestamps, task_numbers, event_types)
                if tn == task_number
            ]
            if not task_events:
                continue

            xval: List[int] = [ts for ts, _, _ in task_events]
            yval: List[int] = [task_number] * len(task_events)
            textval: List[str] = [et for _, _, et in task_events]

            line_x = []
            line_y = []
            last_switch_time = None
            num_switches = 0

            for i in range(len(task_events)):
                if task_events[i][2] == "TaskSwitched":
                    if last_switch_time is not None and num_switches % 2 != 0:
                        line_x.extend([last_switch_time, task_events[i][0], None])
                        line_y.extend([task_number, task_number, None])
                    last_switch_time = task_events[i][0]
                    num_switches += 1

            color: str = self.generate_vibrant_color()

            trace_line = {
                "x": line_x,
                "y": line_y,
                "mode": "lines",
                "name": f"Task {{{task_number}}} {creation_names[task_number-1]} working",
                "type": "scatter",
                "line": {"width": 15, "color": color},
            }
            plot_data.append(trace_line)

            textval[0] = f"TaskCreate: {creation_names[task_number-1]}"

            trace_markers = {
                "x": xval,
                "y": yval,
                "mode": "markers",
                "name": f"Task {creation_names[task_number-1]} events",
                "text": textval,
                "hoverinfo": "text",
                "type": "scatter",
                "marker": {
                    "size": 16,
                    "symbol": "circle",
                    "color": color,
                    "line": {"width": 2, "color": "black"},
                },
            }
            plot_data.append(trace_markers)

        return {"data": plot_data, "layout": layout}

    def generate_vibrant_color(self) -> str:
        r = random.randint(50, 255)
        g = random.randint(50, 255)
        b = random.randint(50, 255)
        while abs(r - g) <= 50 and abs(r - b) <= 50 and abs(g - b) <= 50:
            r = random.randint(50, 255)
            g = random.randint(50, 255)
            b = random.randint(50, 255)
        return f"rgb({r}, {g}, {b})"
