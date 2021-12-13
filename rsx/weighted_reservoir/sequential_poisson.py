r"""
Implementation of the sequential Poisson order sampling algorithm by Ohlsson in [1]_.

This algorithm does not satisfy the ratio estimator property but is an approximation of it. The weights accepted by this
implementation are in the range :math:`(0, \infty)`. This is an implementation of :class:`OrderSampling
<rsx.weighted_reservoir.order_sampling.OrderSampling>` where the keys are equal to

.. math::

   \frac{w}{r}.

The default weight is :math:`1.0`.

References
----------
.. [1] Esbjörn Ohlsson.
       Sequential Sampling from a Business Register and its Application to the Swedish Consumer Price Index (1990).
"""

from math import isfinite
from random import Random

from rsx.utils.helper import random_exclusive
from rsx.weighted_reservoir.order_sampling import OrderSampling


class SequentialPoissonSampling(OrderSampling):
    r"""
    Implementation of the sequential Poisson order sampling algorithm by Ohlsson as a class.

    The space complexity of this class is :math:`\mathcal{O}(k)`, where :math:`k` is the sample size.
    """

    def _key(self, weight: float, rng: Random):
        return weight / random_exclusive(rng)

    def _is_weight_legal(self, weight: float):
        return isfinite(weight) and weight > 0

    def _default_weight(self):
        return 1.0
