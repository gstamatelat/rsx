"""
Contains the :class:`WeightedReservoirSampling` abstract base class of all weighted reservoir sampling algorithms and
its abstract class :class:`AbstractWeightedReservoirSampling` that simplifies the implementation of
:class:`WeightedReservoirSampling`.
"""

from abc import ABC, abstractmethod
from typing import Any
from typing import Collection
from typing import Iterable


class WeightedReservoirSampling(ABC):
    r"""
    Base class for all weighted reservoir sampling algorithms.

    The space complexity of all classes deriving from the base class is :math:`\mathcal{O}(k)`, where :math:`k` is the
    sample size.
    """

    @abstractmethod
    def put(self, element: Any, weight: float = None) -> bool:
        """
        Put an element in this instance.

        The algorithm will determine whether the element will be included in the reservoir. This probability depends on
        the weight of the element given. The default weight (if no such value is given) depends on the implementation.

        :param Any element: the element to put in this instance
        :param float weight: the weight of the element (optional, default depends on the implementation)
        :return: ``True`` if the element was inserted into the reservoir, ``False`` otherwise
        :rtype: bool
        """
        raise NotImplementedError

    @abstractmethod
    def put_iterable(self, elements: Iterable[Any], weights: Iterable[float] = None) -> bool:
        """
        Puts all the items of an :class:`Iterable` in this instance in the order at which they are returned by its
        iterator.

        The weights of the elements are given through the ``weights`` parameter. If the weights are not given, the
        default weight of the implementation will be used. If the ``elements`` and ``weights`` iterables do not contain
        exactly the same number of elements, then the iteration will stop at the shortest of the iterables. This method
        returns ``True`` if the reservoir was changed as a result of this operation (if any individual :meth:`put` calls
        returned ``True``), otherwise ``False``.

        :param Iterable[Any] elements: the iterable containing the items to be put in the instance
        :param Iterable[float] weights: the iterable containing the weights of the elements (optional, default depends
                                        on the implementation)
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
    def sample(self) -> Collection[Any]:
        """
        Returns a read-only view of the reservoir of this instance.

        The reservoir cannot be ``None`` but it can be empty if no elements have been put in the instance. This method
        always returns the same reference and runs in constant time.

        :return: the reservoir of this instance
        :rtype: Collection[Any]
        """
        raise NotImplementedError


class AbstractWeightedReservoirSampling(WeightedReservoirSampling, ABC):
    """
    Abstract implementation of :class:`WeightedReservoirSampling` that minimizes the effort to implement the base class.

    This abstract class implements the :meth:`put_iterable` method.
    """

    def put_iterable(self, elements: Iterable[Any], weights: Iterable[float] = None) -> bool:
        changed: bool = False
        if weights is None:
            for element in elements:
                if self.put(element=element, weight=None):
                    changed = True
        else:
            for (element, weight) in zip(elements, weights):
                if self.put(element=element, weight=weight):
                    changed = True
        return changed
