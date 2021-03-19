from enum import Enum, unique


@unique
class Outcome(Enum):
    Win = 1
    Loss = 2
    Draw = 3
