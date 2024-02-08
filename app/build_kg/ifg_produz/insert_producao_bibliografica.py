import time
from pathlib import Path

import pandas as pd

from app.build_kg.database import (CypherCreateQueryBuilder, Neo4jConnection,
                                   Neo4jDataType, make_neo4j_bolt_connection,
                                   make_relationship_query)
from app.build_kg.utils import (GeneralFilters,
                                cqb_add_property_when_value_not_absent,
                                remove_properties)
from app.utils.environment import Environment
from app.utils.storage import Storage


def execute(conn: Neo4jConnection, producao_bibliografica_csv: Path, revista_csv: Path, conferencia_csv: Path):
    revista_df = pd.read_csv(revista_csv, delimiter=";")

    queries = revista_df.apply(_create_revista_query, axis=1)

    start = time.perf_counter()
    conn.run_queries_batched(queries, 500, 200)
    end = time.perf_counter()

    print(f"[ifg_produz] Revista ({revista_df.shape[0]} linhas): {end - start}s")

    conferencia_df = pd.read_csv(conferencia_csv, delimiter=";")

    queries = conferencia_df.apply(_create_conferencia_query, axis=1)

    start = time.perf_counter()
    conn.run_queries_batched(queries, 500, 200)
    end = time.perf_counter()

    print(f"[ifg_produz] Conferência ({conferencia_df.shape[0]} linhas): {end - start}s")

    producao_bibliografica_df = pd.read_csv(producao_bibliografica_csv, delimiter=";")

    transactions = producao_bibliografica_df.apply(_create_producao_bibliografica_transaction, axis=1)

    start = time.perf_counter()
    conn.run_transactions_batched(transactions, 500, 200)
    end = time.perf_counter()

    print(f"[ifg_produz] Produção Bibliográfica ({producao_bibliografica_df.shape[0]} linhas): {end - start}s")


def _create_revista_query(row):
    properties_keys = list(row.index)

    create_query_builder = CypherCreateQueryBuilder("Revista")

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


def _create_conferencia_query(row):
    properties_keys = list(row.index)

    create_query_builder = CypherCreateQueryBuilder("Conferencia")

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


def _create_producao_bibliografica_transaction(row):
    transaction = []

    if pd.notna(row["codigo_revista"]):
        transaction.append(_create_producao_bibliografica_to_revista_relationship_query(row))

    if pd.notna(row["codigo_conferencia"]):
        transaction.append(_create_producao_bibliografica_to_conferencia_relationship_query(row))

    transaction.append(_create_curriculo_to_producao_bibliografica_relationship_query(row))
    transaction.insert(0, _create_producao_bibliografica_query(row))

    return tuple(transaction)


def _create_producao_bibliografica_query(row):
    properties_keys = list(row.index)

    properties_to_be_removed = ["codigo_conferencia", "codigo_curriculo", "codigo_revista"]

    properties_keys = remove_properties(properties_to_be_removed, properties_keys)

    create_query_builder = CypherCreateQueryBuilder("ProducaoBibliografica")

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


def _create_curriculo_to_producao_bibliografica_relationship_query(row):
    return make_relationship_query(
        "Curriculo",
        GeneralFilters.integer_codigo_filter(row["codigo_curriculo"]),
        "ProducaoBibliografica",
        GeneralFilters.integer_codigo_filter(row["codigo"]),
        "HAS"
    )


def _create_producao_bibliografica_to_conferencia_relationship_query(row):
    return make_relationship_query(
        "ProducaoBibliografica",
        GeneralFilters.integer_codigo_filter(row["codigo"]),
        "Conferencia",
        GeneralFilters.integer_codigo_filter(row["codigo_conferencia"]),
        "PRESENTED_AT"
    )


def _create_producao_bibliografica_to_revista_relationship_query(row):
    return make_relationship_query(
        "ProducaoBibliografica",
        GeneralFilters.integer_codigo_filter(row["codigo"]),
        "Revista",
        GeneralFilters.integer_codigo_filter(row["codigo_revista"]),
        "PRESENTED_AT"
    )


if __name__ == '__main__':
    execute(
        make_neo4j_bolt_connection(Environment.neo4j_user, Environment.neo4j_password,
                                   Environment.neo4j_host, Environment.neo4j_port),
        Storage.get_file("ifg_produz/preprocessed/producao_bibliografica.csv"),
        Storage.get_file("ifg_produz/preprocessed/revista.csv"),
        Storage.get_file("ifg_produz/preprocessed/conferencia.csv")
    )
