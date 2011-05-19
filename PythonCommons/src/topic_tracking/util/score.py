import math


def compute_exponential_decay_constant(half_life):
    return math.e ** (-math.log(2) / half_life)
