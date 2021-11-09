"""
Implementation of Jessen's *Method 2* of whole sampling published in [1]_.

Jessen's method works by constructing a tableau of samples during preprocessing and allowing this tableau to be queried
in constant time. This algorithm is implemented using the builder pattern. The :class:`JessenBuilder` class simulates
the preprocessing stage of creating the tableau. It allows the user to enter the population details (population values
and weights) and generate instances of the :class:`JessenSampling` class that are used to query for random samples in
constant time. The samples themselves are returned by the latter class as instances of :class:`JessenSample` which is a
read-only decorator around a list in order to protect the caller from accidental mutation of the samples stored in the
tableau.

Builder Pattern Motivation
--------------------------
The purpose of the builder class and this design in general is to create an environment via which the generation of
:class:`JessenSampling` instances can accommodate the requirements of individual usage scenarios without compromising
cpu and memory usage. In particular, the requirements refer to how the arguments of the population are accepted by the
sampling method. For example one caller might have the population elements along with their weights in a dictionary,
another caller might have them in two separate lists etc. A limiting situation is when the population or the
probabilities of the population elements are not readily available, for example they are generated via a loop. In that
case, the caller might be willing to copy the values first in a concrete data structure and pass it on the sampling
method. Due to the sampling method implementation relying on specific data structures, those values would have to be
copied again internally. This class addresses this situation by unifying the formats of the sample size, the population
and the population probabilities. As a result, each instance holds these values and can generate instances of the
:class:`JessenSampling` class based on them.

Duplicate Items
---------------
The implementation assures no uniqueness of the population elements. If the same element is inserted into the population
more than once, the resulting samples may have duplicate items. If uniqueness is desired, the caller must enforce it.
Also see the relevant comment in the :class:`JessenBuilder` class.

Infeasibility
-------------
Jessen's algorithm satisfies the ratio estimator property and is susceptible to infeasibility cases. These cases will
fail with error during the execution of the :meth:`JessenBuilder.build() <JessenBuilder.build>` method.

Example
-------
Select a sample of 2 words from a sentence based on their frequency of appearance:

.. code-block:: python

   sentence: str = "we few we happy few we band of brothers"
   counter: Counter[str] = Counter(sentence.split())
   jessen: JessenSampling = JessenBuilder().add_dictionary(counter).build(2)  # Build the instance
   print(jessen.sample())  # We can query many times ...
   print(jessen.sample())  # ... with very little cost

References
----------
.. [1] R. J. Jessen.
       Some methods of probability non-replacement sampling (1969).
"""

from __future__ import annotations

import functools
import heapq
import random
from typing import Any
from typing import Callable
from typing import Iterable
from typing import Iterator
from typing import Mapping
from typing import Tuple
from typing import Union

from rsx.utils.alias import AliasMethod
from rsx.utils.exceptions import BadWeightError
from rsx.utils.exceptions import InfeasibleCaseError
from rsx.utils.helper import SequenceDecorator


@functools.total_ordering
class _Weighted:
    def __init__(self, value: object, weight: float):
        self.value: object = value
        self.weight: float = weight

    def __lt__(self, other) -> bool:
        return self.weight.__lt__(other.weight)

    def __eq__(self, other) -> bool:
        return self.weight.__eq__(other.weight)


class JessenSample(SequenceDecorator):
    """
    Represents a sample from the sample space of Jessen's algorithm.

    This class is actually a read-only decorator around a list that represents the sample and implements the interface
    of the :class:`Sequence <typing.Sequence>` abstract data type. Therefore, it can be used on foreach loops, random
    access using the bracket operator etc. It has constant time random access, constant time advancement of its iterator
    and linear time contains check.
    """

    def __init__(self, sample: list[Any]) -> None:  # pylint: disable=useless-super-delegation
        """
        The constructor initializes a new instance of this class as a decorator of the given underlying list in constant
        time. The instance created will be backed by that list.

        :param list[Any] sample: the underlying sample to create this decorator from
        """
        super().__init__(sample)


