"""
Tests for the alias method implementation.
"""
from collections import Counter

from rsx.utils.alias import AliasMethod


def test_correctness():
    """
    Test the correctness with a trivial example.
    """
    distribution = [0.1, 0.2, 0.3, 0.4]
    iterations = 1000000

    alias = AliasMethod(distribution)
    frequencies = Counter()
    for _ in range(iterations):
        frequencies[alias.sample()] += 1
    squared_error = sum((distribution[k] - v / iterations) ** 2 for (k, v) in frequencies.items())
    assert squared_error / len(distribution) < 1.0e-5
