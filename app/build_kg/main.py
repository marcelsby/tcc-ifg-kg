import logging as log
from pathlib import Path

import pandas as pd
from neo4j.exceptions import ServiceUnavailable

from app.build_kg.database import (CypherCreateQueryBuilder, Neo4jConnection,
                                   Neo4jDataType, make_neo4j_bolt_connection,
                                   make_relationship_query)
from app.utils.environment import Environment
from app.utils.storage import Storage


def _insert_unidades(conn: Neo4jConnection, preprocessed_dir: Path):
    unidades_csv = preprocessed_dir / "unidades.csv"
    unidades_df = pd.read_csv(unidades_csv, delimiter=";")

    query_builder = CypherCreateQueryBuilder("Unidade")

    for index, row in unidades_df.iterrows():
        builded_query = (
            query_builder.add_property("nome", row["nome"])
            .add_property("sigla", row["sigla"])
            .add_property("logradouro", row["logradouro"])
            .add_property("numero", row["numero"])
            .add_property("bairro", row["bairro"])
            .add_property("cep", row["cep"])
            .add_property("cidade", row["cidade"])
            .add_property("site", row["site"])
            .add_property("telefone", row["telefone"])
            .add_property("email", row["email"])
            .add_property("cnpj", row["cnpj"])
            .add_property("uasg", row["uasg"])
            .build()
        )
        try:
            conn.query(builded_query)
            log.info(f'SUCESSO ao inserir unidade: {row["sigla"]}')
        except ServiceUnavailable as e:
            log.error(
                f'ERRO ao inserir unidade: {row["sigla"]}. Mensagem de erro: {str(e)}'
            )


def _insert_docentes(conn: Neo4jConnection, preprocessed_dir: Path):
    docentes_csv = preprocessed_dir / "docentes.csv"
    docentes_df = pd.read_csv(docentes_csv, delimiter=";")

    create_query_builder = CypherCreateQueryBuilder(["Docente", "Servidor"])

    for index, row in docentes_df.iterrows():
        create_query = (
            create_query_builder.add_property("nome", row["nome"])
            .add_property("matricula", row["matricula"])
            .add_property("disciplina_ministrada", row["disciplina_ministrada"])
            .add_property(
                "data_ingresso", row["data_ingresso"], value_type=Neo4jDataType.DATE
            )
            .add_property("atribuicao", row["atribuicao"])
            .add_property("carga_horaria", row["carga_horaria"])
            .build()
        )

        relationship_query = make_relationship_query(
            "Docente",
            "matricula",
            row["matricula"],
            "Unidade",
            "nome",
            row["campus"],
            "PART_OF",
        )

        try:
            conn.query(create_query)
            conn.query(relationship_query)
            log.info(
                f'SUCESSO ao inserir docente e o seu relacionamento com uma unidade: {row["matricula"]}'
            )
        except ServiceUnavailable as e:
            log.error(
                f"ERRO ao inserir docente e o seu relacionamento com uma unidade. Mensagem de erro: {str(e)}"
            )


def _insert_taes(conn: Neo4jConnection, preprocessed_dir: Path):
    taes_csv = preprocessed_dir / "taes.csv"
    taes_df = pd.read_csv(taes_csv, delimiter=";")

    create_query_builder = CypherCreateQueryBuilder(["TAE", "Servidor"])

    for index, row in taes_df.iterrows():
        create_query = (
            create_query_builder.add_property("nome", row["nome"])
            .add_property("matricula", row["matricula"])
            .add_property(
                "data_ingresso", row["data_ingresso"], value_type=Neo4jDataType.DATE
            )
            .add_property("atribuicao", row["atribuicao"])
            .add_property("carga_horaria", row["carga_horaria"])
            .build()
        )

        relationship_query = make_relationship_query(
            "TAE",
            "matricula",
            row["matricula"],
            "Unidade",
            "sigla",
            row["uorg_exercicio"],
            "PART_OF",
        )

        try:
            conn.query(create_query)
            conn.query(relationship_query)
            log.info(
                f'SUCESSO ao inserir TAE e o seu relacionamento com uma unidade: {row["matricula"]}'
            )
        except ServiceUnavailable as e:
            log.error(
                f"ERRO ao inserir TAE e o seu relacionamento com uma unidade. Mensagem de erro: {str(e)}"
            )


def _insert_cursos(conn: Neo4jConnection, preprocessed_dir: Path):
    cursos_csv = preprocessed_dir / "cursos.csv"
    cursos_df = pd.read_csv(cursos_csv, delimiter=";")

    create_query_builder = CypherCreateQueryBuilder("Curso")

    attribute_keys = list(cursos_df.columns)

    for _, row in cursos_df.iterrows():
        for key in attribute_keys:
            value = row[key]

            if key == "campus":
                continue
            elif key in ["codigo", "qtd_vagas_ano", "qtd_semestres"] or key.startswith("ch_"):
                create_query_builder.add_property(key, value, Neo4jDataType.INTEGER)
            else:
                create_query_builder.add_property(key, value)

        create_query = create_query_builder.build()

        curso_to_unidade_relationship_query = make_relationship_query(
            "Curso",
            "codigo",
            row["codigo"],
            "Unidade",
            "sigla",
            row["campus"],
            "OFFERED_AT",
            a_value_type=Neo4jDataType.INTEGER,
        )

        try:
            conn.query(create_query)
            conn.query(curso_to_unidade_relationship_query)
            log.info(
                f'SUCESSO ao inserir curso e o seu relacionamento com uma unidade: {row["codigo"]} -> {row["campus"]}'
            )
        except ServiceUnavailable as e:
            log.error(
                f"ERRO ao inserir curso e o seu relacionamento com uma unidade. Mensagem de erro: {str(e)}"
            )

        unidade_to_curso_relationship_query = make_relationship_query(
            "Unidade",
            "sigla",
            row["campus"],
            "Curso",
            "codigo",
            row["codigo"],
            "OFFERS",
            b_value_type=Neo4jDataType.INTEGER
        )

        try:
            conn.query(unidade_to_curso_relationship_query)
            log.info(
                f'SUCESSO ao inserir o relacionamento de uma unidade com um curso: {row["campus"]} -> {row["codigo"]}')
        except ServiceUnavailable as e:
            log.error(
                f"ERRO ao inserir o relacionamento de uma unidade com um curso. Mensagem de erro: {str(e)}"
            )


def execute():
    neo4j_conn = make_neo4j_bolt_connection(Environment.neo4j_user, Environment.neo4j_password,
                                            Environment.neo4j_host, Environment.neo4j_port)

    preprocessed_dir = Storage.get_dir("dados_abertos/preprocessed")

    _insert_unidades(neo4j_conn, preprocessed_dir)
    _insert_docentes(neo4j_conn, preprocessed_dir)
    _insert_taes(neo4j_conn, preprocessed_dir)
    _insert_cursos(neo4j_conn, preprocessed_dir)


if __name__ == '__main__':
    execute()
