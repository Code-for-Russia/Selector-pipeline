from enum import Enum

class ElectionLevel(str, Enum):
    FEDERAL = "FEDERAL"
    REGIONAL = "REGIONAL"
    MUNICIPAL = "MUNICIPAL"


class ElectionType(str, Enum):
    PERSONAL = "PERSONAL"
    REPRESENTATIVE = "REPRESENTATIVE"


class ElectionLocationType(str, Enum):
    MUNICIPAL_DISTRICT = "MUNICIPAL_DISTRICT"
    CITY_RURAL = "CITY_RURAL"