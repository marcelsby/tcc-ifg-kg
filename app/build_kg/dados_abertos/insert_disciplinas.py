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


def execute(conn: Neo4jConnection, disciplinas_csv: Path):
    disciplinas_df = pd.read_csv(disciplinas_csv, delimiter=";")

    transactions = disciplinas_df.apply(_create_disciplina_transaction, axis=1)

    start = time.perf_counter()
    conn.run_transactions_batched(transactions, 50, 200)
    end = time.perf_counter()

    conn.query("CREATE INDEX disciplina_codigo FOR (d:Disciplina) ON (d.codigo)")

    print(f"[dados_abertos] Disciplinas ({disciplinas_df.shape[0]} linhas): {end - start}s")


def _create_disciplina_transaction(row):
    create_query = _create_curso_query(row)
    disciplina_to_curso_rel_query = _create_disciplina_to_curso_relationship_query(row)
    curso_to_disciplina_rel_query = _create_curso_to_disciplina_relationship_query(row)

    return create_query, disciplina_to_curso_rel_query, curso_to_disciplina_rel_query


def _create_curso_query(row):
    properties_keys = list(row.index)

    properties_keys.remove("codigo_curso")

    create_query_builder = CypherCreateQueryBuilder("Disciplina")

    for property_key in properties_keys:
        value_type = Neo4jDataType.STRING

        if property_key in ["codigo", "periodo", "carga_horaria"]:
            value_type = Neo4jDataType.INTEGER

        cqb_add_property_when_value_not_absent(
            create_query_builder,
            property_key,
            row[property_key],
            value_type
        )

    return create_query_builder.build()


def _create_disciplina_to_curso_relationship_query(row):
    return make_relationship_query(
        "Disciplina",
        GeneralFilters.integer_codigo_filter(row["codigo"]),
        "Curso",
        GeneralFilters.integer_codigo_filter(row["codigo_curso"]),
        "TAUGHT_AT"
    )


def _create_curso_to_disciplina_relationship_query(row):
    return make_relationship_query(
        "Curso",
        GeneralFilters.integer_codigo_filter(row["codigo_curso"]),
        "Disciplina",
        GeneralFilters.integer_codigo_filter(row["codigo"]),
        "OFFERS"
    )


if __name__ == "__main__":
    execute(
        make_neo4j_bolt_connection(Environment.neo4j_user, Environment.neo4j_password,
                                   Environment.neo4j_host, Environment.neo4j_port),
        Storage.get_file("dados_abertos/preprocessed/disciplinas.csv")
    )
