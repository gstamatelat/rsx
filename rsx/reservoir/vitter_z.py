"""
Implementation of *Algorithm Z* by Vitter [1]_.

*Algorithm Z* improves Vitter's *Algorithm X* by calculating the number of skips between two acceptances in the
reservoir instead of deciding whether to include each element individually.

This module contains the :class:`VitterZSampling` class and the convenience method :func:`vitter_z_sampling`.

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
from rsx.utils.helper import random_exclusive


def vitter_z_sampling(collection: Iterable[Any], sample_size: int, rng: Random = None) -> list[Any]:
    """
    Convenience sampling method that uses :class:`VitterZSampling` to sample ``sample_size`` items from ``collection``.

    Each call to the this method will initialize a new instance of the :class:`VitterZSampling` class and returns its
    reservoir in mutable form.

    :param Iterable[Any] collection: the population collection
    :param int sample_size: the desired sample size
    :param random.Random rng: the random number generator (optional, default :code:`random.SystemRandom()`)
    :return: a sample of size `sample_size` (or less) from `collection`
    :rtype: list[Any]
    """
    vitter_z_sampler: VitterZSampling = VitterZSampling(sample_size, rng)
    if isinstance(collection, Sequence):
        vitter_z_sampler.put_sequence(collection)
    else:
        vitter_z_sampler.put_iterable(collection)
    return vitter_z_sampler._reservoir()  # pylint: disable=protected-access


def _vitter_z_skip_function(sample_size: int, rng: Random) -> Iterator[int]:
    """
    The skip function of Vitter's *Algorithm Z* reservoir sampling scheme.

    :param int sample_size: the desired sample size
    :param Random rng: the random number generator
    :return: an iterator of skip intervals
    :rtype: Iterator[int]
    """
    stream_size: int = sample_size
    w: float = rng.random() ** (-1.0 / sample_size)  # pylint: disable=invalid-name
    while True:
        term: int = stream_size - sample_size + 1
        while True:
            # Generate U and X
            u: float = random_exclusive(rng)  # pylint: disable=invalid-name
            x: float = stream_size * (w - 1.0)  # pylint: disable=invalid-name
            g: int = int(x)  # pylint: disable=invalid-name
            # Test if U <= h(G) / cg(X)
            lhs: float = ((((u * ((stream_size + 1) / term) ** 2) * (term + g)) / (stream_size + x)) ** (
                    1.0 / sample_size))
            rhs: float = (((stream_size + x) / (term + g)) * term) / stream_size
            if lhs < rhs:
                w = rhs / lhs  # pylint: disable=invalid-name
                stream_size += g + 1  # increase stream size
                yield g
                break
            # Test if U <= f(G) / cg(X)
            y: float = (((u * (stream_size + 1)) / term) * (stream_size + g + 1)) / (  # pylint: disable=invalid-name
                    stream_size + x)
            denom: float
            numer_lim: int
            if sample_size < g:
                denom = stream_size
                numer_lim = term + g
            else:
                denom = stream_size - sample_size + g
                numer_lim = stream_size + 1
            for numer in range(stream_size + g, numer_lim - 1, -1):
                y = (y * numer) / denom  # pylint: disable=invalid-name
                denom = denom - 1
            w = rng.random() ** (-1.0 / sample_size)  # pylint: disable=invalid-name
            if (y ** (1.0 / sample_size)) <= (stream_size + x) / stream_size:
                stream_size += g + 1  # increase stream size
                yield g
                break


class VitterZSampling(AbstractReservoirSampling):
    r"""
    Implementation of Vitter's *Algorithm Z* as a class.

    The space complexity of this class is :math:`\mathcal{O}(k)`, where :math:`k` is the sample size.
    """

    def __init__(self, sample_size: int, rng: Random = None) -> None:
        """
        The constructor initializes a new instance of this class using the specified sample size and random number
        generator.

        :param int sample_size: the desired sample size
        :param random.Random rng: the random number generator to use (optional, default :code:`random.SystemRandom()`)
        """
        super().__init__(_vitter_z_skip_function, sample_size, rng)
