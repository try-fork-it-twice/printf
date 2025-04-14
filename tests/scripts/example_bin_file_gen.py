import struct
from typing import Optional
from icecream import ic

TASK_CREATE = 0
TASK_SWITCHED_IN = 1
TASK_SWITCHED_OUT = 2
TASK_SCANF_CONFIG = 3


class TraceGenerator:
    def __init__(self):
        self.buffer = bytearray()

    def task_create(self, timestamp: int, task_number: int, task_name: str):
        fmt = "<B I I 64s"
        encoded = task_name.encode("utf-8")
        if len(encoded) >= 64:
            encoded = encoded[:63] + b"\0"
        else:
            encoded = encoded + b"\0" + b"\0" * (64 - len(encoded) - 1)
        self.buffer.extend(
            struct.pack(fmt, TASK_CREATE, timestamp, task_number, encoded)
        )
        return self

    def task_switched_in(self, timestamp: int, task_number: int):
        fmt = "<B I I"
        self.buffer.extend(struct.pack(fmt, TASK_SWITCHED_IN, timestamp, task_number))
        return self

    def task_switched_out(self, timestamp: int, task_number: int):
        fmt = "<B I I"
        self.buffer.extend(struct.pack(fmt, TASK_SWITCHED_OUT, timestamp, task_number))
        return self

    def task_custom(
        self,
        timestamp: int,
        task_number: int,
        event_type: int,
        task_name: Optional[str] = None,
    ):
        fmt = "<B I I"
        if task_name:
            encoded = task_name.encode("utf-8")
            if len(encoded) >= 64:
                encoded = encoded[:63] + b"\0"
            else:
                encoded = encoded + b"\0" + b"\0" * (64 - len(encoded) - 1)
            self.buffer.extend(
                struct.pack(fmt, event_type, timestamp, task_number) + encoded
            )
        else:
            self.buffer.extend(struct.pack(fmt, event_type, timestamp, task_number))
        return self

    def task_config(self, version: str, max_task_name_len: int = 64):
        fmt = "<B B B B B"
        major, minor, patch = map(int, version.split("."))
        self.buffer.extend(
            struct.pack(fmt, TASK_SCANF_CONFIG, major, minor, patch, max_task_name_len)
        )
        return self

    def save(self, filename: str):
        with open(filename, "w+b") as f:
            f.write(self.buffer)
        ic("Saved trace file to", filename)
        return self


def gen() -> TraceGenerator:
    return TraceGenerator()
