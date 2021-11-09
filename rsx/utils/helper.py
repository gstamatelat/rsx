"""
Various helper functions and utilities.
"""

from typing import Any
from typing import Iterable
from typing import Sequence


def normalize_probabilities(weights: list[float]) -> list[float]:
    """
    Normalize the given array of floats and returns another array that sums to unity.

    :param list[float] weights: the input array
    :return: the normalized array
    :rtype: list[float]
    """
    weight_sum = sum(weights)
    probabilities: list[float] = []
    for weight in weights:
        if weight <= 0:
            raise ValueError("weight must be positive")
        probabilities.append(weight / weight_sum)
    return probabilities


def check_feasibility(weights: Iterable[float], sample_size: int) -> bool:
    r"""
    Checks the feasibility of a strict inclusion probability problem.

    More formally, given an iterable of weights and an integer indicating the desired sample size, this function checks
    whether the problem consisting in selecting a random sample of the desired size from the population where the
    inclusion probability of each of the population units is strictly proportional to its weight is feasible.

    The check boils down to checking whether all weights :math:`w_i` of the population satisfy the equation
    :math:`w_i * k / Z \le 1`, where :math:`k` is the desired sample size and :math:`Z` is the sum of the weights of all
    elements.

    :param Iterable[float] weights: an iterable of weights representing the weights of the population
    :param int sample_size: the desired sample size
    :return: ``True`` if the problem is feasible, otherwise ``False``
    """
    weight_sum = sum(weights)
    for weight in weights:
        if sample_size * weight / weight_sum > 1:
            return False
    return True


class SequenceDecorator(Sequence[Any]):
    """
    Auxiliary utility that decorates a :class:`list` around a read-only :class:`typing.Sequence` container.
    """

    def __init__(self, data: list[Any]) -> None:
        """
        The constructor initializes a new instance of this class as a decorator of the given underlying list. The
        instance created will be backed by that list. The constructor runs in constant time.

        :param list[Any] data: the underlying list to create this decorator from
        """
        super().__init__()
        self.__data = data

    def __len__(self) -> int:
        return self.__data.__len__()

    def __getitem__(self, item) -> Any:
        return self.__data.__getitem__(item)

    def __eq__(self, o: Any) -> bool:
        return self.__data.__eq__(o)

    def __repr__(self) -> str:
        return self.__data.__repr__()