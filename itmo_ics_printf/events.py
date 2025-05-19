import struct
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import IntEnum
from typing import Optional, Self, TypeAlias, final

TaskNumber: TypeAlias = int
Microseconds: TypeAlias = int


class EventType(IntEnum):
    CONFIG = 0
    TASK_CREATE = 1
    TASK_SWITCHED_IN = 2
    TASK_SWITCHED_OUT = 3


@dataclass
class Version:
    major: int
    minor: int
    patch: int

    @classmethod
    def parse(cls, version: str) -> "Version":
        parts = [int(part) for part in version.split(".")]
        if len(parts) != 3:
            raise ValueError(f"Unsupported version format: expected major.minor.patch, but got {version}")

        return cls(*parts)


class TraceEvent(ABC):
    @classmethod
    @abstractmethod
    def from_bytes(cls, buf: bytes, cfg: "Config") -> Self:
        """Parse event from the compatible `scanf` binary representation."""

    @classmethod
    @abstractmethod
    def size(self, cfg: "Config") -> int:
        """Size of the event in bytes."""


@dataclass
@final
class Config(TraceEvent):
    STRUCT_FORMAT = "<B B B B B"
    SIZE = struct.calcsize(STRUCT_FORMAT)

    version: Version
    max_task_name_len: int

    @classmethod
    def from_bytes(cls, buf: bytes, _: Optional["Config"] = None) -> "Config":
        _, major, minor, patch, max_task_name_len = struct.unpack(cls.STRUCT_FORMAT, buf[: cls.SIZE])
        version = Version(major, minor, patch)
        return cls(version, max_task_name_len)

    @classmethod
    def size(self, _: Optional["Config"] = None) -> int:
        return Config.SIZE


@dataclass
@final
class TaskCreate(TraceEvent):
    STRUCT_FORMAT = "<B I I"
    SIZE = struct.calcsize(STRUCT_FORMAT)

    timestamp: Microseconds
    task_number: TaskNumber
    task_name: str

    @classmethod
    def from_bytes(cls, buf: bytes, cfg: Config) -> "TaskCreate":
        full_format = f"{cls.STRUCT_FORMAT} {cfg.max_task_name_len}s"
        full_size = struct.calcsize(full_format)
        _, timestamp, task_number, raw_task_name = struct.unpack(full_format, buf[:full_size])
        task_name = raw_task_name.split(b"\0")[0].decode("utf-8")
        return cls(timestamp, task_number, task_name)

    @classmethod
    def size(self, cfg: Config) -> int:
        return TaskCreate.SIZE + cfg.max_task_name_len


@dataclass
@final
class TaskSwitchedIn(TraceEvent):
    STRUCT_FORMAT = "<B I I"
    SIZE = struct.calcsize(STRUCT_FORMAT)

    timestamp: Microseconds
    task_number: TaskNumber

    @classmethod
    def from_bytes(cls, buf: bytes, _: Optional[Config] = None) -> "TaskSwitchedIn":
        _, timestamp, task_number = struct.unpack(cls.STRUCT_FORMAT, buf[: cls.SIZE])
        return cls(timestamp, task_number)

    @classmethod
    def size(self, _: Optional[Config] = None) -> int:
        return TaskSwitchedIn.SIZE


@dataclass
@final
class TaskSwitchedOut(TraceEvent):
    STRUCT_FORMAT = "<B I I"
    SIZE = struct.calcsize(STRUCT_FORMAT)

    timestamp: Microseconds
    task_number: TaskNumber

    @classmethod
    def from_bytes(cls, buf: bytes, _: Optional[Config] = None) -> "TaskSwitchedOut":
        _, timestamp, task_number = struct.unpack(cls.STRUCT_FORMAT, buf[: cls.SIZE])
        return cls(timestamp, task_number)

    @classmethod
    def size(self, _: Optional[Config] = None) -> int:
        return TaskSwitchedOut.SIZE
