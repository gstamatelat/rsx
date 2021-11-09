r"""
Implementation of the Alias-Vose method [1]_.

The alias method is a family of efficient algorithms to sample an element from a discrete probability distribution and
it was originally published by Alastair J. Walker [2]_. It uses a preprocessing state to construct a probability table
and an alias table. Then random elements can be drawn in constant time according to that probability distribution. The
alias method that was revised by Michael D. Vose [1]_ and is implemented in this module aims to be numerically stable
and avoid floating point number rounding errors while performing the preprocessing stage in time linear the the states
of the discrete probability distribution. The implementation of the method is the :class:`AliasMethod` class.

Usage
-----
The following example demonstrates how to take a sample of 2 elements with replacement from the discrete probability
distribution

.. math::

   p(i) =
   \begin{cases}
     0.1, & \text{if } i = 0 \\
     0.2, & \text{if } i = 1 \\
     0.3, & \text{if } i = 2 \\
     0.4, & \text{if } i = 3
   \end{cases}

.. code-block:: python

   alias: AliasMethod = AliasMethod([.1, .2, .3, .4])
   print(list(alias.sample() for _ in range(2)))

References
----------
.. [1] Michael D. Vose.
       A linear algorithm for generating random numbers with a given distribution (1991).
.. [2] Alastair J. Walker.
       An efficient method for generating discrete random variables with general distributions (1977).
"""

import math
import random
import typing


class AliasMethod:  # pylint: disable=too-few-public-methods
    """
    Implementation of the Alias-Vose method as a class.

    This class uses an implicit population of the zero-based indices in :math:`[0,n)`, where :math:`n` is the number of
    discrete elements in the distribution. It also uses memory proportional to :math:`n`.
    """

    def __init__(self, probabilities: typing.Collection[float]):
        """
        Initialize this instance with a discrete probability distribution ``probabilities``, where the probability of
        the element with index ``i`` is equal to ``probabilities[i]``.

        This class associates the implicit population items with a zero-based index which is returned by the
        :meth:`sample` method. The given probabilities need to sum to unity and no check will be performed to ensure
        that. The given collection will not be mutated within the constructor and the future of the instance will not
        depend on this reference either. This constructor runs in time proportional to the size of the given
        distribution collection.

        :param Collection[float] probabilities: the discrete probability distribution as a series of probabilities
        """
        if len(probabilities) < 1:
            raise ValueError("the population must contain at least one element")

        # Initialize
        self.n = len(probabilities)  # pylint: disable=invalid-name
        self.u: list[float] = []  # pylint: disable=invalid-name
        self.k: list[int] = []
        small: list[int] = []
        large: list[int] = []
        i: int = 0
        for next_probability in probabilities:
            scaled_probability: float = self.n * next_probability
            if scaled_probability > 1:
                large.append(i)
            elif scaled_probability < 1:
                small.append(i)
            self.u.append(scaled_probability)
            self.k.append(i)
            i += 1

        # Process
        while small and large:
            l: int = large.pop()  # pylint: disable=invalid-name
            s: int = small.pop()  # pylint: disable=invalid-name
            self.k[s] = l
            self.u[l] = (self.u[l] + self.u[s]) - 1
            if self.u[l] < 1:
                small.append(l)
            else:
                large.append(l)

        # Finalize
        while small:
            self.u[small.pop()] = 1
        while large:
            self.u[large.pop()] = 1

    def sample(self, rng: random.Random = None) -> int:
        """
        Sample a single element from the discrete probability distribution given and return its index.

        This method runs in constant time.

        :param Random rng: the random number generator (optional, default ``random.SystemRandom()``
        :return: an index representing the chosen element from the discrete probability distribution
        :rtype: int
        """
        if rng is None:
            rng = random.SystemRandom()
        x: float = rng.random()  # pylint: disable=invalid-name
        i: int = math.floor(self.n * x)
        y: float = self.n * x + 1 - i - 1  # pylint: disable=invalid-name
        if y < self.u[i]:
            return i
        return self.k[i]
