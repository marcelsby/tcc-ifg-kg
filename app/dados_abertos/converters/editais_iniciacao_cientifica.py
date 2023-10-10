import json
from pathlib import Path

from app.dados_abertos.converters import (CsvHeaderMetadata,
                                          get_csv_headers_metadata)
from app.utils.storage import FileExtension, Storage
from app.utils.validators import validate_json_file


def _json_to_csv(header: str, subject: Path, transformed_path: Path) -> None:
    """
    :param header: O cabeçalho do CSV que será gerado.

    :param subject: O Path para o arquivo JSON que será convertido para CSV,
    que após a conversão será salvo com o mesmo nome, mas com a extensão ".csv".

    :param transformed_path: O Path para a pasta onde será salvo o arquivo CSV resultante da conversão.
    """
    validate_json_file(subject)

    transformed_file = transformed_path / f'{subject.name.replace(".json", ".csv")}'

    if not transformed_file.exists():
        transformed_file.touch()
    else:
        # Limpa o arquivo caso ele exista, para não duplicar os resultados da conversão
        transformed_file.write_text("")

    header_attributes = header.split(";")

    with open(subject) as f:
        loaded_json = json.load(f)

    converted_rows = []

    for item in loaded_json:
        row_values = []

        for attribute in header_attributes:
            value = item[attribute]

            if isinstance(value, str):
                value = value.strip()

            if isinstance(value, int):
                value = str(value)

            row_values.append(value)

        converted_rows.append(";".join(row_values))

    with open(transformed_file, mode="a") as f:
        f.write(header + "\n")
        data = "\n".join(converted_rows)
        f.write(data)


def convert():
    """
    Converte os editais de iniciação científica coletados do SIGEPE para o formato esperado pelo processo de
    pré-processamento dos dados.
    """
    transformed_path = Storage.get_dir("dados_abertos/transformed", create_if_not_exists=True)

    header_metadata: CsvHeaderMetadata = next(
        filter(lambda metadata: metadata.subject.name == "editais_iniciacao_cientifica.json",
               get_csv_headers_metadata(FileExtension.JSON)))

    _json_to_csv(header_metadata.header, header_metadata.subject, transformed_path)


if __name__ == '__main__':
    convert()
