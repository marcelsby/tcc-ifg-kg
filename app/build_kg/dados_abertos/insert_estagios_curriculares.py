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


def execute(conn: Neo4jConnection, estagios_curriculares_csv: Path):
    estagios_curriculares_df = pd.read_csv(estagios_curriculares_csv, delimiter=";")

    transactions = estagios_curriculares_df.apply(_create_estagio_curricular_transaction, axis=1)

    start = time.perf_counter()
    conn.run_transactions_batched(transactions, 200, 300)
    end = time.perf_counter()

    print(f"[dados_abertos] Estágios Curriculares ({estagios_curriculares_df.shape[0]} linhas): {end - start}s")


def _create_estagio_curricular_transaction(row):
    transaction = []

    properties_to_remove = []

    if pd.notna(row["codigo_curso"]):
        properties_to_remove.extend(["sigla_campus", "curso"])
        transaction.append(_create_estagio_to_curso_relationship_query(row))

    transaction.insert(0, _create_estagio_curricular_query(row, properties_to_remove))

    return tuple(transaction)


def _create_estagio_curricular_query(row, properties_to_remove: list[str]):
    properties_keys = list(row.index)

    properties_keys = remove_properties(["codigo_curso", *properties_to_remove], properties_keys)

    create_query_builder = CypherCreateQueryBuilder("EstagioCurricular")

    for property_key in properties_keys:
        value_type = Neo4jDataType.STRING

        if property_key in ["data_inicio", "data_fim", "data_relatorio"]:
            value_type = Neo4jDataType.DATE

        if property_key == "valor_remuneracao":
            value_type = Neo4jDataType.FLOAT

        cqb_add_property_when_value_not_absent(
            create_query_builder,
            property_key,
            row[property_key],
            value_type
        )

    return create_query_builder.build()


def _create_estagio_to_curso_relationship_query(row):
    return make_relationship_query(
        "EstagioCurricular",
        GeneralFilters.string_filter("codigo", row["codigo"]),
        "Curso",
        GeneralFilters.integer_codigo_filter(row["codigo_curso"]),
        "UNDERTOOK_AT"
    )


if __name__ == "__main__":
    execute(
        make_neo4j_bolt_connection(Environment.neo4j_user, Environment.neo4j_password,
                                   Environment.neo4j_host, Environment.neo4j_port),
        Storage.get_file("dados_abertos/preprocessed/estagios_curriculares.csv")
    )
