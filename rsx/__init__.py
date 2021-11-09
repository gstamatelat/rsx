"""
Random sampling is the process of selecting a subset of units from a larger population using some amount of randomness.
This package is devoted to this problem and contains a collection of algorithms for its solution.

Categorization
--------------
Algorithms are categorized based on their interface, which often dictates their performance characteristics and
applicability.

#. Simple sampling is a category of unweighted algorithms that have uniform first order and higher order inclusion
   probabilities. They sample from a concrete population that usually has to allow random access.
#. Systematic sampling is a class of sampling algorithms where a sample is taken based on constant size jumps over the
   population. These are weighted algorithms that require a concrete population with random access.
#. Whole sampling procedures operate in two phases. First they build a sample space given the population weighted
   elements. Then, samples can be queried in constant time.
#. Reservoir algorithms is a special class of sampling algorithms take elements from a stream whose size is either very
   large or unknown. Their memory is constant with respect to the stream size. Reservoir methods can be unweighted or
   weighted.

Terminology
-----------
*Without Replacement*
    Sampling methods for which each unit of the population has only one chance of being selected in the sample.

*With Replacement*
    Sampling methods that are not without replacement.

*Constant Sample Size*
    The random sampling algorithms which accept the sample size as a parameter and always generate samples of that size,
    which is denoted as :math:`k`.

*Ratio Estimator Property*
    In the context of weighted random sampling, the *ratio estimator property* refers to the property according to which
    the first order inclusion probabilities of the elements in the population are strictly proportional to the weights
    of these elements. Methods that are known (or not known) to satisfy this property will have the respective mention
    in their description.

Notation
--------
Typical notation include :math:`n`, which dictates the number of elements in the population and :math:`k` which dictates
the desired number of elements in the sample or the number of elements in the sample when this parameter is not set, for
example when the algorithm is not of constant sample size. Furthermore, :math:`Z` denotes the sum of the weights of the
elements in the population and refers to weighted sampling algorithms.

General Properties
------------------
Exceptions
==========
In general, exceptions that are raised by class methods are not supposed to be caught. As there is generally no
finalization implemented, catching instance method exceptions will cause that instance to behave unpredictably or
erroneously. The custom exceptions are implemented in the :mod:`rsx.utils.exceptions` module.
"""

__version__ = "0.1"
