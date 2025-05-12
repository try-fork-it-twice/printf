from .base import TraceLogAdapter


def create_adapter(adapter_type: str) -> TraceLogAdapter:
    """
    Factory function to create an adapter based on the specified type.
    """
    # if adapter_type == "base":
    #     return TraceLogAdapter()
    # else:
    #     raise ValueError(f"Unknown adapter type: {adapter_type}")
    raise NotImplementedError(
        f"Adapter type '{adapter_type}' is not implemented. Available adapters: base"
    )
