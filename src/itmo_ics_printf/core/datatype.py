import struct
import sys
import warnings
from abc import ABC
from pathlib import Path

from typing import Optional, Dict
from itmo_ics_printf import __version__

try:
    from icecream import ic  # type: ignore
except ImportError:

    def ic(*args: str) -> None:
        print(*args)


SCANF_VERSION = tuple(map(int, __version__.split(".")))


TASK_CREATE = 0
TASK_SWITCHED_IN = 1
TASK_SWITCHED_OUT = 2
TASK_SCANF_CONFIG = 3

EVENT_TYPE_NAMES: Dict[int, str] = {
    TASK_CREATE: "TASK_CREATE",
    TASK_SWITCHED_IN: "TASK_SWITCHED_IN",
    TASK_SWITCHED_OUT: "TASK_SWITCHED_OUT",
    TASK_SCANF_CONFIG: "TASK_SCANF_CONFIG",
}


def _warning(message: str) -> None:
    warnings.warn(
        f"{'-' * 20}\nWarning:\n{message}\n{'-' * 20}\n",
        category=RuntimeWarning,
        stacklevel=2,
    )


class NoScanfConfigError(Exception):
    def __init__(self) -> None:
        super().__init__("No Scanf configuration found in the trace log.")
        self.message = "No Scanf configuration found in the trace log."


class DifferentScanfVersionError(Exception):
    def __init__(self, expected: str, actual: str) -> None:
        super().__init__(f"Expected Scanf version {expected}, but got {actual}.")
        self.expected = expected
        self.actual = actual


class TraceEvent(ABC):
    @classmethod
    def from_bytes(cls, buf: bytes) -> "TraceEvent":
        raise NotImplementedError("Subclasses should implement this method")


class TaskScanfConfig(TraceEvent):
    class ScanfVersion:
        major = SCANF_VERSION[0]
        minor = SCANF_VERSION[1]
        patch = SCANF_VERSION[2]

        def __init__(self, major: int, minor: int, patch: int) -> None:
            self.major = major
            self.minor = minor
            self.patch = patch

        def __repr__(self) -> str:
            return f"{self.major}.{self.minor}.{self.patch}"

    STRUCT_FORMAT = f"<B B B B B"
    SIZE = struct.calcsize(STRUCT_FORMAT)

    def __init__(self, version: ScanfVersion, max_task_name_len: int) -> None:
        self.version = version
        self.max_task_name_len = max_task_name_len

    def __repr__(self) -> str:
        return f"TaskScanfConfig(version={self.version}, max_task_name_len={self.max_task_name_len})"

    @classmethod
    def from_bytes(
        cls,
        buf: bytes,
    ) -> "TaskScanfConfig":
        _, major, minor, patch, max_task_name_len = struct.unpack(
            cls.STRUCT_FORMAT, buf[: cls.SIZE]
        )
        version = cls.ScanfVersion(major, minor, patch)
        return cls(version, max_task_name_len)


class TaskCreate(TraceEvent):
    STRUCT_FORMAT = f"<B I I"
    SIZE = struct.calcsize(STRUCT_FORMAT)

    def __init__(self, timestamp: int, task_number: int, task_name: str) -> None:
        self.timestamp = timestamp
        self.task_number = task_number
        self.task_name = task_name

    def __repr__(self) -> str:
        return (
            f"TaskCreate(timestamp={self.timestamp}, task_number={self.task_number},"
            f" task_name={self.task_name})"
        )

    @classmethod
    def from_bytes(
        cls, buf: bytes, max_task_name_len: Optional[int] = None
    ) -> "TaskCreate":
        if max_task_name_len is None:
            max_task_name_len = 64
            _warning(
                f"max_task_name_len is None, using default value: {max_task_name_len}"
            )

        full_format = f"{cls.STRUCT_FORMAT} {max_task_name_len}s"
        full_size = struct.calcsize(full_format)

        if len(buf) < full_size:
            raise ValueError(
                f"Buffer too small: {len(buf)} bytes, expected at least {full_size} bytes for "
                f"TaskCreate event."
            )

        _, timestamp, task_number, raw_task_name = struct.unpack(
            full_format, buf[:full_size]
        )
        task_name = raw_task_name.split(b"\0")[0].decode("utf-8")
        return cls(timestamp, task_number, task_name)


class TaskSwitched(TraceEvent):
    STRUCT_FORMAT = "<B I I"
    SIZE = struct.calcsize(STRUCT_FORMAT)

    def __init__(self, event_type: int, timestamp: int, task_number: int) -> None:
        self.event_type = event_type
        self.timestamp = timestamp
        self.task_number = task_number

    def __repr__(self) -> str:
        type_str = (
            "TASK_SWITCHED_IN"
            if self.event_type == TASK_SWITCHED_IN
            else "TASK_SWITCHED_OUT"
        )
        return f"TaskSwitched({type_str}, timestamp={self.timestamp}, task_number={self.task_number})"

    @classmethod
    def from_bytes(cls, buf: bytes) -> "TaskSwitched":
        event_type, timestamp, task_number = struct.unpack(
            cls.STRUCT_FORMAT, buf[: cls.SIZE]
        )
        return cls(event_type, timestamp, task_number)


class TraceLog:
    events: list[TraceEvent]
    max_task_name_len: int
    scanf_version: TaskScanfConfig.ScanfVersion

    def __init__(self) -> None:
        self.events = []

    def _configure(
        self, version: TaskScanfConfig.ScanfVersion, max_task_name_len: int
    ) -> None:
        self.max_task_name_len = max_task_name_len

        self.scanf_version = version
        print(
            f"Configured TraceLog: version={self.scanf_version}, "
            f"max_task_name_len={self.max_task_name_len}"
        )

    def load(self, filename: str | Path) -> "TraceLog":
        with open(filename, "rb") as f:
            content = f.read()

        offset: int = 0
        event_type = content[offset]
        if event_type != TASK_SCANF_CONFIG:
            raise NoScanfConfigError()

        event: TraceEvent
        event = TaskScanfConfig.from_bytes(
            content[offset : offset + TaskScanfConfig.SIZE]
        )
        if event.version.major != SCANF_VERSION[0]:
            raise DifferentScanfVersionError(
                expected=f"{SCANF_VERSION[0]}.*.*",
                actual=f"{event.version.major}.{event.version.minor}.{event.version.patch}",
            )

        offset += TaskScanfConfig.SIZE
        self.events.append(event)
        self._configure(event.version, event.max_task_name_len)

        while offset < len(content):
            event_type = content[offset]

            if event_type == TASK_CREATE:
                event = TaskCreate.from_bytes(
                    content[offset : offset + TaskCreate.SIZE + self.max_task_name_len],
                    self.max_task_name_len,
                )
                offset += TaskCreate.SIZE + self.max_task_name_len
            elif event_type in (TASK_SWITCHED_IN, TASK_SWITCHED_OUT):
                event = TaskSwitched.from_bytes(
                    content[offset : offset + TaskSwitched.SIZE]
                )
                offset += TaskSwitched.SIZE
            else:
                raise ValueError(f"Unknown event type: {event_type} at offset {offset}")
            self.events.append(event)

        return self
