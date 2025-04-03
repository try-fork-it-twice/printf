import pytest

import plotly.graph_objects as go

from itmo_ics_printf.adapters import create_adapter
from itmo_ics_printf.core.datatype import TraceLog
from typing import Dict, Any


def test_plotly():
    try:
        tracelog = TraceLog().load("tests/traces/trace2.bin")

        adapter = create_adapter("plotly")
        plot_data: Dict[str, Any] = adapter.convert(tracelog)

        fig = go.Figure(data=plot_data["data"], layout=plot_data["layout"])
        fig.show()

        assert isinstance(fig, go.Figure)
    except ImportError:
        pytest.skip("plotly not installed")


if __name__ == "__main__":
    test_plotly()
