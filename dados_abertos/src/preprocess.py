import json
from pathlib import Path

from utils.messages import print_success, print_error


def json_to_csv(cabecalho: str, raw: Path, transformed: Path):
    if not transformed.is_file():
        Path(transformed).touch()

    qtd_atributos = len(cabecalho.split(";"))

    with open(raw) as f:
        loaded_json = json.load(f)

    try:
        with open(transformed, "a") as output_file:
            output_file.write(cabecalho)

            for registro in loaded_json:
                linha = ""

                for atributo in range(0, qtd_atributos):
                    valor: str = registro["itens"][atributo]["valor"]

                    if valor in (None, "0.0"):
                        valor = ""
                    elif valor == ";":
                        valor = ","
                    else:
                        valor = valor.strip()

                    if atributo == qtd_atributos - 1:
                        linha += valor + "\n"
                    else:
                        linha += valor + ";"

                output_file.write(linha)

            print_success("Linhas escritas com sucesso!")
            print_success(f"Arquivo de saída: {transformed}")
    except Exception as e:
        print_error("Erro ao imprimir as linhas no arquivo de saída!")
        print_error("Mensagem de erro: " + str(e))
        exit(1)
