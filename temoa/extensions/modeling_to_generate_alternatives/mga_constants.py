import enum
from enum import Enum


# dev note:  few of these are currently developed.... some placeholder ideas...
@enum.unique
class MgaAxis(Enum):
    TECH_CATEGORY_CAPACITY = 2
    TECH_CATEGORY_ACTIVITY = 3
    TECH_CATEGORY_EMISSION = 4


@enum.unique
class MgaWeighting(Enum):
    HULL_EXPANSION = 1
    UNUSED_STUFF = 2
