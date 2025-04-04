import struct


TASK_CREATE = 0
TASK_SWITCHED_IN = 1
TASK_SWITCHED_OUT = 2

SCANF_MAX_TASK_NAME_LEN = 64


class TraceEvent:
    @classmethod
    def from_bytes(cls, buf: bytes) -> "TraceEvent":
        raise NotImplementedError("Subclasses should implement this method")


class TaskCreate(TraceEvent):
    STRUCT_FORMAT = f"<B I I {SCANF_MAX_TASK_NAME_LEN}s"
    SIZE = struct.calcsize(STRUCT_FORMAT)

    def __init__(self, timestamp: int, task_number: int, task_name: str):
        self.timestamp = timestamp
        self.task_number = task_number
        self.task_name = task_name

    def __repr__(self) -> str:
        return f"TaskCreate(timestamp={self.timestamp}, task_number={self.task_number}, task_name={self.task_name})"

    @classmethod
    def from_bytes(cls, buf: bytes) -> "TaskCreate":
        _, timestamp, task_number, raw_task_name = struct.unpack(
            cls.STRUCT_FORMAT, buf[: cls.SIZE]
        )
        task_name = raw_task_name.split(b"\0")[0].decode("utf-8")
        return cls(timestamp, task_number, task_name)


class TaskSwitched(TraceEvent):
    STRUCT_FORMAT = "<B I I"
    SIZE = struct.calcsize(STRUCT_FORMAT)

    def __init__(self, event_type: int, timestamp: int, task_number: int):
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
    def __init__(self):
        self.events = []

    def load(self, filename: str) -> "TraceLog":
        with open(filename, "rb") as f:
            content = f.read()

        offset = 0
        while offset < len(content):
            event_type = content[offset]
            if event_type == TASK_CREATE:
                event = TaskCreate.from_bytes(
                    content[offset : offset + TaskCreate.SIZE]
                )
                offset += TaskCreate.SIZE
            elif event_type in (TASK_SWITCHED_IN, TASK_SWITCHED_OUT):
                event = TaskSwitched.from_bytes(
                    content[offset : offset + TaskSwitched.SIZE]
                )
                offset += TaskSwitched.SIZE
            else:
                raise ValueError(f"Unknown event type: {event_type} at offset {offset}")
            self.events.append(event)

        return self
