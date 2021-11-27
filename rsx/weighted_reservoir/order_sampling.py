"""
Implementation of order sampling as defined in [1]_ (Section 2.8).

According to order sampling, each unit of the population is assigned a key based on its weight and the items with the
largest key are selected as the sample. The implementation is based on a priority queue algorithm, in order to abide by
the specification of the reservoir sampling interface, within the abstract class :class:`OrderSampling`.

.. [1] Yves G. Berger, Yves Tillé.
       Sampling with Unequal Probabilities (2009).
"""

import heapq
from abc import ABC, abstractmethod
from random import Random, SystemRandom
from typing import Collection, Any

from rsx.utils.exceptions import BadWeightError
from rsx.utils.helper import Weighted, SequenceDecorator
from rsx.weighted_reservoir.weighted_reservoir_sampling import AbstractWeightedReservoirSampling


class OrderSampling(AbstractWeightedReservoirSampling, ABC):
    """
    Implementation of order sampling as an abstract class.

    Concrete subclasses need to implement the ``_key``, ``_is_weight_legal`` and ``_default_weight`` methods, which are
    described next.

    ``def _key(weight: float, rng: Random)``
       Must return a key based on the given weight and random number generator. The returned key must be on average
       increasing with the given weight.
    ``def _is_weight_legal(weight: float)``
       Must return a boolean value indicating whether the given value is a legal weight.
    ``def _default_weight()``
       Must return the default weight of the algorithm, when no weight has been given.
    """

    def __init__(self, sample_size: int, rng: Random = None):
        """
        The constructor initializes the instance using a sample size and a random number generator without any elements
        in the reservoir. The constructor runs in constant time.

        :param int sample_size: the desired sample size
        :param Random rng: the random number generator (optional, default ``SystemRandom()``)
        """
        if sample_size < 1:
            raise ValueError("sample_size must be >= 1")
        self.__sample_size: int = sample_size
        self.__stream_size: int = 0
        if rng is None:
            self.__rng: Random = SystemRandom()
        else:
            self.__rng = rng
        self.__heap: list[Weighted] = []

    @abstractmethod
    def _key(self, weight: float, rng: Random):
        raise NotImplementedError

    @abstractmethod
    def _is_weight_legal(self, weight: float):
        raise NotImplementedError

    @abstractmethod
    def _default_weight(self):
        raise NotImplementedError

    def put(self, element: Any, weight: float = None) -> bool:
        if element is None:
            raise ValueError("element was None")
        if weight is None:
            weight = self._default_weight()
        if not self._is_weight_legal(weight):
            raise BadWeightError
        self.__stream_size += 1
        new_item: Weighted = Weighted(element, self._key(weight, self.__rng))
        if len(self.__heap) < self.__sample_size:
            heapq.heappush(self.__heap, new_item)
            return True
        if self.__heap[0].weight < new_item.weight:
            heapq.heapreplace(self.__heap, new_item)
            return True
        return False

    def sample_size(self) -> int:
        return self.__sample_size

    def stream_size(self) -> int:
        return self.__stream_size

    def sample(self) -> Collection[Any]:
        return SequenceDecorator(self.__heap, lambda x: x.value)
