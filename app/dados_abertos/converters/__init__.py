import json
from dataclasses import dataclass
from pathlib import Path

from app.utils.storage import FileExtension, Storage


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


def get_csv_headers_metadata(raw_file_extension: FileExtension) -> list[CsvHeaderMetadata]:
    headers_metadata_file = Storage.get_file("dados_abertos/csv_headers_metadata.json")

    with open(headers_metadata_file, "r") as f:
        headers_metadata_json = json.load(f)

    headers_metadata = []

    for raw_metadata in headers_metadata_json["metadata"]:
        if raw_metadata["raw_file_extension"] == raw_file_extension.value:
            subject_path = Storage.get_file(f'dados_abertos/raw/{raw_metadata["subject"]}.{raw_file_extension.value}')

            header_metadata = CsvHeaderMetadata(subject_path, raw_metadata["header"])

            headers_metadata.append(header_metadata)

    return headers_metadata


def convert():
    from .barramento_ifg import convert as convert_barramento_ifg
    from .editais_iniciacao_cientifica import \
        convert as convert_editais_iniciacao_cientifica

    convert_barramento_ifg()
    convert_editais_iniciacao_cientifica()
