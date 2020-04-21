import dataclasses
import datetime

import mappings


def validate_number_type(number):
    if isinstance(number, (int, float)):
        return int(number)
    if isinstance(number, str):
        if number.lower() in ['n', 'np', 'np*', 'ni podatka']:  # NP = Ni Podatka
            return None
        if number.lower() == 'o':   # typo
            return 0
        if number.startswith('10 (od tega 2 kontrolna)'):  # TODO handle in a different way
            return 10
        if number.startswith('1 (kontrolni)'):  # TODO handle in a different way
            return 1
    if number is None:
        return None
    raise ValueError(number)


@dataclasses.dataclass
class Numbers:
    examinations___medical_emergency: int
    examinations___suspected_covid: int
    phone_triage___suspected_covid: int
    tests___performed: int
    tests___positive: int
    sent_to___hospital: int
    sent_to___self_isolation: int

    def __post_init__(self):  # validate and transform all properties
        for field in self.__annotations__.keys():
            setattr(self, field, validate_number_type(getattr(self, field)))


@dataclasses.dataclass
class Entity:
    name: str
    name_key: str = dataclasses.field(init=False)
    date: datetime.date
    sheet: str
    file: str
    numbers: Numbers

    def __post_init__(self):
        assert isinstance(self.name, str)
        assert self.name in mappings.name, self.name
        self.name_key = mappings.name[self.name]
        assert isinstance(self.date, datetime.date)
