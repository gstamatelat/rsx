"""
Whole sample procedures are considered the methods that assign a probability to each possible sample of :math:`k` items
from the population and one selection using those probabilities selects the whole sample [1]_.

Usually these algorithms can be split into the preprocessing stage where, using a (possibly) time consuming process, the
sub-sample space is being created and probabilities are assigned to each sample. After this preprocessing, samples can
be queried in (usually) constant time from the sample space. Thus, they should be preferred when an application requires
very often and fast retrievals of samples. However, in order for whole sampling methods to achieve constant time access
to a random sample they usually have to store the samples in memory and as a result the possible samples might be a very
small fraction of all possible sample combinations.

.. [1] Ken R.W. Brewer, Muhammad Hanif.
       Sampling with unequal probabilities (1983).
"""
