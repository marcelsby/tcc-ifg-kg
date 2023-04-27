import json
from pathlib import Path

from alive_progress import alive_bar

from app.dados_abertos.converters import CsvHeaderMetadata
from app.utils.messages import print_error
from app.utils.storage import FileExtension, Storage
from app.utils.validators import validate_json_file


def _get_csv_headers_metadata(raw_file_extension: FileExtension) -> list[CsvHeaderMetadata]:
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

    try:
        with open(transformed_file, "a") as output_file:
            output_file.write(f"{header}\n")

            for item in loaded_json:
                converted_row = ""

                for attribute in range(0, attributes_count):
                    value: str = item["itens"][attribute]["valor"]

                    if value in (None, "0.0"):
                        value = ""
                    elif value == ";":
                        value = ","
                    else:
                        value = value.strip()

                    if attribute == attributes_count - 1:
                        converted_row += value + "\n"
                    else:
                        converted_row += value + ";"

                output_file.write(converted_row)

    except Exception as e:
        print_error("Erro ao imprimir as linhas no arquivo de saída!")
        print_error("Mensagem de erro: " + str(e))
        exit(1)


def convert() -> None:
    """
    Converte os arquivos coletados do Barramento IFG para o formato esperado pelo processo de pré-processamento dos dados.
    """
    transformed_path = Storage.get_dir("dados_abertos/transformed", need_create=True)

    json_to_csv_headers_metadata: list[CsvHeaderMetadata] = _get_csv_headers_metadata(FileExtension.JSON)

    with alive_bar(len(json_to_csv_headers_metadata), title="Converting 'Barramento IFG' JSON files to CSV") as bar:
        for metadata in json_to_csv_headers_metadata:
            _json_to_csv(metadata.header, metadata.subject, transformed_path)
            bar()


if __name__ == '__main__':
    convert()
