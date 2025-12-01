"""
The possible operating modes for a scenario
"""

from enum import Enum, unique


@unique
class TemoaMode(Enum):
    """The processing mode for the scenario"""

    PERFECT_FORESIGHT = 1  # Normal run, single execution for full time horizon
    MGA = 2  # Modeling for Generation of Alternatives, multiple runs w/ changing constrained obj
    MYOPIC = 3  # Step-wise execution through the future
    METHOD_OF_MORRIS = 4  # Method-of-Morris run
    BUILD_ONLY = 5  # Just build the model, no solve
    CHECK = 6  # build and run price check, source trace it
    SVMGA = 7  # single-vector MGA
    MONTE_CARLO = 8  # MC optimization
