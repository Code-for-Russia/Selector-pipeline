from enum import Enum

class ElectionLevel(Enum):
    FEDERAL = 1
    REGIONAL = 2
    MUNICIPAL = 3


class ElectionType(Enum):
    PERSONAL = 1
    REPRESENTATIVE = 2


class ElectionLocationType(Enum):
    MUNICIPAL_DISTRICT = 1
    CITY_RURAL = 2