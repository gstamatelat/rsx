r"""
Implementation of Madow's ordered systematic sampling [1]_.

According to the ordered systematic approach, the cumulative sum of the weights of the elements of the population is
computed ahead of time; in the case of the unweighted version this is not necessary. Then, the skip is calculated as
:math:`s = Z/k`, where :math:`Z` is the sum of the weights of the population items and :math:`k` the desired sample
size. For the generation of the sample a random number :math:`r` in :math:`[0,s)` is generated and the :math:`i`-th unit
in the sample is taken from the cumulative sum prefixes :math:`\lfloor r+is \rfloor` of the population.

Inclusion Probabilities
-----------------------
Due to the systematic nature of the sampling, the first order inclusion probabilities of the elements are strictly
proportional to their weight. However, the most of the :math:`k`-order inclusion probabilities are zero and elements
that appear consecutively in the ordering has almost no chance of being selected together, unless their weights are very
large.

Infeasibility
-------------
As the ordered systematic method satisfies the ratio estimator property, it suffers from the phenomenon of infeasibility
if at least one element has too large of a weight. This implementation, in particular the :class:`SystematicSampling`
will automatically check if the instance is infeasible and raise an exception accordingly. The unweighted version of the
method does not suffer from infeasibility.

Members
-------
Implementations are categorized based on two criteria:

* Whether the implementation refers to the weighted version or the unweighted version. Although the weighted variants
  are a generalization of unweighted variants, the unweighted implementations are typically faster and should be used
  when no weights are given.
* Whether the implementation is aware of the values of the elements of the population. The implementations that are not
  aware of the values of the elements of the population are typically faster and only return a samples of zero-based
  indices. The caller is responsible of maintaining a random access list of population values in this case. In contrast,
  implementations that are aware of the population values return samples of values (not indices) but occupy more memory
  to store the population as a random access list. They should be used when the elements of the population are not
  already inside a random access collection.

The table below summarizes these properties on the implementations.

================================================  ========  ==========
Implementation                                    Weighted  Population
================================================  ========  ==========
``class OrderedSystematic``                       True      False
``class OrderedSystematicPopulation``             True      True
``def ordered_systematic_unweighted``             False     False
``def ordered_systematic_unweighted_population``  False     True
================================================  ========  ==========

Usage
-----
Draw an unweighted random sample of 2 indices in the :math:`[0,5)` range:

.. code-block:: python

   print(list(ordered_systematic_unweighted(5, 2)))

Draw an unweighted random sampling of 2 elements from a population:

.. code-block:: python

   print(list(ordered_systematic_unweighted_population(['a', 'b', 'c', 'd', 'e'], 2)))

Draw a weighted sample of words in a sentence based on their appearance frequency:

.. code-block:: python

   sentence: str = "it was the best of times it was the worst of times"
   frequencies: typing.Counter[str] = Counter()
   for word in sentence.split():
       frequencies[word] += 1
   systematic_sampling: OrderedSystematicPopulation = OrderedSystematicPopulation()
   for (word, occurrences) in frequencies.items():
       systematic_sampling.push_item(word, occurrences)
   print(f"One sample: {list(systematic_sampling.sample(2))}")
   print(f"Another sample: {list(systematic_sampling.sample(2))}")

References
----------
.. [1] William G. Madow, Lillian H. Madow.
       On the theory of systematic sampling, I (1949).
"""

import bisect
import math
import random
import typing
from typing import Any

from rsx.utils.exceptions import BadWeightError
from rsx.utils.exceptions import InfeasibleCaseError


def ordered_systematic_unweighted(population: int, sample_size: int, rng: random.Random = None) -> typing.Iterator[int]:
    r"""
    Implementation of the unweighted version of ordered systematic sampling.

    The population items are assumed to be identified by their index and the generator returned by this method iterates
    through indices instead of population values. For example, for a sample with :math:`k = 5` from a population of
    :math:`n = 10`, the resulting generator may contain one of two possible states: :math:`[0,2,4,6,8]` or
    :math:`[1,3,5,7,9]` with 50% probability for each. This corresponds to the following call:

    .. code-block:: python

       ordered_systematic_unweighted(10, 5)

    This method runs faster than using weighted constructs and versions of the algorithm. Specifically, it runs in time
    :math:`\Theta(k)` to exhaust the returned generator and consumes constant extra memory.

    :param int population: the population
    :param int sample_size: the desired sample size
    :param Random rng: the random number generator (optional, default :code:`random.SystemRandom()`)
    :return: a sample of the population as a generator of their indices
    :rtype: Iterator[int]
    """
    if not 0 < sample_size <= population:
        raise ValueError("condition 0 < k <= n is not met")
    if rng is None:
        rng = random.SystemRandom()
    skip: float = population / sample_size
    current: float = rng.uniform(0, skip)
    for _ in range(sample_size):
        yield math.floor(current)
        current += skip


def ordered_systematic_unweighted_population(population: list[Any],
                                             sample_size: int,
                                             rng: random.Random = None) \
        -> typing.Iterator[int]:
    """
    Identical to the :func:`ordered_systematic_unweighted` method but using population values instead of population
    indices.

    In particular, this method accepts the population as a list of values instead of only its size. This function is
    simply a decorator around the :func:`ordered_systematic_unweighted` function:

    .. code-block:: python

       for index in ordered_systematic_unweighted(len(population), sample_size, rng):
           yield population[index]

    :param list[Any] population: the population as a list of elements
    :param int sample_size: the desired sample size
    :param rng: the random number generator (optional, default :code:`random.SystemRandom()`)
    :return: a sample of the population
    :rtype: Iterator[Any]
    """
    for index in ordered_systematic_unweighted(len(population), sample_size, rng):
        yield population[index]


