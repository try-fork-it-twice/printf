from pathlib import Path

from matplotlib.axes import Axes
from matplotlib.figure import Figure

from itmo_ics_printf.analyze import ExecutionInfo, events_execution_info
from itmo_ics_printf.errors import DifferentScanfVersionError, MissedConfigEventError
from itmo_ics_printf.events import Config, EventType, TaskCreate, TaskSwitchedIn, TaskSwitchedOut, TraceEvent, Version
from itmo_ics_printf.plotting import plot_events
from itmo_ics_printf.version import __version__

PRINTF_VERSION = Version.parse(__version__)


class TraceLog:
    def __init__(self, config: Config, events: list[TraceEvent]) -> None:
        self.config = config
        self.events = events

    @classmethod
    def load(cls, filename: str | Path) -> "TraceLog":
        """Parse TraceLog from tracelog binary file generated by `scanf`."""
        with open(filename, "rb") as f:
            content = f.read()

        events: list[TraceEvent] = []
        offset: int = 0

        event_type = content[offset]
        if event_type != EventType.CONFIG:
            raise MissedConfigEventError()

        config = Config.from_bytes(content[offset : offset + Config.SIZE])
        if config.version.major != PRINTF_VERSION.major:
            raise DifferentScanfVersionError(expected=PRINTF_VERSION, actual=config.version)

        offset += Config.size()
        events.append(config)

        event: TraceEvent
        while offset < len(content):
            event_type = content[offset]
            match event_type:
                case EventType.TASK_CREATE:
                    event = TaskCreate.from_bytes(
                        content[offset : offset + TaskCreate.size(config)],
                        config,
                    )
                case EventType.TASK_SWITCHED_IN:
                    event = TaskSwitchedIn.from_bytes(
                        content[offset : offset + TaskSwitchedIn.size(config)],
                        config,
                    )
                case EventType.TASK_SWITCHED_OUT:
                    event = TaskSwitchedOut.from_bytes(
                        content[offset : offset + TaskSwitchedOut.size(config)],
                        config,
                    )
                case _:
                    raise ValueError(f"Unknown event type: {event_type} at offset {offset}")

            offset += event.size(config)
            events.append(event)

        return cls(config, events)

    def plot(self) -> tuple[Figure, Axes]:
        """Plot task events on a timeline.

        For each task:
        - Task creation shown as circles
        - Task execution intervals shown as continuous lines

        Returns:
            Matplotlib Figure and Axes objects
        """
        return plot_events(self.events)

    def execution_info(self) -> ExecutionInfo:
        """Analyze tasks creation and execution statistics.

        Returns:
            Tasks creation and execution statistics.

        Raises:
            BadTraceLogError: If the sequence of TASK_SWITCHED_IN and TASK_SWITCHED_OUT events is invalid.
                E.g., two consecutive SWITCHED_IN, or a SWITCHED_OUT without a preceding SWITCHED_IN.
        """
        return events_execution_info(self.events)
