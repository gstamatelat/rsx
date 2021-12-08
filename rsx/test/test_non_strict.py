"""
Tests for all algorithms without the ratio estimator property.
"""

from typing import Any
from typing import Iterable

import pytest

import rsx.weighted_reservoir.efraimidis
import rsx.weighted_reservoir.pareto
from rsx.test.helper import first_order_frequencies


def sampling_efraimidis(population: list[Any], weights: list[float], sample_size: int) -> Iterable[int]:
    method = rsx.weighted_reservoir.efraimidis.EfraimidisSampling(sample_size)
    for i in range(len(population)):
        method.put(population[i], weights[i])
    return method.sample()


def sampling_pareto(population: list[Any], weights: list[float], sample_size: int) -> Iterable[int]:
    method = rsx.weighted_reservoir.pareto.ParetoSampling(sample_size)
    for i in range(len(population)):
        method.put(population[i], weights[i])
    return method.sample()


@pytest.mark.parametrize(
    "sampling_method", [
        sampling_efraimidis,
        sampling_pareto
    ]
)
def test_first_order(sampling_method):
    """
    The first order inclusion probability should increase with the weight of the element.
    """
    population_size: int = 10
    for sample_size in range(1, 6):
        frequencies: dict[Any, int] = first_order_frequencies(
            sampling_method,
            200000,
            population_size,
            sample_size,
            [(i + 1) / (population_size + 1) for i in range(population_size)]
        )
        differences: list[float] = [frequencies[i + 1] - frequencies[i] for i in range(population_size - 1)]
        assert all(diff > 0 for diff in differences), \
            f"The differences were {differences} for sample size {sample_size}"
