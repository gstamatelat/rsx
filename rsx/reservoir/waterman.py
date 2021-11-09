"""
Implementation of *Algorithm R* credited to Alan Waterman [1]_.

The implementation is the simplest unweighted sampling algorithm that each time a new element is put, it determines
whether it should be accepted in the sample by producing a random number.

This module contains the :class:`WatermanSampling` class and the convenience method :func:`waterman_sampling`.

Usage
-----
Select 10 random numbers in the range [0,99]:

.. code-block:: python

   random_numbers: list[int] = waterman_sampling(range(100), 10)
   print(random_numbers)

This can also be achieved with the following fragment that demonstrates the class API:

.. code-block:: python

   ws: WatermanSampling = WatermanSampling(10)
   ws.put_iterable(range(0,100))
   random_numbers: Sequence[int] = ws.sample()
   print(random_numbers)

References
----------
.. [1] Donald Knuth.
       The Art of Computer Programming, Vol II, Random Sampling and Shuffling (1997).
"""

import random
from collections.abc import Iterable
from typing import Any
from typing import Sequence

from rsx.reservoir.reservoir_sampling import ReservoirSampling
from rsx.utils.helper import SequenceDecorator


def waterman_sampling(collection: Iterable[Any], sample_size: int, rng: random.Random = None) -> list[Any]:
    """
    Convenience sampling method that uses :class:`WatermanSampling` to sample ``sample_size`` items from ``collection``.

    Each call to the this method will initialize a new instance of the :class:`WatermanSampling` class and contains the
    following code:

    .. code-block:: python

       waterman_sampler: WatermanSampling = WatermanSampling(sample_size, rng)
       waterman_sampler.put_iterable(collection)
       return waterman_sampler._reservoir()

    :param Iterable[Any] collection: the population collection
    :param int sample_size: the desired sample size
    :param random.Random rng: the random number generator (optional, default :code:`random.SystemRandom()`)
    :return: a sample of size `sample_size` (or less) from `collection`
    :rtype: list[Any]
    """
    waterman_sampler: WatermanSampling = WatermanSampling(sample_size, rng)
    waterman_sampler.put_iterable(collection)
    return waterman_sampler._reservoir()  # pylint: disable=protected-access


class WatermanSampling(ReservoirSampling):
    r"""
    Implementation of Waterman's algorithm as a class.

    The space complexity of this class is :math:`\mathcal{O}(k)`, where :math:`k` is the sample size.
    """

    def __init__(self, sample_size: int, rng: random.Random = None) -> None:
        """
        The constructor initializes a new instance of this class using the specified sample size and random number
        generator.

        :param int sample_size: the desired sample size
        :param random.Random rng: the random number generator to use (optional, default :code:`random.SystemRandom()`)
        """
        if sample_size < 1:
            raise ValueError("sample_size must be >= 1")
        self.__sample_size: int = sample_size
        self.__stream_size: int = 0
        if rng is None:
            self.rng: random.Random = random.SystemRandom()
        else:
            self.rng = rng
        self.__reservoir: list[Any] = []
        self.__reservoir_view: Sequence[Any] = SequenceDecorator(self.__reservoir)

    def put(self, element: Any) -> bool:
        if element is None:
            raise ValueError("e was None")
        self.__stream_size += 1
        if len(self.__reservoir) < self.__sample_size:
            self.__reservoir.append(element)
            return True
        __r = self.rng.randrange(0, self.__stream_size)
        if __r < self.__sample_size:
            self.__reservoir[__r] = element
            return True
        return False

    def put_iterable(self, iterable: Iterable[Any]) -> bool:
        if iterable is None:
            raise ValueError("iterable was None")
        changed: bool = False
        for element in iterable:
            if self.put(element):
                changed = True
        return changed

    def sample_size(self) -> int:
        return self.__sample_size

    def stream_size(self) -> int:
        return self.__stream_size

    def sample(self) -> Sequence[Any]:
        return self.__reservoir_view

    def _reservoir(self) -> list[Any]:
        """
        Returns a reference of the reservoir of this instance in mutable form.

        .. warning::

           Invoking this method is dangerous as it may break the instance. In particular if the object returned is
           modified, even slightly, this will result in undefined future behavior of the instance. As a result, the
           instance must not be used after performing some mutation on the reservoir.

        This method runs in constant time.

        :return: the reservoir of this instance
        :rtype: list[Any]
        """
        return self.__reservoir
