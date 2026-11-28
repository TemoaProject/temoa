from enum import Enum, unique


@unique
class MooObjective(Enum):
    """The objective functions that can be explored in a MOO run"""

    COST = 'cost'
    EMISSION = 'emission'
    CONSTRUCTION_INPUT = 'construction_input'

    @classmethod
    def from_label(cls, label: object) -> 'MooObjective':
        cleaned = str(label).strip().lower()
        for member in cls:
            if member.value == cleaned:
                return member
        choices = ', '.join(member.value for member in cls)
        raise ValueError(f"Unknown MOO objective '{label}'.  Possible choices are: {choices}")
