r"""
Implementation of the simple sampling method Alg. 3 in [1]_.

The implementation is a simple random sampling scheme without replacement and utilizes a virtual shuffle over the
elements of the population that guarantees no collisions. Random access is required for the population elements. All
possible samples of size :math:`k` are equiprobable. The algorithm runs in time :math:`\Theta(k)` and uses extra memory
:math:`\mathcal{O}(k)`.

This module contains 2 functions :func:`swor` and :func:`swor_population` which are the implementations of the
algorithm. The :func:`swor` function provides a zero-based index interface by assuming the population values to be in
the range :math:`[0,n)` while the :func:`swor_population` function is a convenience wrapper around :func:`swor` that
accepts the population values as a :class:`list`.

Usage
-----
1. Select 10 random numbers in the range [0,99] such that all possible samples are equiprobable:

   .. code-block:: python

      random_numbers: list[int] = list(swor(n=100, k=10))
      print(random_numbers)

2. Select 5 random unique letters from the alphabet:

   .. code-block:: python

      random_letters = list(swor_population(list("abcdefghijklmnopqrstuvwxyz"), 5))
      print(random_letters)

References
----------
.. [1] Vladimir Batagelj, Ulrik Brandes.
       Efficient generation of large random networks (2005).
"""

from random import Random
from random import SystemRandom
from typing import Any
from typing import Iterator
from typing import Sequence


def swor_population(population: Sequence[Any], k: int, rng: Random = None) -> Iterator[Any]:
    """
    Implementation of the simple random sampling without replacement.

    The sample is returned as an :class:`Iterator <typing.Iterator>` object because it avoids the need of extra memory.
    If you need to reuse the result of this operation you need to store it in a collection, such as a :class:`list`. The
    input population should not mutate while the iteration is in progress.

    :param Sequence[Any] population: the population
    :param int k: the size of the sample
    :param Random rng: the random number generator to use (optional, default :code:`random.SystemRandom()`)
    :return: an :class:`iterator <typing.Iterator>` that holds the references of `k` random items of `population`
    :rtype: Iterator[Any]
    """
    for next_index in swor(len(population), k, rng):
        yield population[next_index]


def swor(n: int, k: int, rng: Random = None) -> Iterator[int]:  # pylint: disable=invalid-name
    """
    Implementation of the simple random sampling without replacement.

    The population is assumed to be the elements in the range :math:`[0,n)`. The sample is returned as an
    :class:`Iterator <typing.Iterator>` object because it avoids the need of extra memory. If you need to reuse the
    result of this operation you need to store it in a collection, such as a :class:`list`.

    :param int n: the population size
    :param int k: the size of the sample
    :param Random rng: the random number generator to use (optional, default :code:`random.SystemRandom()`)
    :return: an :class:`iterator <typing.Iterator>` that holds the references of `k` random items of `population`
    :rtype: Iterator[int]
    """
    if not n >= k >= 0:
        raise ValueError(f"The condition n >= k > 0 is not satisfied, got n = {n}, k = {k}")
    if rng is None:
        rng = SystemRandom()
    swaps: dict[int, int] = {}
    for i in range(k):
        next_index: int = rng.randrange(0, n - i)
        yield swaps.get(next_index, next_index)
        swaps[next_index] = swaps.get(n - i - 1, n - i - 1)
