import time
from pathlib import Path

import pandas as pd

from app.build_kg.database import (CypherCreateQueryBuilder, CypherQueryFilter,
                                   CypherQueryFilterType, Neo4jConnection,
                                   Neo4jDataType, make_neo4j_bolt_connection,
                                   make_relationship_query)
from app.build_kg.utils import cqb_add_property_when_value_not_absent
from app.utils.environment import Environment
from app.utils.storage import Storage


def execute(conn: Neo4jConnection, cidades_csv: Path):
    cidades_df = pd.read_csv(cidades_csv, delimiter=";")

    transactions = cidades_df.apply(_create_cidade_transaction, axis=1)

    start = time.perf_counter()
    conn.run_transactions(transactions)
    end = time.perf_counter()

    print(f"[ifg_produz] Cidades ({cidades_df.shape[0]} linhas): {end - start}s")


def _create_cidade_transaction(row):
    create_query = _create_cidade_query(row)
    cidade_to_uf_rel_query = _create_cidade_to_uf_relationship_query(row)

    return create_query, cidade_to_uf_rel_query


def _create_cidade_query(row):
    properties_keys = list(row.index)

    properties_keys.remove("sigla_uf")
    properties_keys.remove("aliases")

    create_query_builder = CypherCreateQueryBuilder("Cidade")

    for property_key in properties_keys:
        cqb_add_property_when_value_not_absent(
            create_query_builder,
            property_key,
            row[property_key],
            Neo4jDataType.STRING
        )

    return create_query_builder.build()


def _create_cidade_to_uf_relationship_query(row):
    return make_relationship_query(
        "Cidade",
        _Filters.cidade_codigo_filter(row),
        "UnidadeFederativa",
        _Filters.uf_sigla_filter(row),
        "PART_OF"
    )


class _Filters:
    @staticmethod
    def uf_sigla_filter(row):
        return CypherQueryFilter("sigla", CypherQueryFilterType.EQUAL, row["sigla_uf"])

    @staticmethod
    def cidade_codigo_filter(row):
        return CypherQueryFilter("codigo", CypherQueryFilterType.EQUAL, row["codigo"])


if __name__ == '__main__':
    execute(
        make_neo4j_bolt_connection(Environment.neo4j_user, Environment.neo4j_password,
                                   Environment.neo4j_host, Environment.neo4j_port),
        Storage.get_file("ifg_produz/preprocessed/cidades.csv")

    )
