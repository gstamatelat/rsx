r"""
Implementation of unweighted reservoir-based random sampling algorithms.

The reservoir algorithms take a sample of size :math:`k` from a population of size :math:`n`, where :math:`n` is either
very large or unknown. The population is treated like a stream of elements while the reservoir sampling algorithms
operate using a single pass over the population.

Complexity
----------
Reservoir-based algorithms use an auxiliary data structure (the *reservoir*), which is an online version of the sample
regardless of the time. As a result, they use :math:`\mathcal{O}(k)` extra space. Furthermore, the time taken to process
a single element from the stream is independent of the size of the stream although the number of RNG invocations vary
among the different implementations.

Duplicates
----------
A reservoir-based algorithm does not keep track of duplicate elements because that would result in a linear memory
complexity. Thus, it is valid to put the same element multiple times in the same instance and the algorithms will treat
these elements as different. This also holds true for the case where the same references are put into the instance.

Precision
---------
Many implementations have an accumulating state which causes the precision of the algorithms to degrade as the stream
becomes bigger. An example might be a variable state which strictly increases or decreases as elements are read from the
stream. Because the implementations use finite precision data types (usually double or long), this behavior causes the
precision of these implementations to degrade as the stream size increases.

Interface
---------
Reservoir-based sampling algorithms are implemented as classes and they implement the API specified by the
:class:`ReservoirSampling <rsx.reservoir.reservoir_sampling.ReservoirSampling>` class. Furthermore, the
:class:`AbstractReservoirSampling <rsx.reservoir.reservoir_sampling.AbstractReservoirSampling>` class is an abstract
implementation of :class:`ReservoirSampling <rsx.reservoir.reservoir_sampling.ReservoirSampling>` using the concept of
skips that decide how many elements to skip rather than deciding individually for each element whether to include it in
the reservoir.
"""
