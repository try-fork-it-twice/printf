from pathlib import Path

import pytest

from itmo_ics_printf.errors import (
    DifferentScanfVersionError,
    MissedConfigEventError,
)
from itmo_ics_printf.events import (
    Config,
    TaskCreate,
    TaskSwitchedIn,
)
from itmo_ics_printf.tracelog import (
    TraceLog,
)
from tests.scripts.example_bin_file_gen import gen


def test_tracelog_load_basic_valid_file(tmp_path: Path) -> None:
    path = tmp_path / "trace_output.bin"
    (
        gen()
        .task_config(version="1.0.0", max_task_name_len=64)
        .task_create(timestamp=0, task_number=1, task_name="Alpha")
        .task_switched_in(timestamp=5, task_number=1)
        .task_switched_out(timestamp=10, task_number=1)
        .task_create(timestamp=15, task_number=2, task_name="Beta")
        .save(path)
    )

    tracelog = TraceLog.load(path)

    assert isinstance(tracelog, TraceLog)
    assert len(tracelog.events) == 5
    assert isinstance(tracelog.events[1], TaskCreate)
    assert tracelog.events[1].timestamp == 0
    assert isinstance(tracelog.events[2], TaskSwitchedIn)
    assert tracelog.events[1].task_name == "Alpha"
    assert tracelog.events[0] is not None


def test_tracelog_load_no_events(tmp_path: Path) -> None:
    path = tmp_path / "trace_output_empty.bin"
    gen().task_config(version="1.0.0", max_task_name_len=64).save(path)
    tracelog = TraceLog.load(path)

    assert isinstance(tracelog, TraceLog)
    assert len(tracelog.events) == 1
    assert isinstance(tracelog.events[0], Config)
    assert tracelog.events[1:] == []


def test_tracelog_load_missing_event_fields(tmp_path: Path) -> None:
    path = tmp_path / "trace_output_invalid.bin"
    gen().task_config(version="1.0.0", max_task_name_len=64).task_custom(timestamp=1, task_number=1, event_type=0).save(path)

    with pytest.raises(Exception):
        TraceLog.load(path)


def test_tracelog_load_unknown_event_type(tmp_path: Path) -> None:
    path = tmp_path / "trace_output_invalid.bin"
    gen().task_config(version="1.0.0", max_task_name_len=64).task_custom(timestamp=1, task_number=0, event_type=99).save(path)

    with pytest.raises(Exception):
        TraceLog.load(path)


def test_tracelog_different_major_version(tmp_path: Path) -> None:
    path = tmp_path / "trace_output_invalid.bin"
    gen().task_config(version="255.1.0", max_task_name_len=64).save(path)

    with pytest.raises(DifferentScanfVersionError):
        TraceLog.load(path)


def test_tracelog_load_missing_config_event(tmp_path: Path) -> None:
    path = tmp_path / "trace_output_invalid.bin"
    gen().task_custom(timestamp=1, task_number=0, event_type=2).save(path)

    with pytest.raises(MissedConfigEventError):
        TraceLog.load(path)
