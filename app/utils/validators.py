import json
from json import JSONDecodeError
from pathlib import Path


class JSONFileValidationError(Exception):
    def __init__(self, message: str, cause: Exception):
        super().__init__(message)
        self.__cause__ = cause


def validate_json_file(file_to_validate: Path):
    try:
        with open(file_to_validate) as f:
            json.load(f)
    except JSONDecodeError as e:
        raise JSONFileValidationError(
            f"Falha ao validar o conteúdo do arquivo como JSON. Arquivo: '{file_to_validate}'", cause=e)
