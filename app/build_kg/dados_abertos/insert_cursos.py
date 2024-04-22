import time
from pathlib import Path

import pandas as pd

from app.build_kg.database import (CypherCreateQueryBuilder, Neo4jConnection,
                                   Neo4jDataType, make_neo4j_bolt_connection,
                                   make_relationship_query)
from app.build_kg.utils import (GeneralFilters,
                                cqb_add_property_when_value_not_absent)
from app.utils.environment import Environment
from app.utils.storage import Storage


def execute(conn: Neo4jConnection, cursos_csv: Path):
    cursos_df = pd.read_csv(cursos_csv, delimiter=";")

    transactions = cursos_df.apply(_create_curso_transaction, axis=1)

    start = time.perf_counter()
    conn.run_transactions_batched(transactions, 10, 200)
    end = time.perf_counter()

    conn.query("CREATE INDEX curso_codigo FOR (c:Curso) ON (c.codigo)")

    print(f"[dados_abertos] Cursos ({cursos_df.shape[0]} linhas): {end - start}s")


def _create_curso_transaction(row):
    create_query = _create_curso_query(row)
    curso_to_unidade_rel_query = _create_curso_to_unidade_relationship_query(row)
    unidade_to_curso_rel_query = _create_unidade_to_curso_relationship_query(row)

    return create_query, curso_to_unidade_rel_query, unidade_to_curso_rel_query


def _create_curso_query(row):
    properties_keys = list(row.index)

    properties_keys.remove("campus")

    create_query_builder = CypherCreateQueryBuilder("Curso")

    for property_key in properties_keys:
        value_type = Neo4jDataType.STRING

        if property_key in ["codigo", "qtd_vagas_ano", "qtd_semestres"] or property_key.startswith("ch_"):
            value_type = Neo4jDataType.INTEGER

        cqb_add_property_when_value_not_absent(
            create_query_builder,
            property_key,
            row[property_key],
            value_type
        )

    return create_query_builder.build()


def _create_curso_to_unidade_relationship_query(row):
    return make_relationship_query(
        "Curso",
        GeneralFilters.integer_codigo_filter(row["codigo"]),
        "Unidade",
        GeneralFilters.string_filter("sigla", row["campus"]),
        "OFFERED_AT"
    )


def _create_unidade_to_curso_relationship_query(row):
    return make_relationship_query(
        "Unidade",
        GeneralFilters.string_filter("sigla", row["campus"]),
        "Curso",
        GeneralFilters.integer_codigo_filter(row["codigo"]),
        "OFFERS"
    )


if __name__ == "__main__":
    execute(
        make_neo4j_bolt_connection(Environment.neo4j_user, Environment.neo4j_password,
                                   Environment.neo4j_host, Environment.neo4j_port),
        Storage.get_file("dados_abertos/preprocessed/cursos.csv")
    )
