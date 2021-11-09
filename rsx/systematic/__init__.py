r"""
Implementation of weighted systematic random sampling algorithms.

Systematic sampling is the process at which the population is sampled every :math:`s`-th element while the process
starts from a random index. The :math:`s` variable itself is set based on criteria of the problem, such as the
(constant) sample size, the population size, or other parameters of the elements of the population. The weighted version
of the systematic approach is to sample every :math:`s` amount of weight in the implicit ordering of the population
elements.

Inclusion Probabilities
-----------------------
Due to their operation, the systematic sampling designs obey the ratio estimator property and the inclusion
probabilities of individual elements of the population are strictly proportional to their weight. Typically, however,
because the population is sampled systematically, most of the :math:`k`-order inclusion probabilities are zero in most
of the implementations.

Infeasibility
-------------
Because the systematic family of algorithms satisfy the ratio estimator property, each of the individual first order
inclusion probabilities are strictly proportional to the weight of the respective elements. As a result, there are
infeasible instances if the maximum element weight of the population is greater than :math:`k/Z`, where :math:`k` is the
desired sample size and :math:`Z` is the sum of the weights of the population. Such requirements may be imposed by the
implementations but may not be.
"""
