"""
Contains the implementation of the :class:`ReservoirSampling` abstract base class of all unweighted reservoir sampling
algorithms and the :class:`AbstractReservoirSampling` abstract class that simplifies the implementation of
:class:`ReservoirSampling` using the concept of skips.
"""

from abc import ABC, abstractmethod
from random import Random
from random import SystemRandom
from typing import Any
from typing import Callable
from typing import Iterable
from typing import Iterator
from typing import Sequence

from rsx.utils.helper import SequenceDecorator


class ReservoirSampling(ABC):
    r"""
    Base class for all unweighted reservoir sampling algorithms.

    The space complexity of all classes deriving from the base class is :math:`\mathcal{O}(k)`, where :math:`k` is the
    sample size.
    """

    @abstractmethod
    def put(self, element: Any) -> bool:
        """
        Put an element in this instance.

        The algorithm will determine whether the element will be included in the reservoir.

        :param Any element: the element to put in this instance
        :return: ``True`` if the element was inserted into the reservoir, ``False`` otherwise
        :rtype: bool
        """
        raise NotImplementedError

    @abstractmethod
    def put_iterable(self, iterable: Iterable[Any]) -> bool:
        """
        Puts all the items of an :class:`Iterable` in this instance in the order at which they are returned by its
        iterator.

        Returns ``True`` if the reservoir was changed as a result of this operation (if any individual :meth:`put` calls
        returned ``True``), otherwise ``False``.

        :param Iterable[Any] iterable: the iterable containing the items to be put in the instance
        :return: a value indicating whether the reservoir was changed as a result of this operation
        :rtype: bool
        """
        raise NotImplementedError

    @abstractmethod
    def put_sequence(self, sequence: Sequence[Any]) -> bool:
        """
        Puts all the items of a :class:`Sequence` in this instance in the order at which they are returned by its
        iterator.

        This method is identical to :meth:`put_iterable` in terms of its operation but may run in sublinear time. This
        is due to the fact that the input is known to support fast random access and the skip can be performed more
        efficiently. As a result, it must be preferred over :meth:`put_iterable` when the population is known to be in
        a random access container (such as a :class:`list`).

        :param Sequence[Any] sequence: the sequence containing the items to be put in the instance
        :return: a value indicating whether the reservoir was changed as a result of this operation
        :rtype: bool
        """
        raise NotImplementedError

    @abstractmethod
    def sample_size(self) -> int:
        """
        Returns the size of the sample that this instance was created with.

        The value returned by this method may be less than ``len(sample())`` if less than ``sample_size()`` items have
        been put in the instance.

        :return: the size of the sample that this instance was created with
        :rtype: int
        """
        raise NotImplementedError

    @abstractmethod
    def stream_size(self) -> int:
        """
        Returns the number of elements that have been put in the instance during its lifetime.

        :return: the number of elements that have been put in the instance during its lifetime.
        :rtype: int
        """
        raise NotImplementedError

    @abstractmethod
    def sample(self) -> Sequence[Any]:
        """
        Returns a read-only view of the reservoir of this instance.

        The returned collection is a :class:`Sequence <collections.abc.Sequence>` but the elements are in no particular
        order inside the collection. Because the ``__eq__`` operator in sequences is implemented by considering the
        order of the elements, this may create a situation where two samples containing the same elements do not
        evaluate as equal because of different order. As an aid, the :func:`sequence_equals
        <rsx.utils.helper.sequence_equals>` function can be used to determine whether two sequences contain the same
        elements.

        The reservoir cannot be ``None`` but it can be empty if no elements have been put in the instance. This method
        always returns the same reference and runs in constant time.

        :return: the reservoir of this instance
        :rtype: Sequence[Any]
        """
        raise NotImplementedError


class AbstractReservoirSampling(ReservoirSampling):
    """
    Abstract implementation of :class:`ReservoirSampling` with the concept of skips.
    """

    def __init__(self,
                 skip_function: Callable[[int, Random], Iterator[int]],
                 sample_size: int,
                 rng: Random = None) -> None:
        """
        The constructor initializes this instance with an empty reservoir using the desired sample size and the skip
        function.

        The skip function ``skip_function`` represented by the callable argument is a function that accepts the sample
        size as the first argument and a random number generator as the second argument. Using these two quantities,
        the function returns a (possibly infinitely sized) :class:`Iterator` of integers that represents the consecutive
        skips of elements before one gets accepted in the reservoir (starting from the point where the reservoir fully
        fills for the first time). For example, if ``sample_size = 5`` and the iterator returned by the skip function
        yields the values 1, 0, 2, 0, 4, then the boolean vector indicating whether the respective element will be
        accepted in the reservoir is:

        .. code-block::

           1, 1, 1, 1, 1, 0, 1, 1, 0, 0, 1, 1, 0, 0, 0, 0, 1

        The skip function callable memory usage must not depend on the sample size, i.e. must be constant.

        :param Callable[[int, Random], Iterator[int]] skip_function: the skip function described
        :param int sample_size: the desired sample size
        :param Random rng:  the random number generator (optional, default ``random.SystemRandom()``)
        """
        if sample_size < 1:
            raise ValueError("sample_size must be >= 1")
        self.__sample_size: int = sample_size
        self.__stream_size: int = 0
        if rng is None:
            self.__rng: Random = SystemRandom()
        else:
            self.__rng = rng
        self.__reservoir: list[Any] = []
        self.__reservoir_view: Sequence[Any] = SequenceDecorator(self.__reservoir)
        self.__skip_function: Iterator[int] = skip_function(sample_size, self.__rng)
        self.__skip: int = next(self.__skip_function)

    def __put(self, element: Any) -> None:
        self.__reservoir[self.__rng.randrange(0, self.__sample_size)] = element

    def put(self, element: Any) -> bool:
        if element is None:
            raise ValueError("element was None")
        self.__stream_size += 1
        if len(self.__reservoir) < self.__sample_size:
            self.__reservoir.append(element)
            return True
        if self.__skip > 0:
            self.__skip -= 1
            return False
        self.__put(element)
        self.__skip = next(self.__skip_function)
        return True

    def put_iterable(self, iterable: Iterable[Any]) -> bool:
        changed: bool = False
        for element in iterable:
            if self.put(element):
                changed = True
        return changed

    def put_sequence(self, sequence: Sequence[Any]) -> bool:
        return_value = False
        offset: int = 0
        while offset < len(sequence) and len(self.__reservoir) < self.__sample_size:
            self.__reservoir.append(sequence[offset])
            return_value = True
            offset += 1
        while len(sequence) > offset + self.__skip:
            offset += self.__skip
            self.__put(sequence[offset])
            self.__skip = next(self.__skip_function)
            offset += 1
            return_value = True
        self.__skip -= len(sequence) - offset
        return return_value

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
