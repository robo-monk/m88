from dataclasses import dataclass
from enum import Enum

Country = Enum("Country", ["NL", "ES", "BG"])
# Bacteria = Enum("Bacteria", ["PSEUDO", "KLEBSIA", "ECOLI"])
class Country(Enum):
    NL = "NL"
    ES = "ES"
    BG = "BG"

    def to_camelcase(self):
        match self:
            case Country.NL:
                return "Netherlands"
            case Country.ES:
                return "Spain"
            case Country.BG:
                return "Bulgaria"

class Bacteria(Enum):
    PSEUDO = 'PSEUDO'
    KLEBSIA = "KLEBSIA"
    ECOLI = "ECOLI"

    def to_capitalized(self):
        match self:
            case Bacteria.PSEUDO:
                return "PSEUDO"
            case Bacteria.KLEBSIA:
                return "KLEBSIA"
            case Bacteria.ECOLI:
                return "ECOLI"




@dataclass
class State:
    year: int | None = None
    country: Country | None = None
    bacteria: Bacteria | None = None 

    def __str__(self):
        return f"State(year={self.year}, country={self.country}, bacteria={self.bacteria})"


state = State()