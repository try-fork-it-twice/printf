import pytest

import plotly.graph_objects as go

from itmo_ics_printf.adapters import create_adapter
from itmo_ics_printf.core.datatype import TraceLog
from typing import Dict, Any


def _test_plotly(path: str):
    try:
        tracelog = TraceLog().load(path)

        adapter = create_adapter("plotly")
        plot_data: Dict[str, Any] = adapter.convert(tracelog)

        fig = go.Figure(data=plot_data["data"], layout=plot_data["layout"])
        fig.show()

        assert isinstance(fig, go.Figure)
    except ImportError:
        pytest.skip("plotly not installed")


def test_plotly():
    for i in range(1, 5):
        tracelog_path = f"tests/traces/trace{i}.bin"
        _test_plotly(tracelog_path)
