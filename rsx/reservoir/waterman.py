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

from collections.abc import Iterable
from random import Random
from typing import Any
from typing import Iterator
from typing import Sequence

from rsx.reservoir.reservoir_sampling import AbstractReservoirSampling


def waterman_sampling(collection: Iterable[Any], sample_size: int, rng: Random = None) -> list[Any]:
    """
    Convenience sampling method that uses :class:`WatermanSampling` to sample ``sample_size`` items from ``collection``.

    Each call to the this method will initialize a new instance of the :class:`WatermanSampling` class and returns its
    reservoir in mutable form.

    :param Iterable[Any] collection: the population collection
    :param int sample_size: the desired sample size
    :param random.Random rng: the random number generator (optional, default :code:`random.SystemRandom()`)
    :return: a sample of size `sample_size` (or less) from `collection`
    :rtype: list[Any]
    """
    waterman_sampler: WatermanSampling = WatermanSampling(sample_size, rng)
    if isinstance(collection, Sequence):
        waterman_sampler.put_sequence(collection)
    else:
        waterman_sampler.put_iterable(collection)
    return waterman_sampler._reservoir()  # pylint: disable=protected-access


def _waterman_skip_function(sample_size: int, rng: Random) -> Iterator[int]:
    """
    The skip function of Waterman's reservoir sampling scheme.

    :param int sample_size: the desired sample size
    :param Random rng: the random number generator
    :return: an iterator of skip intervals
    :rtype: Iterator[int]
    """
    stream_size: int = sample_size
    while True:
        stream_size += 1
        skip_count: int = 0
        while rng.random() * stream_size >= sample_size:
            stream_size += 1
            skip_count += 1
        yield skip_count


class WatermanSampling(AbstractReservoirSampling):
    r"""
    Implementation of Waterman's algorithm as a class.

    The space complexity of this class is :math:`\mathcal{O}(k)`, where :math:`k` is the sample size.
    """

    def __init__(self, sample_size: int, rng: Random = None) -> None:
        """
        The constructor initializes a new instance of this class using the specified sample size and random number
        generator.

        :param int sample_size: the desired sample size
        :param random.Random rng: the random number generator to use (optional, default :code:`random.SystemRandom()`)
        """
        super().__init__(_waterman_skip_function, sample_size, rng)
