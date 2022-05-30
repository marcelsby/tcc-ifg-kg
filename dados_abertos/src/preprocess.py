import json
from pathlib import Path

from utils.messages import print_success, print_error


def barramento_ifg_json_to_csv(
    header: str, filename: str, raw: Path, transformed: Path
):
    raw = raw / f"{filename}.json"
    transformed = transformed / f"{filename}.csv"

    if not (transformed).is_file():
        Path(transformed).touch()
    else:
        # Limpa o arquivo caso ele exista, para não duplicar os resultados da conversão
        transformed.write_text("")

    attributes_count = len(header.split(";"))

    with open(raw) as f:
        loaded_json = json.load(f)

    try:
        with open(transformed, "a") as output_file:
            output_file.write(f"{header}\n")

            for row in loaded_json:
                linha = ""

                for attribute in range(0, attributes_count):
                    value: str = row["itens"][attribute]["valor"]

                    if value in (None, "0.0"):
                        value = ""
                    elif value == ";":
                        value = ","
                    else:
                        value = value.strip()

                    if attribute == attributes_count - 1:
                        linha += value + "\n"
                    else:
                        linha += value + ";"

                output_file.write(linha)

            print_success("Linhas escritas com sucesso!")
            print_success(f"Arquivo de saída: {transformed}")
    except Exception as e:
        print_error("Erro ao imprimir as linhas no arquivo de saída!")
        print_error("Mensagem de erro: " + str(e))
        exit(1)
