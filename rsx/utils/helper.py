"""
Various helper functions and utilities.
"""

import functools
from collections import Counter
from random import Random
from random import SystemRandom
from typing import Any, Callable
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


def random_exclusive(rng: Random = None) -> float:
    """
    Returns a pseudorandom double value in :math:`(0,1)` exclusive.

    This method will perform repeated calls to ``rng.random()`` until the value returned is not 0. In practice, the
    probability to get a zero is extremely low but some algorithms require exclusiveness.

    :param Random rng: the random number generator to use (optional, default ``SystemRandom()``)
    :return: a pseudorandom float value in `(0,1)` exclusive
    :rtype: float
    """
    if rng is None:
        rng = SystemRandom()
    random_value: float = 0.0
    while random_value == 0.0:
        random_value = rng.random()
    return random_value


def sequence_equals(a: Sequence[Any], b: Sequence[Any]) -> bool:  # pylint: disable=invalid-name
    """
    Returns a value indicating whether two sequences contain the same elements.

    More specifically, returns ``True`` if the two sequences are of the same size, contain the same distinct elements,
    and each element has equal appearance frequency on both collections.

    This method runs in time proportional to the size of the arguments and uses extra space that is also proportional
    to the size of the arguments.

    :param Sequence[Any] a: one collection
    :param Sequence[Any] b: the other collection
    :return: ``True`` if ``a`` and ``b`` contain the same elements, otherwise ``False``
    :rtype: bool
    """
    if len(a) != len(b):
        return False
    if a is b:
        return True
    counter_a: Counter = Counter(a)
    counter_b: Counter = Counter(b)
    return counter_a == counter_b


@functools.total_ordering
class Weighted:
    """
    Represents an item with a weight.

    This class is intended to be used in weighted random sampling algorithms.
    """

    def __init__(self, value: object, weight: float):
        """
        The constructor initializes the instance with an object and a weight.

        :param object value: the object
        :param float weight: the weight of the object
        """
        self.value: object = value
        self.weight: float = weight

    def __lt__(self, other) -> bool:
        return self.weight.__lt__(other.weight)

    def __eq__(self, other) -> bool:
        return self.weight.__eq__(other.weight)


class SequenceDecorator(Sequence[Any]):
    """
    Auxiliary utility that decorates a :class:`Sequence <collections.abc.Sequence>` around a read-only :class:`Sequence
    <collections.abc.Sequence>` container.
    """

    def __init__(self, data: Sequence[Any], mapping_function: Callable[[Any], Any] = lambda x: x) -> None:
        """
        The constructor initializes a new instance of this class as a decorator of the given underlying sequence. The
        instance created will be backed by that sequence. The optional ``mapping_function`` argument maps all items of
        the given input collection and defaults to the identity function if not given. The constructor runs in constant
        time.

        :param Sequence[Any] data: the underlying list to create this decorator from
        :param Callable[[Any], Any] mapping_function: the mapping function of the elements (optional, default: the
                                                      identity function)
        """
        super().__init__()
        self.__data = data
        self.__mapping_function = mapping_function

    def __len__(self) -> int:
        return self.__data.__len__()

    def __getitem__(self, item) -> Any:
        return self.__mapping_function(self.__data.__getitem__(item))

    def __eq__(self, o: Any) -> bool:
        if not isinstance(o, Sequence):
            return False
        if len(self) != len(o):
            return False
        for x1, x2 in zip(self, o):
            if x1 != x2:
                return False
        return True

    def __repr__(self) -> str:
        return self.__data.__repr__()
