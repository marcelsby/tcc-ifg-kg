import json
from typing import Callable

from alive_progress import alive_bar

from app.utils.storage import Storage
from app.utils.validators import validate_json_file


def _clean_cursos():
    cursos_json_file = Storage.get_file("dados_abertos/raw/cursos.json")

    validate_json_file(cursos_json_file)

    with open(cursos_json_file, "r") as f:
        cursos = json.load(f)

    for curso in cursos:
        """
        Remove a coluna cheia de "0.0" (valores inválidos) e que não está especificada no 
        dicionário de dados desse dataset.

        A hipótese mais provável é que é uma coluna inserida por acidente no dataset.        
        """
        curso["itens"].pop(14)

        """
        Transforma os valores que estão representados como float para inteiros, o que é a 
        maneira correta de representá-los.
        """
        for item_index in range(10, len(curso["itens"]) - 1):
            value = curso["itens"][item_index]["valor"]

            if value is not None:
                parsed_value: int = int(float(value))
                curso["itens"][item_index]["valor"] = parsed_value

    with open(cursos_json_file, "w") as f:
        json.dump(cursos, f, separators=(",", ":"), ensure_ascii=False)


def clean():
    clean_funcs: list[Callable] = [_clean_cursos]

    with alive_bar(len(clean_funcs), title="Cleaning 'Barramento IFG' collected files") as bar:
        for func in clean_funcs:
            func()
            bar()


if __name__ == '__main__':
    clean()