class JessenBuilder:
    """
    Represents a builder object that can generate instances of the :class:`JessenSampling` class.

    The class contains various ``add`` methods that can be used to insert elements of the population in the instance
    along with their weights. These methods do not replace existing elements nor operate additively to existing elements
    when called with the same element twice. For example the calls

    .. code-block:: python

       .add(item=x, weight=1)
       .add(item=x, weight=2)

    will create a population of two elements with the same value and different weights. As a result, the samples that
    correspond to this population may have duplicate elements too. The caller must ensure uniqueness if this behavior
    is desired. All of the add methods return a pointer to the instance itself for use in invocation chains and run in
    time proportional to the number of elements added.

    After the desired population has been added, the :meth:`build` method may be called to build the sample space and
    pass it over to the returned instance of the :class:`JessenSampling` class. The :meth:`build` method will also reset
    this instance by erasing all items in the population. The memory footprint of this class is proportional to the
    size of the population inserted in it.
    """

    def __init__(self):
        """
        The constructor initializes a new builder with no items in the population and runs in constant time.
        """
        self.__heap: list[_Weighted] = []
        self.__weight_sum: float = 0

    def add(self, item: object, weight: float) -> JessenBuilder:
        """
        Adds a single population item in the instance along with its weight.

        :param object item: the item
        :param float weight: the weight of the unit
        :return: the instance itself
        :rtype: JessenBuilder
        """
        if weight <= 0:
            raise BadWeightError("weight must be strictly positive")
        self.__heap.append(_Weighted(item, weight))
        self.__weight_sum += weight
        return self

    def add_weights(self, weights: Union[Iterator[float], Iterable[float]]) -> JessenBuilder:
        """
        Adds a series of :math:`n` weights that correspond the the implicit population integer values in :math:`[0,n)`.

        This method is equivalent to

        .. code-block:: python

           add_range(itertools.count(), weights)

        If given an infinite iterator as input, this method will run forever.

        :param Union[Iterator[float], Iterable[float]] weights: a series of weights to add as corresponding weights to
                                                                the implicit population
        :return: the instance itself
        :rtype: JessenBuilder
        """
        for i, weight in enumerate(weights):
            self.add(i, weight)
        return self

    def add_range(self,
                  population: Union[Iterator[object], Iterable[object]],
                  weights: Union[Iterator[float], Iterable[float]]) -> JessenBuilder:
        """
        Adds a series of population elements from the given iterator (or iterable) and their respective weights as
        another iterator.

        This method accepts Python :class:`ranges <range>` or various methods of :mod:`itertools` (for example
        :func:`itertools.count() <itertools.count>`) as targets of the first argument. If the arguments don't have
        exactly the same number of elements, the items added will be determined by the minimum length of the given
        iterators and the rest of the elements will be silently discarded. This method is equivalent to

        .. code-block:: python

           for element, weight in zip(population, weights):
               self.add(element, weight)
           return self

        If both inputs are infinite iterators, this method will run forever.

        :param Union[Iterator[object], Iterable[object]] population: the population items
        :param Union[Iterator[float], Iterable[float]] weights: the weights of the the population
        :return: the instance itself
        :rtype: JessenBuilder
        """
        for element, weight in zip(population, weights):
            self.add(element, weight)
        return self

    def add_mapping(self,
                    population: Union[Iterator[object], Iterable[object], int],
                    weights: Callable[[object], float]) -> JessenBuilder:
        r"""
        Adds a series of population of elements from the given iterator (or iterable) and a mapping function the returns
        the weight of each of these elements.

        As an example, the following code will add the 5 integer valued elements :math:`[1,5]` in the instance, where
        the inclusion probability of element :math:`i` is proportional to :math:`\ln(i) + 1`:

        .. code-block:: python

           add_mapping(range(1, 6), lambda x: math.log(x) + 1)

        :param Union[Iterator[object], Iterable[object], int] population: the population items
        :param Callable[[object], float] weights: a mapping function that takes a population element and returns its
                                                  weight
        :return: the instance itself
        :rtype: JessenBuilder
        """
        if isinstance(population, int):
            population = range(population)
        for item in population:
            self.add(item, weights(item))
        return self

    def add_dictionary(self, population: Mapping[object, float]) -> JessenBuilder:
        """
        Adds the population corresponding to the keys of the given dictionary, where the values correspond to their
        weights.

        Example:

        .. code-block:: python

           add_dictionary({'a': 1, 'b': 2, 'c': 1, 'd': 2})

        :param Mapping[object, float] population: a mapping of the population elements with their weights
        :return: the instance itself
        :rtype: JessenBuilder
        """
        for item, weight in population.items():
            self.add(item, weight)
        return self

    def reset(self) -> None:
        """
        Resets the instance by clearing all population elements and completely resetting its state to the initial one.
        This method exists mostly in case the infeasible case exception raised by the :meth:`build` method needs to be
        caught.
        """
        self.__heap.clear()
        self.__weight_sum = 0

    def build(self, sample_size: int) -> JessenSampling:
        r"""
        Creates and returns a new instance of :class:`JessenSampling` based on the population inserted in this instance.

        This method will reset the instance by emptying the population and it can be reused for further builds. It will
        raise an exception if the problem represented by this instance is infeasible. This method runs in time
        :math:`\mathcal{O}(k n \log n)`, where :math:`n` is the population size and :math:`k` is the sample size. The
        returned :class:`JessenSampling` instance will consume :math:`\mathcal{O}(nk)` memory.

        In case of an infeasible problem case, an :class:`InfeasibleCaseError
        <rsx.utils.exceptions.InfeasibleCaseError>` error will be raised. In this case, the exception should not be
        caught as it can cause the instance to behave incorrectly in the future. The reason for this is the intermediate
        step of weight normalization that checks for feasibility. In case the infeasibility is detected, the population
        will contain some normalized and some non-normalized values. In case the exception is caught, the instance
        should be reset using the :meth:`reset` method.

        :param int sample_size: the desired sample size
        :return: a new :class:`JessenSampling` instance using the population added in this instance
        :rtype: JessenSampling
        """
        # Check sizes
        if not 0 < sample_size <= len(self.__heap):
            raise ValueError("condition 0 < k <= n not satisfied")

        # Normalize weights
        for weighted in self.__heap:
            normalized_weight = weighted.weight * sample_size / self.__weight_sum
            if normalized_weight > 1:
                raise InfeasibleCaseError(f"infeasible case for element {weighted.value}")
            weighted.weight = -normalized_weight

        # Define sample space and probabilities
        sample_space: list[list[object]] = []
        sample_probabilities: list[float] = []

        # Build the sample space
        heapq.heapify(self.__heap)
        overall_balance: float = 1.0
        while len(self.__heap) >= sample_size:
            new_weighted: list[_Weighted] = []
            new_sample: list[object] = []
            for _ in range(sample_size):
                popped: _Weighted = heapq.heappop(self.__heap)
                new_weighted.append(popped)
                new_sample.append(popped.value)
            reduce_by: float = min(-new_weighted[-1].weight, overall_balance + self.__heap[0].weight) \
                if self.__heap else -new_weighted[-1].weight
            if reduce_by == 0:
                break
            for new_tuple in new_weighted:
                if new_tuple.weight + reduce_by < 0:
                    new_tuple.weight = new_tuple.weight + reduce_by
                    heapq.heappush(self.__heap, new_tuple)
            sample_space.append(new_sample)
            sample_probabilities.append(reduce_by)
            overall_balance -= reduce_by

        # Reset the instance so that it is ready for the next build
        self.reset()

        # Return the new sampling instance
        return JessenSampling(sample_space, sample_probabilities)


