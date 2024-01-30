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


def execute(conn: Neo4jConnection, docentes_csv: Path):
    docentes_df = pd.read_csv(docentes_csv, delimiter=";")

    transactions = docentes_df.apply(_create_docente_transaction, axis=1)

    start = time.perf_counter()
    conn.run_transactions_batched(transactions, 100, 200)
    end = time.perf_counter()

    print(f"[dados_abertos] Docentes ({docentes_df.shape[0]} linhas): {end - start}s")


def _create_docente_transaction(row):
    create_query = _create_docente_query(row)
    to_unidade_rel_query = _create_docente_to_unidade_relationship_query(row)

    return create_query, to_unidade_rel_query


def _create_docente_query(row):
    properties_keys = list(row.index)

    properties_keys.remove("campus")

    create_query_builder = CypherCreateQueryBuilder(["Docente", "Servidor"])

    for property_key in properties_keys:
        value_type = Neo4jDataType.STRING

        if property_key == "matricula":
            value_type = Neo4jDataType.INTEGER

        if property_key == "data_ingresso":
            value_type = Neo4jDataType.DATE

        cqb_add_property_when_value_not_absent(
            create_query_builder,
            property_key,
            row[property_key],
            value_type
        )

    return create_query_builder.build()


def _create_docente_to_unidade_relationship_query(row):
    return make_relationship_query(
        "Docente",
        GeneralFilters.integer_filter("matricula", row["matricula"]),
        "Unidade",
        GeneralFilters.string_filter("nome", row["campus"]),
        "PART_OF"
    )


if __name__ == "__main__":
    execute(
        make_neo4j_bolt_connection(Environment.neo4j_user, Environment.neo4j_password,
                                   Environment.neo4j_host, Environment.neo4j_port),
        Storage.get_file("dados_abertos/preprocessed/docentes.csv")
    )
