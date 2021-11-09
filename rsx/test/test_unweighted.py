"""
Tests for all unweighted algorithms.
"""

from typing import Any
from typing import Iterable

import pytest

import rsx.reservoir.waterman
import rsx.simple.swor
import rsx.systematic.ordered
import rsx.whole.jessen
from rsx.test.helper import first_order_mean_squared_error


def sampling_waterman(population: list[Any], weights: list[float], sample_size: int) -> Iterable[Any]:
    return rsx.reservoir.waterman.waterman_sampling(population, sample_size)


def sampling_simple_without_replacement(population: list[Any], weights: list[float], sample_size: int) -> Iterable[Any]:
    return rsx.simple.swor.swor_population(population, sample_size)


def sampling_ordered_systematic(population: list[Any], weights: list[float], sample_size: int) -> Iterable[Any]:
    return rsx.systematic.ordered.ordered_systematic_unweighted_population(population, sample_size)


def sampling_jessen(population: list[Any], weights: list[float], sample_size: int) -> Iterable[Any]:
    jessen = rsx.whole.jessen.JessenBuilder() \
        .add_weights(weights) \
        .build(sample_size)
    return list(map(lambda x: population[x], jessen.sample()))


@pytest.mark.parametrize(
    "sampling_method", [
        sampling_waterman,
        sampling_simple_without_replacement,
        sampling_ordered_systematic,
        sampling_jessen
    ]
)
def test_first_order(sampling_method):
    """
    The first order inclusion probabilities should be uniform. In other words, all elements should have an equal
    probability of being included in the sample.
    """
    assert first_order_mean_squared_error(sampling_method, 300000, 10, 1, [1] * 10) < 1.0e-5
    assert first_order_mean_squared_error(sampling_method, 300000, 10, 2, [1] * 10) < 1.0e-5
    assert first_order_mean_squared_error(sampling_method, 300000, 10, 3, [1] * 10) < 1.0e-5
    assert first_order_mean_squared_error(sampling_method, 300000, 10, 4, [1] * 10) < 1.0e-5
    assert first_order_mean_squared_error(sampling_method, 300000, 10, 5, [1] * 10) < 1.0e-5
