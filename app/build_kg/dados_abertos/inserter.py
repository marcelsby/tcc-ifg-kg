from app.build_kg.dados_abertos import (
    insert_cursos, insert_disciplinas, insert_disciplinas_ministradas,
    insert_disciplinas_ministradas_docentes, insert_docentes,
    insert_editais_iniciacao_cientifica, insert_estagios_curriculares,
    insert_taes, insert_unidades)
from app.build_kg.database import make_neo4j_bolt_connection
from app.utils.environment import Environment
from app.utils.storage import StorageWithBasePath


def insert():
    conn = make_neo4j_bolt_connection(Environment.neo4j_user, Environment.neo4j_password,
                                      Environment.neo4j_host, Environment.neo4j_port)

    storage = StorageWithBasePath("dados_abertos/preprocessed/")

    insert_unidades.execute(
        conn,
        storage.get_file("unidades.csv")
    )

    insert_docentes.execute(
        conn,
        storage.get_file("docentes.csv")
    )

    insert_taes.execute(
        conn,
        storage.get_file("taes.csv")
    )

    insert_cursos.execute(
        conn,
        storage.get_file("cursos.csv")
    )

    insert_disciplinas.execute(
        conn,
        storage.get_file("disciplinas.csv")
    )

    insert_disciplinas_ministradas.execute(
        conn,
        storage.get_file("disciplinas_ministradas.csv")
    )

    insert_disciplinas_ministradas_docentes.execute(
        conn,
        storage.get_file("disciplinas_ministradas_docentes.csv")
    )

    insert_editais_iniciacao_cientifica.execute(
        conn,
        storage.get_file("editais_iniciacao_cientifica.csv")
    )

    insert_estagios_curriculares.execute(
        conn,
        storage.get_file("estagios_curriculares.csv")
    )


if __name__ == "__main__":
    insert()
