r"""
Implementation of weighted reservoir-based random sampling algorithms.

Weighted reservoir algorithms have all the characteristics of complexity, duplicates and precision of unweighted
reservoir algorithms (see :mod:`rsx.reservoir <rsx.reservoir>`) but additionally assign a weight to each of the elements
of the population that affects the probability of that element to be placed in the reservoir.

Weights
-------
The interpretation of the weight may be different for each implementation as is the case for all weighted random
sampling methods and implementations in this package may not exhibit identical behavior, especially with respect to
the first order inclusion probabilities. The contract is, however, that a higher weight value suggests a higher
probability for an item to be included in the sample. Implementations may also define certain restrictions on the values
of the weight and violations will result in :class:`BadWeightException <rsx.utils.exceptions.BadWeightException>`.
"""
