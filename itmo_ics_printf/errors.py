from itmo_ics_printf.events import Version


class PrintfError(Exception):
    pass


class MissedConfigEventError(PrintfError):
    def __init__(self) -> None:
        super().__init__("SCANF_CONFIG event was not found in the trace log.")


class UnknownEventError(PrintfError):
    def __init__(self, event_type: int) -> None:
        super().__init__(f"Unknown event type {event_type}")


class DifferentScanfVersionError(PrintfError):
    def __init__(self, expected: Version, actual: Version) -> None:
        super().__init__(f"Major version mismatch: printf version is {expected}, but got scanf Tracelog with version {actual}.")
        self.expected = expected
        self.actual = actual


class BadTraceLogError(PrintfError):
    pass
