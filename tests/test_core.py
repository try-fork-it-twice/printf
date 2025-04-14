import pytest
from tests.scripts.example_bin_file_gen import gen
from itmo_ics_printf.core.datatype import (
    TaskCreate,
    TaskSwitched,
    TraceLog,
    TaskScanfConfig,
)
from pathlib import Path


def test_tracelog_load_basic_valid_file(tmp_path: Path) -> None:

    path = tmp_path / "trace_output.bin"
    (
        gen()
        .task_create(timestamp=0, task_number=1, task_name="Alpha")
        .task_switched_in(timestamp=5, task_number=1)
        .task_switched_out(timestamp=10, task_number=1)
        .task_create(timestamp=15, task_number=2, task_name="Beta")
        .save(path)
    )

    tracelog = TraceLog().load(path)

    assert isinstance(tracelog, TraceLog)
    assert len(tracelog.events) == 4
    assert isinstance(tracelog.events[0], TaskCreate)
    assert tracelog.events[0].timestamp == 0
    assert isinstance(tracelog.events[1], TaskSwitched)
    assert tracelog.events[0].task_name == "Alpha"


def test_tracelog_load_no_events(tmp_path: Path) -> None:
    path = tmp_path / "trace_output_empty.bin"
    gen().save(path)
    tracelog = TraceLog().load(path)

    assert isinstance(tracelog, TraceLog)
    assert tracelog.events == []


def test_tracelog_load_missing_event_fields(tmp_path: Path) -> None:
    path = tmp_path / "trace_output_invalid.bin"
    gen().task_custom(timestamp=1, task_number=0, event_type=0).save(path)

    with pytest.raises(Exception):
        TraceLog().load(path)


def test_tracelog_load_unknown_event_type(tmp_path: Path) -> None:
    path = tmp_path / "trace_output_invalid.bin"
    gen().task_custom(timestamp=1, task_number=0, event_type=99).save(path)

    with pytest.raises(Exception):
        TraceLog().load(path)


def test_tracelog_load_from_non_binary_file(tmp_path: Path) -> None:
    path = tmp_path / "trace_output.txt"
    with open(path, "w") as f:
        f.write("This is not a binary file.")

    with pytest.raises(Exception):
        TraceLog().load(path)


def test_tracelog_load_missing_file() -> None:
    fake_path = "/nonexistent/path/to/file.json"
    with pytest.raises(FileNotFoundError):
        TraceLog().load(fake_path)


def test_tracelog_load_empty_file(tmp_path: Path) -> None:
    path = tmp_path / "trace_output_empty.bin"
    with open(path, "wb") as f:
        pass

    TraceLog().load(path)


def test_tracelog_load_extra_fields(tmp_path: Path) -> None:
    path = tmp_path / "trace_output_invalid.bin"
    gen().task_custom(
        timestamp=1, task_number=0, event_type=1, task_name="ExtraField"
    ).save(path)

    with pytest.raises(Exception):
        TraceLog().load(path)


def test_v2_tracelog_load_basic_valid_file(tmp_path: Path) -> None:

    path = tmp_path / "trace_output.bin"
    (
        gen()
        .task_config(version="0.2.0", max_task_name_len=64)
        .task_create(timestamp=0, task_number=1, task_name="Alpha")
        .task_switched_in(timestamp=5, task_number=1)
        .task_switched_out(timestamp=10, task_number=1)
        .task_create(timestamp=15, task_number=2, task_name="Beta")
        .save(path)
    )

    tracelog = TraceLog().load(path)

    assert isinstance(tracelog, TraceLog)
    assert len(tracelog.events) == 5
    assert isinstance(tracelog.events[1], TaskCreate)
    assert tracelog.events[1].timestamp == 0
    assert isinstance(tracelog.events[2], TaskSwitched)
    assert tracelog.events[1].task_name == "Alpha"
    assert tracelog.events[0] is not None


def test_v2_tracelog_load_no_events(tmp_path: Path) -> None:
    path = tmp_path / "trace_output_empty.bin"
    gen().task_config(version="0.2.0", max_task_name_len=64).save(path)
    tracelog = TraceLog().load(path)

    assert isinstance(tracelog, TraceLog)
    assert len(tracelog.events) == 1
    assert isinstance(tracelog.events[0], TaskScanfConfig)
    assert tracelog.events[1:] == []


def test_v2_tracelog_load_missing_event_fields(tmp_path: Path) -> None:
    path = tmp_path / "trace_output_invalid.bin"
    (
        gen()
        .task_config(version="0.2.0", max_task_name_len=64)
        .task_custom(timestamp=1, task_number=0, event_type=0)
        .save(path)
    )

    with pytest.raises(Exception):
        TraceLog().load(path)


def test_v2_tracelog_load_unknown_event_type(tmp_path: Path) -> None:
    path = tmp_path / "trace_output_invalid.bin"
    (
        gen()
        .task_config(version="0.2.0", max_task_name_len=64)
        .task_custom(timestamp=1, task_number=0, event_type=99)
        .save(path)
    )

    with pytest.raises(Exception):
        TraceLog().load(path)


def test_v2_tracelog_load_extra_fields(tmp_path: Path) -> None:
    path = tmp_path / "trace_output_invalid.bin"
    (
        gen()
        .task_config(version="0.2.0", max_task_name_len=64)
        .task_custom(timestamp=1, task_number=0, event_type=1, task_name="ExtraField")
        .save(path)
    )

    with pytest.raises(Exception):
        TraceLog().load(path)


def test_v2_tracelog_load_extra_name_length(tmp_path: Path) -> None:
    path = tmp_path / "trace_output_invalid.bin"
    (
        gen()
        .task_config(version="0.2.0", max_task_name_len=1)
        .task_custom(timestamp=1, task_number=0, event_type=1, task_name="TooLongName")
        .save(path)
    )

    with pytest.raises(Exception):
        TraceLog().load(path)
