"""
Implementation of *Algorithm L* by Li [1]_.

*Algorithm L* improves the algorithms of Vitter (see :mod:`vitter_x <rsx.reservoir.vitter_x>` and :mod:`vitter_y
<rsx.reservoir.vitter_y>` modules) by identifying that the random skip variable follows the geometric distribution.

This module contains the :class:`LiLSampling` class and the convenience method :func:`li_l_sampling`.

References
----------
.. [1] Kim-Hung Li.
       Reservoir-sampling algorithms of time complexity O(n(1 + log(N/n))) (1994).
"""
import math
from collections.abc import Iterable
from random import Random
from typing import Any
from typing import Iterator
from typing import Sequence

from rsx.reservoir.reservoir_sampling import AbstractReservoirSampling
from rsx.utils.helper import random_exclusive


def li_l_sampling(collection: Iterable[Any], sample_size: int, rng: Random = None) -> list[Any]:
    """
    Convenience sampling method that uses :class:`LiLSampling` to sample ``sample_size`` items from ``collection``.

    Each call to the this method will initialize a new instance of the :class:`LiLSampling` class and returns its
    reservoir in mutable form.

    :param Iterable[Any] collection: the population collection
    :param int sample_size: the desired sample size
    :param random.Random rng: the random number generator (optional, default :code:`random.SystemRandom()`)
    :return: a sample of size `sample_size` (or less) from `collection`
    :rtype: list[Any]
    """
    li_l_sampler: LiLSampling = LiLSampling(sample_size, rng)
    if isinstance(collection, Sequence):
        li_l_sampler.put_sequence(collection)
    else:
        li_l_sampler.put_iterable(collection)
    return li_l_sampler._reservoir()  # pylint: disable=protected-access


def _li_l_skip_function(sample_size: int, rng: Random) -> Iterator[int]:
    """
    The skip function of Li's *Algorithm L* reservoir sampling scheme.

    :param int sample_size: the desired sample size
    :param Random rng: the random number generator
    :return: an iterator of skip intervals
    :rtype: Iterator[int]
    """
    w: float = random_exclusive(rng) ** (1.0 / sample_size)  # pylint: disable=invalid-name
    while True:
        random1: float = random_exclusive(rng)
        random2: float = random_exclusive(rng)
        skip: int = int(math.log(random1) / math.log(1 - w))
        w = w * random2 ** (1.0 / sample_size)  # pylint: disable=invalid-name
        yield skip


class LiLSampling(AbstractReservoirSampling):
    r"""
    Implementation of Li's *Algorithm L* as a class.

    The space complexity of this class is :math:`\mathcal{O}(k)`, where :math:`k` is the sample size.
    """

    def __init__(self, sample_size: int, rng: Random = None) -> None:
        """
        The constructor initializes a new instance of this class using the specified sample size and random number
        generator.

        :param int sample_size: the desired sample size
        :param random.Random rng: the random number generator to use (optional, default :code:`random.SystemRandom()`)
        """
        super().__init__(_li_l_skip_function, sample_size, rng)
