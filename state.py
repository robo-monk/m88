from dataclasses import dataclass
from enum import Enum

Country = Enum("Country", ["NL", "ES", "BG"])
Bacteria = Enum("Bacteria", ["PSEUDO", "KLEBSIA", "ECOLI"])

@dataclass
class State:
    year: int | None = None
    country: Country | None = None
    bacteria: Bacteria | None = None 