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


def execute(conn: Neo4jConnection, disciplinas_ministradas_csv: Path):
    disciplinas_ministradas_df = pd.read_csv(disciplinas_ministradas_csv, delimiter=";")

    transactions = disciplinas_ministradas_df.apply(_create_disciplina_ministrada_transaction, axis=1)

    start = time.perf_counter()
    conn.run_transactions_batched(transactions, 3000, 300)
    end = time.perf_counter()

    print(f"[dados_abertos] Disciplinas Ministradas ({disciplinas_ministradas_df.shape[0]} linhas): {end - start}s")


def _create_disciplina_ministrada_transaction(row):
    create_query = _create_disciplina_ministrada_query(row)
    to_disciplina_rel_query = _create_disciplina_ministrada_to_disciplina_relationship_query(row)

    return create_query, to_disciplina_rel_query


def _create_disciplina_ministrada_query(row):
    properties_keys = list(row.index)

    properties_keys.remove("codigo_disciplina")

    create_query_builder = CypherCreateQueryBuilder("DisciplinaMinistrada")

    for property_key in properties_keys:
        value_type = Neo4jDataType.STRING

        if property_key in ["codigo", "ano_letivo", "periodo_letivo"]:
            value_type = Neo4jDataType.INTEGER

        cqb_add_property_when_value_not_absent(
            create_query_builder,
            property_key,
            row[property_key],
            value_type
        )

    return create_query_builder.build()


def _create_disciplina_ministrada_to_disciplina_relationship_query(row):
    return make_relationship_query(
        "DisciplinaMinistrada",
        GeneralFilters.integer_codigo_filter(row["codigo"]),
        "Disciplina",
        GeneralFilters.integer_codigo_filter(row["codigo_disciplina"]),
        "DEFINED_BY"
    )


if __name__ == "__main__":
    execute(
        make_neo4j_bolt_connection(Environment.neo4j_user, Environment.neo4j_password,
                                   Environment.neo4j_host, Environment.neo4j_port),
        Storage.get_file("dados_abertos/preprocessed/disciplinas_ministradas.csv")
    )
