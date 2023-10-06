import concurrent.futures
import time
from pathlib import Path

import pandas as pd

from app.build_kg.database import (CypherCreateQueryBuilder,
                                   CypherJsonLikeProperty, CypherQueryFilter,
                                   CypherQueryFilterType, Neo4jConnection,
                                   Neo4jDataType, make_neo4j_bolt_connection,
                                   make_relationship_query,
                                   run_transactions_batch)
from app.utils.environment import Environment
from app.utils.storage import Storage


def _insert_unidades(conn: Neo4jConnection, preprocessed_dir: Path):
    unidades_csv = preprocessed_dir / "unidades.csv"
    unidades_df = pd.read_csv(unidades_csv, delimiter=";")

    create_query_builder = CypherCreateQueryBuilder("Unidade")
    attributes_keys = list(unidades_df.columns)

    for _, row in unidades_df.iterrows():
        for key in attributes_keys:
            value_type = Neo4jDataType.STRING

            if key == "uasg":
                value_type = Neo4jDataType.INTEGER

            _cqb_add_property_when_value_not_absent(create_query_builder, key, row[key], value_type)

        create_query = create_query_builder.build()

        conn.query(create_query)


def _insert_docentes(conn: Neo4jConnection, preprocessed_dir: Path):
    start = time.perf_counter()

    docentes_csv = preprocessed_dir / "docentes.csv"
    docentes_df = pd.read_csv(docentes_csv, delimiter=";")

    create_query_builder = CypherCreateQueryBuilder(["Docente", "Servidor"])

    attributes_keys = list(docentes_df.columns)
    attributes_keys.remove("campus")

    with conn.driver.session() as session:
        for _, row in docentes_df.iterrows():
            for key in attributes_keys:
                value_type = Neo4jDataType.STRING

                if key == "matricula":
                    value_type = Neo4jDataType.INTEGER
                elif key == "data_ingresso":
                    value_type = Neo4jDataType.DATE

                _cqb_add_property_when_value_not_absent(create_query_builder, key, row[key], value_type)

            create_query = create_query_builder.build()

            docente_matricula_filter = CypherQueryFilter(
                "matricula", CypherQueryFilterType.EQUAL, row["matricula"], Neo4jDataType.INTEGER)

            unidade_campus_filter = CypherQueryFilter("nome", CypherQueryFilterType.EQUAL, row["campus"])

            relationship_query = make_relationship_query(
                "Docente",
                docente_matricula_filter,
                "Unidade",
                unidade_campus_filter,
                "PART_OF",
            )

            with session.begin_transaction() as tx:
                tx.run(create_query)
                tx.run(relationship_query)

    end = time.perf_counter()
    print(f"Docentes ({docentes_df.shape[0]} linhas): {end - start}s")


def _insert_taes(conn: Neo4jConnection, preprocessed_dir: Path):
    start = time.perf_counter()

    taes_csv = preprocessed_dir / "taes.csv"
    taes_df = pd.read_csv(taes_csv, delimiter=";")

    create_query_builder = CypherCreateQueryBuilder(["TAE", "Servidor"])

    attributes_keys = list(taes_df.columns)
    attributes_keys.remove("uorg_exercicio")

    with conn.driver.session() as session:
        for _, row in taes_df.iterrows():
            for key in attributes_keys:
                value_type = Neo4jDataType.STRING

                if key == "matricula":
                    value_type = Neo4jDataType.INTEGER
                elif key == "data_ingresso":
                    value_type = Neo4jDataType.DATE

                _cqb_add_property_when_value_not_absent(create_query_builder, key, row[key], value_type)

            create_query = create_query_builder.build()

            tae_matricula_filter = CypherQueryFilter("matricula", CypherQueryFilterType.EQUAL, row["matricula"])
            unidade_sigla_filter = CypherQueryFilter("sigla", CypherQueryFilterType.EQUAL, row["uorg_exercicio"])

            relationship_query = make_relationship_query(
                "TAE",
                tae_matricula_filter,
                "Unidade",
                unidade_sigla_filter,
                "PART_OF"
            )

            with session.begin_transaction() as tx:
                tx.run(create_query)
                tx.run(relationship_query)

    end = time.perf_counter()
    print(f"TAEs ({taes_df.shape[0]} linhas): {end - start}s")


