from dataclasses import dataclass
from pathlib import Path


@dataclass
class CsvHeaderMetadata:
    subject: Path
    header: str


def convert():
    from .barramento_ifg import convert as convert_barramento_ifg

    convert_barramento_ifg()

# TODO: transformar o json de editais de iniciação científica em csv
