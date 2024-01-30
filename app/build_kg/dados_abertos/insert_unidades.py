import time
from pathlib import Path

import pandas as pd

from app.build_kg.database import (CypherCreateQueryBuilder, Neo4jConnection,
                                   Neo4jDataType, make_neo4j_bolt_connection)
from app.build_kg.utils import cqb_add_property_when_value_not_absent
from app.utils.environment import Environment
from app.utils.storage import Storage


def execute(conn: Neo4jConnection, unidades_csv: Path):
    unidades_df = pd.read_csv(unidades_csv, delimiter=";")

    queries = unidades_df.apply(_create_unidades_queries, axis=1)

    start = time.perf_counter()
    conn.run_queries(tuple(queries))
    end = time.perf_counter()

    print(f"[dados_abertos] Unidades ({unidades_df.shape[0]} linhas): {end - start}s")


def _create_unidades_queries(row):
    properties_keys = list(row.index)

    create_query_builder = CypherCreateQueryBuilder("Unidade")

    for property_key in properties_keys:
        cqb_add_property_when_value_not_absent(
            create_query_builder,
            property_key,
            row[property_key],
            Neo4jDataType.STRING
        )

    return create_query_builder.build()


if __name__ == "__main__":
    execute(
        make_neo4j_bolt_connection(Environment.neo4j_user, Environment.neo4j_password,
                                   Environment.neo4j_host, Environment.neo4j_port),
        Storage.get_file("dados_abertos/preprocessed/unidades.csv")
    )
