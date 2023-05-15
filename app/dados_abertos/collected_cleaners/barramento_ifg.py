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
        for item_index in range(10, len(curso["itens"])):
            value = curso["itens"][item_index]["valor"]

            if value is not None:
                parsed_value: int = int(float(value))
                curso["itens"][item_index]["valor"] = parsed_value

    with open(cursos_json_file, "w") as f:
        json.dump(cursos, f, separators=(",", ":"), ensure_ascii=False)


def _clean_disciplinas_ministradas():
    disciplinas_ministradas_json_file = Storage.get_file("dados_abertos/raw/disciplinas_ministradas.json")

    validate_json_file(disciplinas_ministradas_json_file)

    with open(disciplinas_ministradas_json_file, "r") as f:
        disciplinas_ministradas = json.load(f)

    for disciplina_ministrada in disciplinas_ministradas:
        """
        Outro problema encontrado nesse dataset são algumas disciplinas com o nome incompleto e com caracteres de escape de linha,
        contando que o dicionário de dados especifica 16 campos, quando os itens do dataset foram analisados
        descobriu-se que na verdade estão presentes 17 campos, entretanto esse novo campo basicamente repete
        alguns dados já apresentados anteriormente (turma, nome da disciplina e carga horária da disciplina). 
        
        No caso das disciplinas que estavam com o nome incompleto e com falhas foi possível consultar seu nome completo nesse campo
        adicional e corrigir essas inconsistências.
        """
        subject_code: int = int(disciplina_ministrada["itens"][10]["valor"])

        if subject_code == 26734:
            disciplina_ministrada["itens"][12]["valor"] = "Leitura e Produção Textual de Gêneros Acadêmicos (60)"

    with open(disciplinas_ministradas_json_file, "w") as f:
        json.dump(disciplinas_ministradas, f, separators=(",", ":"), ensure_ascii=False)


def clean():
    clean_funcs: list[Callable] = [_clean_cursos, _clean_disciplinas_ministradas]

    with alive_bar(len(clean_funcs), title="Cleaning 'Barramento IFG' collected files") as bar:
        for func in clean_funcs:
            func()
            bar()


if __name__ == '__main__':
    clean()
