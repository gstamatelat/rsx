"""
Helper functions for the tests.
"""

import typing
from typing import Any
from typing import Iterable


def first_order_mean_squared_error(method: typing.Callable[[list[Any], list[float], int], Iterable[Any]],
                                   iterations: int,
                                   population_size: int,
                                   sample_size: int,
                                   weights: list[float]) -> float:
    """
    Calculates the mean squared error of the first order inclusion probabilities for the given sampling design indicated
    by the `sampling` parameter from the ideal uniform first order inclusion probabilities.

    :param method: the function representing the sampling method
    :type method: Callable[[list[Any], int], list[Any]]
    :param int iterations: the number of iterations to perform
    :param int population_size: the number of elements in the population
    :param int sample_size: the number of elements in the sample
    :param list[float] weights: the weights assigned to the population elements
    :return: the mean squared error of the first order inclusion probabilities of the given sampling design with respect
             to the uniform inclusion probabilities
    :rtype: float
    """
    if iterations < 1:
        raise ValueError("iterations cannot be less than 1")
    if sample_size < 1:
        raise ValueError("sample_size cannot be less than 1")
    if sample_size > population_size:
        raise ValueError("sample_size cannot be higher than population_size")
    if len(weights) != population_size:
        raise ValueError("the weights must be as many as the population elements")
    weight_sum: float = sum(weights)
    frequencies: dict[Any, int] = {}
    for _ in range(iterations):
        sample: Iterable[Any] = method(list(range(population_size)), weights, sample_size)
        for element in sample:
            if element not in frequencies:
                frequencies[element] = 0
            frequencies[element] += 1
    return sum(
        (v / iterations - weights[k] * sample_size / weight_sum) ** 2 for k, v in frequencies.items()
    ) / population_size
