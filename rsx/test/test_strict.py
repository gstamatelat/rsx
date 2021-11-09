"""
Tests for all algorithms with the ratio estimator property (strict inclusion probabilities).
"""

from typing import Any
from typing import Iterable

import pytest

import rsx.reservoir.waterman
import rsx.systematic.ordered
import rsx.whole.jessen
from rsx.test.helper import first_order_mean_squared_error


def sampling_ordered_systematic(population: list[Any], weights: list[float], sample_size: int) -> Iterable[int]:
    method = rsx.systematic.ordered.OrderedSystematicPopulation()
    for i in range(len(population)):
        method.push_item(population[i], weights[i])
    return method.sample(sample_size)


def sampling_jessen(population: list[Any], weights: list[float], sample_size: int) -> Iterable[int]:
    method = rsx.whole.jessen.JessenBuilder() \
        .add_weights(weights) \
        .build(sample_size)
    return [population[i] for i in method.sample()]


@pytest.mark.parametrize(
    "sampling_method", [
        sampling_ordered_systematic,
        sampling_jessen
    ]
)
def test_first_order(sampling_method):
    """
    The first order inclusion probabilities should be proportional to the weights of the elements.
    """
    assert first_order_mean_squared_error(sampling_method, 200000, 10, 1, [i + 1 for i in range(10)]) < 1.0e-5
    assert first_order_mean_squared_error(sampling_method, 200000, 10, 2, [i + 1 for i in range(10)]) < 1.0e-5
    assert first_order_mean_squared_error(sampling_method, 200000, 10, 3, [i + 1 for i in range(10)]) < 1.0e-5
    assert first_order_mean_squared_error(sampling_method, 200000, 10, 4, [i + 1 for i in range(10)]) < 1.0e-5
    assert first_order_mean_squared_error(sampling_method, 200000, 10, 5, [i + 1 for i in range(10)]) < 1.0e-5