def _insert_cursos(conn: Neo4jConnection, preprocessed_dir: Path):
    start = time.perf_counter()

    cursos_csv = preprocessed_dir / "cursos.csv"
    cursos_df = pd.read_csv(cursos_csv, delimiter=";")

    create_query_builder = CypherCreateQueryBuilder("Curso")

    attribute_keys = list(cursos_df.columns)
    attribute_keys.remove("campus")

    with conn.driver.session() as session:
        for _, row in cursos_df.iterrows():
            for key in attribute_keys:
                value_type = Neo4jDataType.STRING

                if key in ["codigo", "qtd_vagas_ano", "qtd_semestres"] or key.startswith("ch_"):
                    value_type = Neo4jDataType.INTEGER

                _cqb_add_property_when_value_not_absent(create_query_builder, key, row[key], value_type)

            create_query = create_query_builder.build()

            curso_codigo_filter = CypherQueryFilter(
                "codigo", CypherQueryFilterType.EQUAL, row["codigo"], Neo4jDataType.INTEGER)

            unidade_sigla_filter = CypherQueryFilter("sigla", CypherQueryFilterType.EQUAL, row["campus"])

            curso_to_unidade_relationship_query = make_relationship_query(
                "Curso",
                curso_codigo_filter,
                "Unidade",
                unidade_sigla_filter,
                "OFFERED_AT",
            )

            unidade_to_curso_relationship_query = make_relationship_query(
                "Unidade",
                unidade_sigla_filter,
                "Curso",
                curso_codigo_filter,
                "OFFERS",
            )

            with session.begin_transaction() as tx:
                tx.run(create_query)
                tx.run(curso_to_unidade_relationship_query)
                tx.run(unidade_to_curso_relationship_query)

    end = time.perf_counter()
    print(f"Cursos ({cursos_df.shape[0]} linhas): {end - start}s")


def _insert_disciplinas(conn: Neo4jConnection, preprocessed_dir: Path):
    start = time.perf_counter()

    disciplinas_csv = preprocessed_dir / "disciplinas.csv"
    disciplinas_df = pd.read_csv(disciplinas_csv, delimiter=";")

    create_query_builder = CypherCreateQueryBuilder("Disciplina")

    attribute_keys = list(disciplinas_df.columns)
    attribute_keys.remove("codigo_curso")

    transactions_queries: list[tuple] = []

    for _, row in disciplinas_df.iterrows():
        for key in attribute_keys:
            value_type = Neo4jDataType.STRING

            if key in ["codigo", "periodo", "carga_horaria"]:
                value_type = Neo4jDataType.INTEGER

            _cqb_add_property_when_value_not_absent(create_query_builder, key, row[key], value_type)

        create_query = create_query_builder.build()

        disciplina_codigo_filter = CypherQueryFilter(
            "codigo", CypherQueryFilterType.EQUAL, row["codigo"], Neo4jDataType.INTEGER
        )

        curso_codigo_filter = CypherQueryFilter(
            "codigo", CypherQueryFilterType.EQUAL, row["codigo_curso"], Neo4jDataType.INTEGER
        )

        disciplina_to_curso_relationship_query = make_relationship_query(
            "Disciplina",
            disciplina_codigo_filter,
            "Curso",
            curso_codigo_filter,
            "TAUGHT_AT"
        )

        curso_to_disciplina_relationship_query = make_relationship_query(
            "Curso",
            curso_codigo_filter,
            "Disciplina",
            disciplina_codigo_filter,
            "OFFERS"
        )

        transactions_queries.append(
            (create_query, disciplina_to_curso_relationship_query, curso_to_disciplina_relationship_query)
        )

    batch_size = 1000

    transactions_batches = [transactions_queries[start_batch_index:start_batch_index + batch_size]
                            for start_batch_index in range(0, len(transactions_queries), batch_size)]

    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(run_transactions_batch, conn, batch) for batch in transactions_batches]

        concurrent.futures.wait(futures)

    end = time.perf_counter()
    print(f"Disciplinas ({disciplinas_df.shape[0]} linhas): {end - start}s")


def _insert_disciplinas_ministradas(conn: Neo4jConnection, preprocessed_dir: Path):
    start = time.perf_counter()

    disciplinas_ministradas_csv = preprocessed_dir / "disciplinas_ministradas.csv"
    disciplinas_ministradas_df = pd.read_csv(disciplinas_ministradas_csv, delimiter=";")

    create_query_builder = CypherCreateQueryBuilder("DisciplinaMinistrada")

    attribute_keys = list(disciplinas_ministradas_df.columns)
    attribute_keys.remove("codigo_disciplina")

    transactions_queries: list[tuple] = []

    for _, row in disciplinas_ministradas_df.iterrows():
        for key in attribute_keys:
            value_type = Neo4jDataType.STRING

            if key in ["codigo", "ano_letivo", "periodo_letivo"]:
                value_type = Neo4jDataType.INTEGER

            _cqb_add_property_when_value_not_absent(create_query_builder, key, row[key], value_type)

        create_query = create_query_builder.build()

        disciplina_ministrada_codigo_filter = CypherQueryFilter(
            "codigo", CypherQueryFilterType.EQUAL, row["codigo"], Neo4jDataType.INTEGER
        )

        disciplina_codigo_filter = CypherQueryFilter(
            "codigo", CypherQueryFilterType.EQUAL, row["codigo_disciplina"], Neo4jDataType.INTEGER
        )

        disciplina_ministrada_to_disciplina_relationship_query = make_relationship_query(
            "DisciplinaMinistrada",
            disciplina_ministrada_codigo_filter,
            "Disciplina",
            disciplina_codigo_filter,
            "DEFINED_BY"
        )

        transactions_queries.append(
            (create_query, disciplina_ministrada_to_disciplina_relationship_query)
        )

    batch_size = 2000

    transactions_batches = [transactions_queries[start_batch_index: start_batch_index + batch_size]
                            for start_batch_index in range(0, len(transactions_queries), batch_size)]

    with concurrent.futures.ThreadPoolExecutor(max_workers=100) as executor:
        futures = [executor.submit(run_transactions_batch, conn, batch) for batch in transactions_batches]

        concurrent.futures.wait(futures)

    end = time.perf_counter()
    print(f"Disciplinas Ministradas ({disciplinas_ministradas_df.shape[0]} linhas): {end - start}s")


