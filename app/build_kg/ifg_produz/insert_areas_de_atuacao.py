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


def execute(conn: Neo4jConnection, areas_de_atuacao_csv: Path):
    areas_de_atuacao_df = pd.read_csv(areas_de_atuacao_csv, delimiter=";")

    transactions = areas_de_atuacao_df.apply(_create_area_de_atuacao_transaction, axis=1)

    start = time.perf_counter()
    conn.run_transactions_batched(transactions, 250, 200)
    end = time.perf_counter()

    print(f"[ifg_produz] Áreas de Atuação ({areas_de_atuacao_df.shape[0]} linhas): {end - start}s")


def _create_area_de_atuacao_transaction(row):
    create_query = _create_area_de_atuacao_query(row)
    curriculo_to_area_de_atuacao_rel_query = _create_curriculo_to_area_de_atuacao_relationship_query(row)

    return create_query, curriculo_to_area_de_atuacao_rel_query


def _create_area_de_atuacao_query(row):
    properties_keys = list(row.index)

    properties_keys.remove("codigo_curriculo")

    create_query_builder = CypherCreateQueryBuilder("AreaAtuacao")

    for property_key in properties_keys:
        value_type = Neo4jDataType.STRING

        if property_key in ["codigo"]:
            value_type = Neo4jDataType.INTEGER

        cqb_add_property_when_value_not_absent(
            create_query_builder,
            property_key,
            row[property_key],
            value_type
        )

    return create_query_builder.build()


def _create_curriculo_to_area_de_atuacao_relationship_query(row):
    return make_relationship_query(
        "Curriculo",
        GeneralFilters.integer_codigo_filter(row["codigo_curriculo"]),
        "AreaAtuacao",
        GeneralFilters.integer_codigo_filter(row["codigo"]),
        "HAS"
    )


if __name__ == '__main__':
    execute(
        make_neo4j_bolt_connection(Environment.neo4j_user, Environment.neo4j_password,
                                   Environment.neo4j_host, Environment.neo4j_port),
        Storage.get_file("ifg_produz/preprocessed/areas_de_atuacao.csv")
    )
