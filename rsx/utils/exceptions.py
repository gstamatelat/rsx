"""
Exceptions used throughout the package.
"""


class BadWeightError(Exception):
    """
    Represents a weight that is not compatible with a certain weight random sampling algorithm.
    """


class InfeasibleCaseError(Exception):
    """
    Represents a population that results in an infeasible random sampling case, typically resulting from an element
    corresponding to inclusion probability that is higher than unity.
    """
