from dataclasses import dataclass
from pathlib import Path


@dataclass
class CsvHeaderMetadata:
    subject: Path
    header: str


class ConversionError(Exception):
    """
    Classe wrapper para encapsular exceções que ocorrem durante um processo de conversão
    """

    def __init__(self, message: str, cause: Exception):
        super().__init__(message)
        self.__cause__ = cause


def convert():
    from .barramento_ifg import convert as convert_barramento_ifg

    convert_barramento_ifg()

# TODO: transformar o json de editais de iniciação científica em csv
