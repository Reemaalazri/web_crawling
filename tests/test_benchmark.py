"""
Smoke tests for benchmark module.
"""

from benchmarks import benchmark_search


def test_benchmark_module_has_main_function() -> None:
    assert callable(benchmark_search.main)