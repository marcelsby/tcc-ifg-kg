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


def execute(conn: Neo4jConnection, discentes_csv: Path):
    discentes_df = pd.read_csv(discentes_csv, delimiter=";")

    transactions = discentes_df.apply(_create_discente_transaction, axis=1)

    start = time.perf_counter()
    conn.run_transactions_batched(transactions, 500, 300)
    end = time.perf_counter()

    print(f"[dados_abertos] Discentes ({discentes_df.shape[0]} linhas): {end - start}s")


def _create_discente_transaction(row):
    transaction = []

    properties_to_remove = []

    if pd.notna(row["sigla_campus"]):
        properties_to_remove.append("campus")
        transaction.append(_create_discente_to_unidade_relationship_query(row))

    if pd.notna(row["codigo_curso"]):
        properties_to_remove.append("nome_curso")
        transaction.append(_create_discente_to_curso_relationship_query(row))

    transaction.insert(0, _create_discente_query(row, properties_to_remove))

    return tuple(transaction)


def _create_discente_query(row, properties_to_remove: list[str]):
    properties_keys = list(row.index)

    create_query_builder = CypherCreateQueryBuilder("Discente")

    create_query_builder.remove_properties(["sigla_campus", "codigo_curso", *properties_to_remove])

    for property_key in properties_keys:
        value_type = Neo4jDataType.STRING

        if property_key in ["ano_ingresso", "periodo_letivo_ingresso", "ano_nascimento"]:
            value_type = Neo4jDataType.INTEGER

        cqb_add_property_when_value_not_absent(
            create_query_builder,
            property_key,
            row[property_key],
            value_type
        )

    return create_query_builder.build()


def _create_discente_to_unidade_relationship_query(row):
    return make_relationship_query(
        "Discente",
        GeneralFilters.string_filter("codigo", row["codigo"]),
        "Unidade",
        GeneralFilters.string_filter("sigla", row["sigla_campus"]),
        "STUDY_AT"
    )


def _create_discente_to_curso_relationship_query(row):
    return make_relationship_query(
        "Discente",
        GeneralFilters.string_filter("codigo", row["codigo"]),
        "Curso",
        GeneralFilters.integer_codigo_filter(row["codigo_curso"]),
        "STUDY"
    )


if __name__ == "__main__":
    execute(
        make_neo4j_bolt_connection(Environment.neo4j_user, Environment.neo4j_password,
                                   Environment.neo4j_host, Environment.neo4j_port),
        Storage.get_file("dados_abertos/preprocessed/discentes.csv")
    )
