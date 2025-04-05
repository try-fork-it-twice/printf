import struct
from icecream import ic

TASK_CREATE = 0
TASK_SWITCHED_IN = 1
TASK_SWITCHED_OUT = 2


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

    def save(self, filename: str):
        with open(filename, "w+b") as f:
            f.write(self.buffer)
        ic("Saved trace file to", filename)
        return self


def gen() -> TraceGenerator:
    return TraceGenerator()


if __name__ == "__main__":
    traces_dir = "./tests/traces/"
    gen().task_create(
        timestamp=1000, task_number=1, task_name="TaskAlpha"
    ).task_switched_in(timestamp=1500, task_number=1).task_switched_out(
        timestamp=2000, task_number=1
    ).save(
        f"{traces_dir}trace1.bin"
    )

    (
        gen()
        .task_create(timestamp=0, task_number=1, task_name="init")
        .task_switched_in(timestamp=110, task_number=1)
        .task_switched_out(timestamp=120, task_number=1)
        .task_create(timestamp=130, task_number=2, task_name="file_open")
        .task_create(timestamp=135, task_number=3, task_name="file_read")
        .task_switched_in(timestamp=140, task_number=2)
        .task_switched_in(timestamp=145, task_number=3)
        .save(f"{traces_dir}trace2.bin")
    )

    gen().task_switched_in(timestamp=10, task_number=1).save(f"{traces_dir}trace3.bin")

    (
        gen()
        .task_create(timestamp=0, task_number=1, task_name="init")
        .task_switched_in(timestamp=5, task_number=1)
        .task_create(timestamp=10, task_number=2, task_name="file_system_init")
        .task_create(timestamp=12, task_number=3, task_name="network_init")
        .task_create(timestamp=14, task_number=4, task_name="io_init")
        .task_switched_out(timestamp=15, task_number=1)
        .task_switched_in(timestamp=16, task_number=2)
        .task_switched_out(timestamp=21, task_number=2)
        .task_switched_in(timestamp=22, task_number=3)
        .task_switched_out(timestamp=27, task_number=3)
        .task_switched_in(timestamp=28, task_number=4)
        .task_switched_out(timestamp=33, task_number=4)
        .task_switched_in(timestamp=34, task_number=1)
        .task_switched_out(timestamp=39, task_number=1)
        .save(f"{traces_dir}trace4.bin")
    )
