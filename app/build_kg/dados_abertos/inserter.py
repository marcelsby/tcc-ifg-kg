from app.build_kg.dados_abertos import (
    insert_cursos, insert_discentes, insert_disciplinas,
    insert_disciplinas_ministradas, insert_disciplinas_ministradas_docentes,
    insert_docentes, insert_editais_iniciacao_cientifica,
    insert_estagios_curriculares, insert_taes, insert_unidades)
from app.build_kg.database import Neo4jConnection, make_neo4j_bolt_connection
from app.utils.environment import Environment
from app.utils.storage import StorageWithBasePath


def insert(connection: Neo4jConnection):
    storage = StorageWithBasePath("dados_abertos/preprocessed/")

    insert_unidades.execute(
        connection,
        storage.get_file("unidades.csv")
    )

    insert_docentes.execute(
        connection,
        storage.get_file("docentes.csv")
    )

    insert_taes.execute(
        connection,
        storage.get_file("taes.csv")
    )

    insert_cursos.execute(
        connection,
        storage.get_file("cursos.csv")
    )

    insert_disciplinas.execute(
        connection,
        storage.get_file("disciplinas.csv")
    )

    insert_disciplinas_ministradas.execute(
        connection,
        storage.get_file("disciplinas_ministradas.csv")
    )

    insert_disciplinas_ministradas_docentes.execute(
        connection,
        storage.get_file("disciplinas_ministradas_docentes.csv")
    )

    insert_discentes.execute(
        connection,
        storage.get_file("discentes.csv")
    )

    insert_editais_iniciacao_cientifica.execute(
        connection,
        storage.get_file("editais_iniciacao_cientifica.csv")
    )

    insert_estagios_curriculares.execute(
        connection,
        storage.get_file("estagios_curriculares.csv")
    )


if __name__ == "__main__":
    conn = make_neo4j_bolt_connection(
        Environment.neo4j_user,
        Environment.neo4j_password,
        Environment.neo4j_host,
        Environment.neo4j_port
    )

    insert(conn)
