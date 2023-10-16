import json
from pathlib import Path

from alive_progress import alive_bar

from app.dados_abertos.converters import (ConversionError,
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

    attributes_count = len(header.split(";"))

    with open(subject) as f:
        loaded_json = json.load(f)

    converted_rows = []

    for item in loaded_json:
        row_values = []

        for attribute_index in range(0, attributes_count):
            value: str = item["itens"][attribute_index]["valor"]

            try:
                if value in (None, "0.0"):
                    value = ""
                elif value == ";":
                    value = ","
                elif isinstance(value, str):
                    value = value.strip()
                elif not isinstance(value, str):
                    value = str(value)

                row_values.append(value)
            except Exception as e:
                raise ConversionError(f"Falha na conversão do arquivo '{subject.name}'. Valor: {value}", e)

        converted_row = ";".join(row_values)
        converted_rows.append(converted_row)

    try:
        with open(transformed_file, "a") as output_file:
            output_file.write(f"{header}\n")
            output_file.write("\n".join(converted_rows))
    except Exception as e:
        raise ConversionError(f"Falha na escrita do arquivo convertido '{subject.name}'.", e)


def convert() -> None:
    """
    Converte os arquivos coletados do Barramento IFG para o formato esperado pelo processo de pré-processamento dos dados.
    """
    transformed_path = Storage.get_dir("dados_abertos/transformed", create_if_not_exists=True)

    json_to_csv_headers_metadata = get_csv_headers_metadata(FileExtension.JSON)

    for index, metadata in enumerate(json_to_csv_headers_metadata):
        if metadata.subject.name in ["editais_iniciacao_cientifica.json"]:
            json_to_csv_headers_metadata.pop(index)

    with alive_bar(len(json_to_csv_headers_metadata), title="Converting 'Barramento IFG' JSON files to CSV") as bar:
        for metadata in json_to_csv_headers_metadata:
            _json_to_csv(metadata.header, metadata.subject, transformed_path)
            bar()


if __name__ == '__main__':
    convert()