class JessenSampling:
    """
    The querying part of the implementation of Jessen's algorithm.

    Instances of this class are returned by the :meth:`JessenBuilder.build() <JessenBuilder.build>` method and their
    memory footprint depends on the builder that created them.
    """

    def __init__(self, sample_space: list[list[object]], sample_probabilities: list[float]) -> None:
        """
        The constructor initializes the instance with the given sample space and their respective probabilities. No
        checks are performed on the arguments. In runs in linear time due to the initialization of the alias method
        tables.

        :param list[list[object]] sample_space: the sample space
        :param list[float] sample_probabilities: the respective probabilities of each sample in the sample space
        """
        self.__alias: AliasMethod = AliasMethod(sample_probabilities)
        self.__sample_space: list[list[object]] = sample_space
        self.__sample_probabilities: list[float] = sample_probabilities

    def sample_space(self) -> Iterator[Tuple[JessenSample, float]]:
        """
        Returns an :class:`iterator <typing.Iterator>` over all the samples in the sampling space.

        The iterator comprises tuples of elements where the first element corresponds to the sample and the second
        element corresponds to its probability. The probabilities of all samples sum to (approximately) unity. The
        returned iterator advances the enumeration in constant time.

        :return: an :class:`iterator <typing.Iterator>` over all the samples in the sampling space.
        :rtype: Iterator[Tuple[JessenSample, float]]
        """
        for (sample, probability) in zip(self.__sample_space, self.__sample_probabilities):
            yield JessenSample(sample), probability

    def sample(self, rng: random.Random = None) -> JessenSample:
        """
        Randomly chooses a sample from the sample space and returns it.

        This method return an object of type :class:`JessenSample`, which is a read-only view of the sample and
        implements the :class:`typing.Sequence` interface. As per the contract of whole sampling, this method runs in
        constant time.

        :param Random rng: the random number generator to use (optional, default ``random.SystemRandom()``)
        :return: the chosen sample
        :rtype: JessenSample
        """
        return JessenSample(self.__sample_space[self.__alias.sample(rng)])

    def _internal_state(self) -> Tuple[list[list[object]], list[float]]:
        """
        Returns the internal state of the instance in a mutable form.

        The internal state comprises a tuple of the sample space and their respective probabilities. The sample space is
        a list of lists, where each one of the encapsulated lists represents the sample and an equal length list of
        float values storing the corresponding probabilities.

        .. warning::

           Invoking this method is dangerous as it may break the instance. In particular if the objects returned are
           modified, even slightly, this will result in undefined behavior of the instance, for example future calls may
           result in errors or wrong behavior. The instance must not be used after changing the internal state.

        This method exists to address situations where the programmer requires access to the underlying structures of
        this instance returned by the method :meth:`sample_space` without having to copy them in a new container.

        :return: the internal state of the instance as a tuple of the sample space and their respective probabilities
        :rtype: Tuple[list[list[object]], list[float]]
        """
        return self.__sample_space, self.__sample_probabilities