def _insert_disciplinas_ministradas_docentes(conn: Neo4jConnection, preprocessed_dir: Path):
    start = time.perf_counter()

    disciplinas_ministradas_docentes_csv = preprocessed_dir / "disciplinas_ministradas_docentes.csv"
    disciplinas_ministradas_docentes_df = pd.read_csv(disciplinas_ministradas_docentes_csv, delimiter=";")

    transactions_queries: list[tuple] = []

    for _, row in disciplinas_ministradas_docentes_df.iterrows():
        transactions: list[tuple] = []

        def as_auxiliary_relationship_prop(as_auxiliary: bool):
            return CypherJsonLikeProperty("as_auxiliary", as_auxiliary,
                                          Neo4jDataType.BOOL)

        def docente_siape_query_filter(siape_field_name):
            return CypherQueryFilter(
                "matricula",
                CypherQueryFilterType.EQUAL,
                row[siape_field_name],
                Neo4jDataType.INTEGER
            )

        disciplina_ministrada_codigo_query_filter = CypherQueryFilter(
            "codigo",
            CypherQueryFilterType.EQUAL,
            row["codigo_pauta"],
            Neo4jDataType.INTEGER
        )

        if not pd.isna(row["siape_docente_principal"]):
            docente_to_disciplina_ministrada_relationship_query = make_relationship_query(
                "Docente",
                docente_siape_query_filter("siape_docente_principal"),
                "DisciplinaMinistrada",
                disciplina_ministrada_codigo_query_filter,
                "TAUGHT",
                [as_auxiliary_relationship_prop(False)]
            )

            disciplina_ministrada_to_docente_relationship_query = make_relationship_query(
                "DisciplinaMinistrada",
                disciplina_ministrada_codigo_query_filter,
                "Docente",
                docente_siape_query_filter("siape_docente_principal"),
                "TAUGHT_BY",
                [as_auxiliary_relationship_prop(False)]
            )

            transactions.append((docente_to_disciplina_ministrada_relationship_query,
                                 disciplina_ministrada_to_docente_relationship_query))

        if not pd.isna(row["siape_docente_auxiliar"]):
            docente_to_disciplina_ministrada_relationship_query = make_relationship_query(
                "Docente",
                docente_siape_query_filter("siape_docente_auxiliar"),
                "DisciplinaMinistrada",
                disciplina_ministrada_codigo_query_filter,
                "TAUGHT",
                [as_auxiliary_relationship_prop(True)]
            )

            disciplina_ministrada_to_docente_relationship_query = make_relationship_query(
                "DisciplinaMinistrada",
                disciplina_ministrada_codigo_query_filter,
                "Docente",
                docente_siape_query_filter("siape_docente_auxiliar"),
                "TAUGHT_BY",
                [as_auxiliary_relationship_prop(True)]
            )

            transactions.append((docente_to_disciplina_ministrada_relationship_query,
                                 disciplina_ministrada_to_docente_relationship_query))

        transactions_queries += transactions

    batch_size = 1100

    transactions_batches = [transactions_queries[start_batch_index: start_batch_index + batch_size]
                            for start_batch_index in range(0, len(transactions_queries), batch_size)]

    with concurrent.futures.ThreadPoolExecutor(max_workers=100) as executor:
        futures = [executor.submit(run_transactions_batch, conn, batch) for batch in transactions_batches]

        concurrent.futures.wait(futures)

    end = time.perf_counter()

    print(f"Disciplinas Ministradas Docentes ({disciplinas_ministradas_docentes_df.shape[0]} linhas): {end - start}s")


def _cqb_add_property_when_value_not_absent(query_builder: CypherCreateQueryBuilder, key, value,
                                            value_type: Neo4jDataType):
    if not pd.isna(value):
        query_builder.add_property(key, value, value_type)

    return query_builder


def execute():
    neo4j_conn = make_neo4j_bolt_connection(Environment.neo4j_user, Environment.neo4j_password,
                                            Environment.neo4j_host, Environment.neo4j_port)

    try:
        preprocessed_dir = Storage.get_dir("dados_abertos/preprocessed")

        _insert_unidades(neo4j_conn, preprocessed_dir)
        _insert_docentes(neo4j_conn, preprocessed_dir)
        _insert_taes(neo4j_conn, preprocessed_dir)
        _insert_cursos(neo4j_conn, preprocessed_dir)
        _insert_disciplinas(neo4j_conn, preprocessed_dir)
        _insert_disciplinas_ministradas(neo4j_conn, preprocessed_dir)
        _insert_disciplinas_ministradas_docentes(neo4j_conn, preprocessed_dir)
    finally:
        neo4j_conn.close()


if __name__ == '__main__':
    execute()
