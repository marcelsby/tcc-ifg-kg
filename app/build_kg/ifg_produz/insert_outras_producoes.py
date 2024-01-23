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


def execute(conn: Neo4jConnection, outras_producoes_csv: Path):
    outras_producoes_df = pd.read_csv(outras_producoes_csv, delimiter=";")

    transactions = outras_producoes_df.apply(_create_outra_producao_transaction, axis=1)

    start = time.perf_counter()
    conn.run_transactions_batched(transactions, 250, 200)
    end = time.perf_counter()

    print(f"[ifg_produz] Outras Produções ({outras_producoes_df.shape[0]} linhas): {end - start}s")


def _create_outra_producao_transaction(row):
    create_query = _create_outra_producao_query(row)
    curriculo_to_producao_tecnica_rel_query = _create_curriculo_to_outra_producao_relationship_query(row)

    return create_query, curriculo_to_producao_tecnica_rel_query


def _create_outra_producao_query(row):
    properties_keys = list(row.index)

    properties_keys.remove("codigo_curriculo")

    create_query_builder = CypherCreateQueryBuilder("OutraProducao")

    for property_key in properties_keys:
        value_type = Neo4jDataType.STRING

        if property_key in ["codigo", "ano"]:
            value_type = Neo4jDataType.INTEGER

        cqb_add_property_when_value_not_absent(
            create_query_builder,
            property_key,
            row[property_key],
            value_type
        )

    return create_query_builder.build()


def _create_curriculo_to_outra_producao_relationship_query(row):
    return make_relationship_query(
        "Curriculo",
        GeneralFilters.integer_codigo_filter(row["codigo_curriculo"]),
        "OutraProducao",
        GeneralFilters.integer_codigo_filter(row["codigo"]),
        "HAS"
    )


if __name__ == '__main__':
    execute(
        make_neo4j_bolt_connection(Environment.neo4j_user, Environment.neo4j_password,
                                   Environment.neo4j_host, Environment.neo4j_port),
        Storage.get_file("ifg_produz/preprocessed/outras_producoes.csv")
    )
