import pytest


def test_numpy_compatibility():
    try:
        import numpy as np

    except ImportError:
        pytest.skip("numpy not installed")
