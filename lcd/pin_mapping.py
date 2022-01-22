from enum import Enum


class PinMapping(Enum):
    """
    Supports two variants of pin mappings:
    |           | 7    | 6    | 5    | 4    | 3    | 2    | 1    | 0    |
    | --------  | ---- | ---- | ---- | ---- | ---- | ---- | ---- | ---- |
    | Variant 1 | D7   | D6   | D5   | D4   | BL   | EN   | RW   | RS   |
    | Variant 2 | EN   | X    | X    | RS   | D7   | D6   | D5   | D4   |
    """
    MAPPING1 = 1
    MAPPING2 = 2
