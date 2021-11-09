"""
Contains the implementation of the :class:`ReservoirSampling` abstract base class of all unweighted reservoir sampling
algorithms.
"""

from abc import ABC, abstractmethod
from typing import Any
from typing import Iterable
from typing import Sequence


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

        The reservoir cannot be ``None`` but it can be empty if no elements have been put in the instance. This method
        always returns the same reference and runs in constant time.

        :return: the reservoir of this instance
        :rtype: Sequence[Any]
        """
        raise NotImplementedError
