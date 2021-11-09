"""
Tests for Jessen algorithms.
"""

import random

from rsx.utils.helper import check_feasibility
from rsx.utils.helper import normalize_probabilities
from rsx.whole.jessen import JessenBuilder


def test_correctness():
    """
    The sample space must be equal to or greater than the size of the distribution given. Also the sum of the
    probabilities of the samples must be equal to unity.
    """
    for _ in range(100):
        distribution = normalize_probabilities([random.random() for _ in range(random.randint(5, 10))])
        sample_size = random.randint(1, 5)
        if check_feasibility(distribution, sample_size):
            jessen = JessenBuilder() \
                .add_weights(distribution) \
                .build(sample_size)
            sample_space_size = 0
            sample_space_prob = 0
            for sample, prob in jessen.sample_space():
                sample_space_size += 1
                sample_space_prob += prob
                assert len(sample) == sample_size
            assert sample_space_size >= len(distribution)
            assert abs(1 - sample_space_prob) < 1.0e-6
