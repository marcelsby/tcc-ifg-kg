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


def execute(conn: Neo4jConnection, atuacao_profissional_csv: Path, atividades_csv: Path):
    atuacao_profissional_df = pd.read_csv(atuacao_profissional_csv, delimiter=";")

    atuacao_profissional_transactions = atuacao_profissional_df.apply(_create_atuacao_profissional_transaction, axis=1)

    start = time.perf_counter()
    conn.run_transactions_batched(atuacao_profissional_transactions, 500, 200)
    end = time.perf_counter()

    print(f"[ifg_produz] Atuação Profissional ({atuacao_profissional_df.shape[0]} linhas): {end - start}s")

    atividades_df = pd.read_csv(atividades_csv, delimiter=";")

    atividades_transactions = atividades_df.apply(_create_atividade_transaction, axis=1)

    start = time.perf_counter()
    conn.run_transactions_batched(atividades_transactions, 250, 200)
    end = time.perf_counter()

    print(f"[ifg_produz] Atividades ({atividades_df.shape[0]} linhas): {end - start}s")


def _create_atuacao_profissional_transaction(row):
    create_query = _create_atuacao_profissional_query(row)
    curriculo_to_atuacao_profissional_rel_query = _create_curriculo_to_atuacao_profissional_relationship_query(row)

    return create_query, curriculo_to_atuacao_profissional_rel_query


def _create_atuacao_profissional_query(row):
    properties_keys = list(row.index)

    properties_keys.remove("codigo_curriculo")

    create_query_builder = CypherCreateQueryBuilder("AtuacaoProfissional")

    for property_key in properties_keys:
        value_type = Neo4jDataType.STRING

        if property_key in ["codigo", "ano_trabalho"]:
            value_type = Neo4jDataType.INTEGER

        cqb_add_property_when_value_not_absent(
            create_query_builder,
            property_key,
            row[property_key],
            value_type
        )

    return create_query_builder.build()


def _create_curriculo_to_atuacao_profissional_relationship_query(row):
    return make_relationship_query(
        "Curriculo",
        GeneralFilters.integer_codigo_filter(row["codigo_curriculo"]),
        "AtuacaoProfissional",
        GeneralFilters.integer_codigo_filter(row["codigo"]),
        "HAS"
    )


def _create_atividade_transaction(row):
    create_query = _create_atividade_query(row)
    atuacao_profissional_to_atividade_rel_query = _create_atuacao_profissional_to_atividade_relationship_query(row)

    return create_query, atuacao_profissional_to_atividade_rel_query


def _create_atividade_query(row):
    properties_keys = list(row.index)

    properties_keys.remove("codigo_atuacao_profissional")

    create_query_builder = CypherCreateQueryBuilder("Atividade")

    for property_key in properties_keys:
        value_type = Neo4jDataType.STRING

        if property_key in ["codigo", "ano_inicio"]:
            value_type = Neo4jDataType.INTEGER

        cqb_add_property_when_value_not_absent(
            create_query_builder,
            property_key,
            row[property_key],
            value_type
        )

    return create_query_builder.build()


def _create_atuacao_profissional_to_atividade_relationship_query(row):
    return make_relationship_query(
        "AtuacaoProfissional",
        GeneralFilters.integer_codigo_filter(row["codigo_atuacao_profissional"]),
        "Atividade",
        GeneralFilters.integer_codigo_filter(row["codigo"]),
        "HAS"
    )


if __name__ == '__main__':
    execute(
        make_neo4j_bolt_connection(Environment.neo4j_user, Environment.neo4j_password,
                                   Environment.neo4j_host, Environment.neo4j_port),
        Storage.get_file("ifg_produz/preprocessed/atuacao_profissional.csv"),
        Storage.get_file("ifg_produz/preprocessed/atividades_atuacao_profissional.csv"),
    )
