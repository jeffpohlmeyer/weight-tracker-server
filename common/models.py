from enum import Enum, IntEnum


class SexEnum(str, Enum):
    male = "male"
    female = "female"


class WeekdayEnum(IntEnum):
    Sunday = 0
    Monday = 1
    Tuesday = 2
    Wednesday = 3
    Thursday = 4
    Friday = 5
    Saturday = 6
