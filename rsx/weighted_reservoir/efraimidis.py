r"""
Implementation of the algorithm by Efraimidis and Spirakis in [1]_.

This algorithm does not satisfy the ratio estimator property but is an approximation of it. The interpretation of the
weights coincides with the selection probabilities on each implicit round of selections with replacement. Weights must
be in the range :math:`(0, \infty)` and the default weight in this implementation is :math:`1.0`.

References
----------
.. [1] Pavlos S. Efraimidis, Paul G. Spirakis
       Weighted random sampling with a reservoir (2005).
"""

from math import isfinite
from random import Random

from rsx.utils.helper import random_exclusive
from rsx.weighted_reservoir.order_sampling import OrderSampling


class EfraimidisSampling(OrderSampling):
    r"""
    Implementation of the algorithm by Efraimidis and Spirakis as a class.

    The space complexity of this class is :math:`\mathcal{O}(k)`, where :math:`k` is the sample size.
    """

    def _key(self, weight: float, rng: Random):
        return pow(random_exclusive(rng), 1 / weight)

    def _is_weight_legal(self, weight: float):
        return isfinite(weight) and weight > 0

    def _default_weight(self):
        return 1.0
