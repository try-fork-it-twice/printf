from itmo_ics_printf.adapters.base import TraceLogAdapter
from itmo_ics_printf.core.datatype import TraceLog
from typing import List, Dict, Any


class PlotlyAdapter(TraceLogAdapter):
    def convert(self, tracelog: TraceLog) -> Dict[str, Any]:
        """
        Convert a TraceLog object to a Plotly figure.
        """

        timestamps: List[int] = [event.timestamp for event in tracelog.events]
        task_numbers: List[int] = [event.task_number for event in tracelog.events]
        event_types: List[str] = [type(event).__name__ for event in tracelog.events]

        plot_data: List[Dict[str, Any]] = []
        layout: Dict[str, Any] = {
            "title": "Task Execution Timeline",
            "xaxis_title": "Timestamp",
            "yaxis_title": "Task Number",
        }

        for task_number in sorted(set(task_numbers)):
            task_events = [
                (ts, et)
                for ts, tn, et in zip(timestamps, task_numbers, event_types)
                if tn == task_number
            ]
            if not task_events:
                continue

            xval: List[int] = [ts for ts, _ in task_events]
            yval: List[int] = [task_number] * len(task_events)
            textval: List[str] = [et for _, et in task_events]

            trace = {
                "x": xval,
                "y": yval,
                "mode": "markers+lines",
                "name": f"Task {task_number}",
                "text": textval,
                "hoverinfo": "text",
                "type": "scatter",
            }
            plot_data.append(trace)

        return {"data": plot_data, "layout": layout}
