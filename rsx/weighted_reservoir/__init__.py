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

Interface
---------
Reservoir-based sampling algorithms are implemented as classes and they implement the API specified by the
:class:`WeightedReservoirSampling <rsx.weighted_reservoir.weighted_reservoir_sampling.WeightedReservoirSampling>` class.
Furthermore, the :class:`WeightedAbstractReservoirSampling
<rsx.weighted_reservoir.weighted_reservoir_sampling.AbstractWeightedReservoirSampling>` class is an abstract
implementation of :class:`WeightedReservoirSampling
<rsx.weighted_reservoir.weighted_reservoir_sampling.WeightedReservoirSampling>` with the most basic functionality of
weighted reservoir sampling.

Usage
-----
Since all weighted reservoir implementations follow the exact same interface, they can be used interchangeably in the
following code snippets.

1. Select 2 terms from a vocabulary, based on their weight:

   .. code-block:: python

      rs: WeightedReservoirSampling = EfraimidisSampling(2)
      rs.put("collection", 1)
      rs.put("algorithms", 2)
      rs.put("python", 2)
      rs.put("random", 3)
      rs.put("sampling", 4)
      rs.put("reservoir", 5)
      print(rs.sample())

2. The same example using the ``put_iterable`` API:

   .. code-block:: python

      d: dict[str, int] = {
          "collections": 1,
          "algorithms":  2,
          "python":      2,
          "random":      3,
          "sampling":    4,
          "reservoir":   5
      }
      rs: WeightedReservoirSampling = EfraimidisSampling(2)
      rs.put_iterable(d.keys(), d.values())
      print(rs.sample())
"""
