import dataclasses
import datetime
import re

import health_centers.mappings


def validate_number_type(number):
    if isinstance(number, (int, float)):
        return int(number)
    if isinstance(number, str):
        number = number.replace('\u200b', '')
        number = number.replace('\\xa0', ' ')
        try:
            return int(number)
        except Exception:
            pass
        search = re.search(r'(\d+)\s+\(', number)
        if search:
            return int(search.group(1))
        # NP = Ni Podatka
        if number.lower() in ['n', 'np', 'np*', 'ni podatka']:
            return None
        if number.lower() == 'o':   # typo
            return 0
        if re.match(r'^še ni ', number):
            return None
        if re.match(r'ni še\s+rezul[ta]*tov.*', number):  # handling typos
            return None
    if number is None:
        return None
    if number in ['izvaja primar']:
        return 0
    raise ValueError(type(number), number)


@dataclasses.dataclass(frozen=True)
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
            object.__setattr__(self, field, validate_number_type(getattr(self, field)))

    def get(self, prop: str):
        return self.__dict__[prop]


@dataclasses.dataclass
class Entity:
    name: str
    name_key: str = dataclasses.field(init=False)
    date: datetime.date
    sheet: str
    file: str
    numbers: Numbers

    def set_name_key(self):
        self.name_key = None

        names = [self.name]
        if self.name.startswith('ZD '):
            names.append('Zdravstveni dom ' + self.name[3:].strip())

        for name in names:
            if name in health_centers.mappings.name:
                self.name_key = health_centers.mappings.name[name]

    def __post_init__(self):
        assert isinstance(self.date, datetime.date)
        assert isinstance(self.name, str)
        self.set_name_key()
        assert self.name_key, self.name
