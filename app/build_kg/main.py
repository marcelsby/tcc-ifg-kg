import logging as log
from pathlib import Path

import pandas as pd
from neo4j.exceptions import ServiceUnavailable

from app.build_kg.database import (CypherCreateQueryBuilder, Neo4jConnection,
                                   Neo4jDataType, make_neo4j_bolt_connection,
                                   CypherQueryFilter,
                                   CypherQueryFilterType, make_simple_relationship_query)
from app.utils.environment import Environment
from app.utils.storage import Storage


def _insert_unidades(conn: Neo4jConnection, preprocessed_dir: Path):
    unidades_csv = preprocessed_dir / "unidades.csv"
    unidades_df = pd.read_csv(unidades_csv, delimiter=";")

    query_builder = CypherCreateQueryBuilder("Unidade")
    attributes_keys = list(unidades_df.columns)

    for _, row in unidades_df.iterrows():
        for key in attributes_keys:
            value_type = Neo4jDataType.STRING

            if key == "uasg":
                value_type = Neo4jDataType.INTEGER

            query_builder.add_property(key, row[key], value_type)

        query = query_builder.build()

        try:
            conn.query(query)
            log.info(f'SUCESSO ao inserir unidade: {row["sigla"]}')
        except ServiceUnavailable as e:
            log.error(
                f'ERRO ao inserir unidade: {row["sigla"]}. Mensagem de erro: {str(e)}'
            )


def _insert_docentes(conn: Neo4jConnection, preprocessed_dir: Path):
    docentes_csv = preprocessed_dir / "docentes.csv"
    docentes_df = pd.read_csv(docentes_csv, delimiter=";")

    create_query_builder = CypherCreateQueryBuilder(["Docente", "Servidor"])

    attributes_keys = list(docentes_df.columns)
    attributes_keys.remove("campus")

    for _, row in docentes_df.iterrows():
        for key in attributes_keys:
            value_type = Neo4jDataType.STRING

            if key == "matricula":
                value_type = Neo4jDataType.INTEGER
            elif key == "data_ingresso":
                value_type = Neo4jDataType.DATE

            create_query_builder.add_property(key, row[key], value_type)

        create_query = create_query_builder.build()

        docente_matricula_filter = CypherQueryFilter("matricula", CypherQueryFilterType.EQUAL, row["matricula"], Neo4jDataType.INTEGER)
        unidade_campus_filter = CypherQueryFilter("nome", CypherQueryFilterType.EQUAL, row["campus"])

        relationship_query = make_simple_relationship_query(
            "Docente",
            docente_matricula_filter,
            "Unidade",
            unidade_campus_filter,
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

    attributes_keys = list(taes_df.columns)
    attributes_keys.remove("uorg_exercicio")

    for _, row in taes_df.iterrows():
        for key in attributes_keys:
            value_type = Neo4jDataType.STRING

            if key == "matricula":
                value_type = Neo4jDataType.INTEGER
            elif key == "data_ingresso":
                value_type = Neo4jDataType.DATE

            create_query_builder.add_property(key, row[key], value_type)

        create_query = create_query_builder.build()

        tae_matricula_filter = CypherQueryFilter("matricula", CypherQueryFilterType.EQUAL, row["matricula"])
        unidade_sigla_filter = CypherQueryFilter("sigla", CypherQueryFilterType.EQUAL, row["uorg_exercicio"])

        relationship_query = make_simple_relationship_query(
            "TAE",
            tae_matricula_filter,
            "Unidade",
            unidade_sigla_filter,
            "PART_OF"
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
    attribute_keys.remove("campus")

    for _, row in cursos_df.iterrows():
        for key in attribute_keys:
            value_type = Neo4jDataType.STRING

            if key in ["codigo", "qtd_vagas_ano", "qtd_semestres"] or key.startswith("ch_"):
                value_type = Neo4jDataType.INTEGER

            create_query_builder.add_property(key, row[key], value_type)

        create_query = create_query_builder.build()

        curso_codigo_filter = CypherQueryFilter("codigo", CypherQueryFilterType.EQUAL, row["codigo"], Neo4jDataType.INTEGER)
        unidade_sigla_filter = CypherQueryFilter("sigla", CypherQueryFilterType.EQUAL, row["campus"])

        curso_to_unidade_relationship_query = make_simple_relationship_query(
            "Curso",
            curso_codigo_filter,
            "Unidade",
            unidade_sigla_filter,
            "OFFERED_AT",
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

        unidade_to_curso_relationship_query = make_simple_relationship_query(
            "Unidade",
            unidade_sigla_filter,
            "Curso",
            curso_codigo_filter,
            "OFFERS",
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
