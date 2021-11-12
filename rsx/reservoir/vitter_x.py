"""
Implementation of *Algorithm X* by Vitter [1]_.

*Algorithm X* improves Waterman's algorithm (see :mod:`waterman <rsx.reservoir.waterman>` module) by minimizing the
amount of random variates generated.

This module contains the :class:`VitterXSampling` class and the convenience method :func:`vitter_x_sampling`.

References
----------
.. [1] Jeffrey Scott Vitter.
       Random sampling with a reservoir (1985).
"""

from collections.abc import Iterable
from random import Random
from typing import Any
from typing import Iterator
from typing import Sequence

from rsx.reservoir.reservoir_sampling import AbstractReservoirSampling


def vitter_x_sampling(collection: Iterable[Any], sample_size: int, rng: Random = None) -> list[Any]:
    """
    Convenience sampling method that uses :class:`VitterXSampling` to sample ``sample_size`` items from ``collection``.

    Each call to the this method will initialize a new instance of the :class:`VitterXSampling` class and returns its
    reservoir in mutable form.

    :param Iterable[Any] collection: the population collection
    :param int sample_size: the desired sample size
    :param random.Random rng: the random number generator (optional, default :code:`random.SystemRandom()`)
    :return: a sample of size `sample_size` (or less) from `collection`
    :rtype: list[Any]
    """
    vitter_x_sampler: VitterXSampling = VitterXSampling(sample_size, rng)
    if isinstance(collection, Sequence):
        vitter_x_sampler.put_sequence(collection)
    else:
        vitter_x_sampler.put_iterable(collection)
    return vitter_x_sampler._reservoir()  # pylint: disable=protected-access


def _vitter_x_skip_function(sample_size: int, rng: Random) -> Iterator[int]:
    """
    The skip function of Vitter's *Algorithm X* reservoir sampling scheme.

    :param int sample_size: the desired sample size
    :param Random rng: the random number generator
    :return: an iterator of skip intervals
    :rtype: Iterator[int]
    """
    stream_size: int = sample_size
    while True:
        stream_size += 1
        random_variate = rng.random()
        skip_count: int = 0
        quot: float = (stream_size - sample_size) / stream_size
        while quot > random_variate:
            stream_size += 1
            skip_count += 1
            quot = (quot * (stream_size - sample_size)) / stream_size
        yield skip_count


class VitterXSampling(AbstractReservoirSampling):
    r"""
    Implementation of Vitter's *Algorithm X* as a class.

    The space complexity of this class is :math:`\mathcal{O}(k)`, where :math:`k` is the sample size.
    """

    def __init__(self, sample_size: int, rng: Random = None) -> None:
        """
        The constructor initializes a new instance of this class using the specified sample size and random number
        generator.

        :param int sample_size: the desired sample size
        :param random.Random rng: the random number generator to use (optional, default :code:`random.SystemRandom()`)
        """
        super().__init__(_vitter_x_skip_function, sample_size, rng)
