from app.build_kg.dados_abertos import (
    insert_cursos, insert_disciplinas, insert_disciplinas_ministradas,
    insert_disciplinas_ministradas_docentes, insert_docentes, insert_taes,
    insert_unidades)
from app.build_kg.database import make_neo4j_bolt_connection
from app.utils.environment import Environment
from app.utils.storage import Storage


def insert():
    conn = make_neo4j_bolt_connection(Environment.neo4j_user, Environment.neo4j_password,
                                      Environment.neo4j_host, Environment.neo4j_port)

    insert_unidades.execute(
        conn,
        Storage.get_file("dados_abertos/preprocessed/unidades.csv")
    )

    insert_docentes.execute(
        conn,
        Storage.get_file("dados_abertos/preprocessed/docentes.csv")
    )

    insert_taes.execute(
        conn,
        Storage.get_file("dados_abertos/preprocessed/taes.csv")
    )

    insert_cursos.execute(
        conn,
        Storage.get_file("dados_abertos/preprocessed/cursos.csv")
    )

    insert_disciplinas.execute(
        conn,
        Storage.get_file("dados_abertos/preprocessed/disciplinas.csv")
    )

    insert_disciplinas_ministradas.execute(
        conn,
        Storage.get_file("dados_abertos/preprocessed/disciplinas_ministradas.csv")
    )

    insert_disciplinas_ministradas_docentes.execute(
        conn,
        Storage.get_file("dados_abertos/preprocessed/disciplinas_ministradas_docentes.csv")
    )


if __name__ == "__main__":
    insert()
