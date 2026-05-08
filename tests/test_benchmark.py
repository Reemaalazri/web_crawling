"""
Smoke tests for benchmark module.
"""

from benchmarks import benchmark_search


# -------------------------
# Benchmark module tests
# -------------------------

def test_benchmark_module_exposes_main_function() -> None:
    """Ensure the benchmark script provides an executable main function."""

    assert callable(benchmark_search.main)
