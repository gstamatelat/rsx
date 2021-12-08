r"""
Implementation of the Pareto order sampling algorithm by Rosén in [1]_ and [2]_.

This algorithm does not satisfy the ratio estimator property but is an approximation of it. The weights are defined to
be the first order inclusion probabilities of the elements but in this reservoir sampling implementation these
probabilities cannot be computed in advance. Therefore, as a compromise, the weights accepted by this implementation are
in :math:`(0,1)`. This is an implementation of :class:`OrderSampling
<rsx.weighted_reservoir.order_sampling.OrderSampling>` where the keys are equal to

.. math::

   \frac{(1-r) w}{r (1-w)}.

The default weight is :math:`0.5`.

References
----------
.. [1] Bengt Rosén.
       On sampling with probability proportional to size (1997).
.. [2] Bengt Rosén.
       Asymptotic theory for order sampling (1997).
"""

from random import Random

from rsx.utils.helper import random_exclusive
from rsx.weighted_reservoir.order_sampling import OrderSampling


class ParetoSampling(OrderSampling):
    r"""
    Implementation of the Pareto order sampling algorithm by Rosén as a class.

    The space complexity of this class is :math:`\mathcal{O}(k)`, where :math:`k` is the sample size.
    """

    def _key(self, weight: float, rng: Random):
        r: float = random_exclusive(rng)  # pylint: disable=invalid-name
        return ((1 - r) * weight) / (r * (1 - weight))

    def _is_weight_legal(self, weight: float):
        return 0 < weight < 1

    def _default_weight(self):
        return 0.5