class OrderedSystematic:
    r"""
    Implementation of the weighted version of Madow's ordered systematic sampling approach.

    The population items are identified by their zero-based index and the samples returned by the :meth:`sample` method
    refer to the indices of an implicit arrangement of elements in the :math:`[0,n)` range. Therefore, the caller is
    responsible of maintaining a random access list of the population elements (if such collection is relevant to the
    problem). Instances of this class operate exclusively with the weights of the elements and not the elements
    themselves.

    The caller may instantiate this class by optionally passing an iterable of the population weights in the
    constructor. If no such argument is given, the instance is initialized with no elements. The :math:`add_weight`
    method may be used to sequentially add additional weights into the instance. Finally, a sample can be drawn using
    the :meth:`sample` method, which returns a :class:`Generator` representing the sample as a series of population
    indices. The :meth:`sample` method may be called many times on the same instance and a different result might be
    returned.

    This class uses additional memory equal to :math:`\Theta(n)` because it stores the cumulative sum of the weights of
    the elements.
    """

    def __init__(self, initial_weights: typing.Iterable[float] = None) -> None:
        """
        Initialize an instance of this class, optionally using some initial weights.

        The initial weights iterable will not be mutated. It is a more convenient way to initialize the instance instead
        of calling the :meth:`add_weight` method after initialization. The constructor runs in time proportional to the
        number of entries in the :code:`initial_weights` iterable.

        :param Iterable[float] initial_weights: an iterable of the initial weights of the elements (optional, default is
                                                to leave the instance without any weights)
        """
        self.cumulative: list[float] = []
        self.largest_weight: float = -1
        if initial_weights is not None:
            for weight in initial_weights:
                self.push_weight(weight)

    def push_weight(self, weight: float) -> int:
        """
        Pushes a new weight into the instance and returns its position as a zero-based index.

        :param float weight: the weight of the new implicit element
        :return: the zero-based index of the element corresponding to the inserted weight
        :rtype: int
        """
        if weight <= 0:
            raise BadWeightError("weight must be positive")
        self.cumulative.append((0 if len(self.cumulative) == 0 else self.cumulative[-1]) + weight)
        self.largest_weight = max(self.largest_weight, weight)
        return len(self.cumulative) - 1

    def sample(self, sample_size: int, rng: random.Random = None) -> typing.Iterator[int]:
        r"""
        Draws a sample from the population based on the inserted weights and returns it as a :class:`Generator` of
        indices that correspond to the indices of the selected population elements.

        This method will raise an exception if the instance of the problem defined by the previously added weights is
        infeasible. This method runs in time :math:`\mathcal{O}(k \log n)` to fully exhaust the returned generator.

        :param int sample_size:
        :param Random rng:
        :return: a sample taken from the population as a generator of zero-based indices
        :rtype: Iterator[int]
        """
        if not 0 < sample_size <= len(self.cumulative):
            raise ValueError("condition 0 < k <= n not satisfied")
        if sample_size * self.largest_weight / self.cumulative[-1] > 1:
            raise InfeasibleCaseError("the problem is infeasible")
        if rng is None:
            rng = random.SystemRandom()
        skip: float = self.cumulative[-1] / sample_size
        current: float = rng.uniform(0, skip)
        last_yield: int = 0
        for _ in range(sample_size):
            last_yield = bisect.bisect_right(self.cumulative, current, lo=last_yield)
            yield last_yield
            current += skip


class OrderedSystematicPopulation:
    r"""
    Decorator around the :class:`OrderedSystematic` class that also stores the population elements, instead of only
    their weights.

    This class should be used when the population elements are not already in a random access container as, internally,
    this container will be created. The basic differences from the :class:`OrderedSystematic` class is that the
    :code:`add_weight` method has been replaced by the :meth:`add_item` method that additionally accepts the element
    value as argument, and the :meth:`sample` method returns a generator of element values instead of their indices.

    This class uses additional memory equal to :math:`\Theta(n)` because it stores a random access copy of the
    population elements along with the cumulative sum of their weights.
    """

    def __init__(self) -> None:
        """
        Initialize an instance of this class with no elements.
        """
        self.index_method: OrderedSystematic = OrderedSystematic()
        self.population: list[Any] = []

    def push_item(self, element: Any, weight: float) -> None:
        """
        Pushes a new element along with its weight into the instance.

        :param Any element: the value of the new element
        :param float weight: the weight of the new element
        """
        self.index_method.push_weight(weight)
        self.population.append(element)

    def sample(self, sample_size: int, rng: random.Random = None) -> typing.Iterator[Any]:
        r"""
        Draws a sample from the population based on the inserted weights and returns it as a :class:`Generator` of
        the population values that have been selected.

        This method will raise an exception if the instance of the problem defined by the previously added weights is
        infeasible. This method runs in time :math:`\mathcal{O}(k \log n)` to fully exhaust the returned generator.

        :param int sample_size:
        :param Random rng:
        :return: a sample taken from the population as a generator of the selected population elements
        :rtype: Iterator[Any]
        """
        for random_index in self.index_method.sample(sample_size, rng):
            yield self.population[random_index]
