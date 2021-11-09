"""
Implementation of the Welford's online variance algorithm [1]_.

The method computes the variance of a sample in one pass using constant memory and allows querying the variance at any
point.

Usage
-----

The following example demonstrates the usage of this class. Random values that are normally distributed with standard
deviation 2 are streamed through an instance of :class:`~sampling.utils.welford_variance.WelfordVariance` until the
standard error falls below 0.001. The variance of the population is then a value very close to 4.

.. code-block:: python

   import random
   wf: WelfordVariance = WelfordVariance()
   while wf.observations() < 2 or wf.population_standard_error() > 0.001:
       wf.add(random.normalvariate(0, 2))
   print(wf.population_variance()) # Prints a value very close to 4

References
----------
.. [1] B. P. Welford.
       Note on a method for calculating corrected sums of squares and products (1962).
"""

import math


class WelfordVariance:
    """
    Implementation of the Welford's online variance algorithm as a class.
    """

    def __init__(self):
        """
        Construct an empty new instance of this class with no observations.
        """
        self.__sum: float = 0
        self.__observations: int = 0
        self.__m = 0

    def add(self, observation: float):
        """
        Add an observation.

        This method updates the state of the instance to reflect the new observation added.

        :param float observation: the observation
        """
        previous_mean: float = self.__sum / self.__observations if self.__observations != 0 else 0

        self.__observations += 1
        self.__sum += observation

        next_mean: float = self.__sum / self.__observations
        self.__m += (observation - next_mean) * (observation - previous_mean)
        assert self.__m >= 0

    def observations(self) -> int:
        """
        Returns the total number of observations that have been added in this instance.

        :return: the total number of observations that have been added in this instance
        :rtype: int
        """
        return self.__observations

    def sum(self) -> float:
        """
        Returns the sum of all observations that have been added in this instance.

        :return: the sum of all observations that have been added in this instance
        :rtype: float
        """
        return self.__sum

    def population_variance(self) -> float:
        """
        Returns the population variance of the observations that have been added to this instance.

        :return: the population variance of the observations that have been added to this instance
        :rtype: float
        """
        return self.__m / self.__observations

    def sample_variance(self) -> float:
        """
        Returns the sample variance of the observations that have been added to this instance.

        :return: the sample variance of the observations that have been added to this instance
        :rtype: float
        """
        return self.__m / (self.__observations - 1)

    def population_standard_error(self) -> float:
        """
        Returns the population standard error.

        The population standard error is the square root of the population variance over the number of observations.

        :return: the population standard error
        :rtype: float
        """
        return math.sqrt(self.population_variance() / self.__observations)

    def sample_standard_error(self) -> float:
        """
        Returns the sample standard error.

        The sample standard error is the square root of the sample variance over the number of observations.

        :return: the sample standard error
        :rtype: float
        """
        return math.sqrt(self.sample_variance() / self.__observations)

    def mean(self) -> float:
        """
        Returns the mean value of the observations that have been added to this instance.

        :return: the mean value of the observations that have been added to this instance
        :rtype: float
        """
        return self.__sum / self.__observations
