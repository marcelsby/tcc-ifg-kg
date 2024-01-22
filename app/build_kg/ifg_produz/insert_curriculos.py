import ast
import time
from pathlib import Path

import pandas as pd

from app.build_kg.database import (CypherCreateQueryBuilder,
                                   CypherJsonLikeProperty, CypherQueryFilter,
                                   CypherQueryFilterType, Neo4jConnection,
                                   Neo4jDataType, make_neo4j_bolt_connection,
                                   make_relationship_query)
from app.build_kg.utils import cqb_add_property_when_value_not_absent
from app.utils.environment import Environment
from app.utils.storage import Storage


def execute(conn: Neo4jConnection, curriculos_csv: Path):
    curriculos_df = pd.read_csv(curriculos_csv, delimiter=";", converters={"aceitando_email": bool})

    transactions = curriculos_df.apply(_create_curriculo_transaction, axis=1)

    start = time.perf_counter()
    conn.run_transactions_batched(transactions, 200, 150)
    end = time.perf_counter()

    print(f"[ifg_produz] Currículos ({curriculos_df.shape[0]} linhas): {end - start}s")


def _create_curriculo_transaction(row):
    transaction = []

    if pd.notna(row["palavra_chave"]):
        transaction = [*_create_curriculo_to_palavra_chave_relationship_queries(row)]

    if pd.notna(row["codigo_cidade_nascimento"]):
        transaction.append(_create_curriculo_to_cidade_relationship_query(row))

    transaction.insert(0, _create_curriculo_query(row))
    transaction.insert(2, _create_servidor_to_curriculo_relationship_query(row))

    return transaction


def _create_curriculo_query(row):
    properties_keys = [key for key in list(row.index) if key not in ["uf_nascimento",
                                                                     "cidade_nascimento",
                                                                     "palavra_chave",
                                                                     "siape",
                                                                     "codigo_cidade_nascimento",
                                                                     "sigla_campus_atual",
                                                                     "categoria",
                                                                     "campus_atual"]]
    create_query_builder = CypherCreateQueryBuilder("Curriculo")

    for property_key in properties_keys:
        value_type = Neo4jDataType.STRING

        if property_key == "codigo":
            value_type = Neo4jDataType.INTEGER
        elif property_key == "data_nascimento":
            value_type = Neo4jDataType.DATE
        elif property_key == "aceitando_email":
            value_type = Neo4jDataType.BOOL

        cqb_add_property_when_value_not_absent(
            create_query_builder,
            property_key,
            row[property_key],
            value_type
        )

    return create_query_builder.build()


def _create_curriculo_to_cidade_relationship_query(row):
    return make_relationship_query(
        "Servidor",
        _Filters.servidor_matricula_filter(row["siape"]),
        "Cidade",
        _Filters.cidade_codigo_filter(row["codigo_cidade_nascimento"]),
        "BORN_AT"
    )


def _create_curriculo_to_palavra_chave_relationship_queries(row):
    rel_queries = []

    for palavra in ast.literal_eval(row["palavra_chave"]):
        rel_query = make_relationship_query(
            "Curriculo",
            _Filters.curriculo_codigo_filter(row["codigo"]),
            "PalavraChave",
            _Filters.palavra_chave_palavra_filter(palavra["palavra"]),
            "HAS",
            [CypherJsonLikeProperty("importancia", palavra["importancia"], Neo4jDataType.INTEGER)]
        )

        rel_queries.append(rel_query)

    return rel_queries


def _create_servidor_to_curriculo_relationship_query(row):
    return make_relationship_query(
        "Servidor",
        _Filters.servidor_matricula_filter(row["siape"]),
        "Curriculo",
        _Filters.curriculo_codigo_filter(row["codigo"]),
        "HAS"
    )


class _Filters:
    @staticmethod
    def servidor_matricula_filter(matricula):
        return CypherQueryFilter("matricula", CypherQueryFilterType.EQUAL, matricula,
                                 Neo4jDataType.INTEGER)

    @staticmethod
    def cidade_codigo_filter(codigo):
        return CypherQueryFilter("codigo", CypherQueryFilterType.EQUAL,
                                 codigo)

    @staticmethod
    def curriculo_codigo_filter(codigo):
        return CypherQueryFilter("codigo", CypherQueryFilterType.EQUAL, codigo,
                                 Neo4jDataType.INTEGER)

    @staticmethod
    def palavra_chave_palavra_filter(palavra):
        return CypherQueryFilter("palavra", CypherQueryFilterType.EQUAL, palavra)


if __name__ == '__main__':
    execute(
        make_neo4j_bolt_connection(Environment.neo4j_user, Environment.neo4j_password,
                                   Environment.neo4j_host, Environment.neo4j_port),
        Storage.get_file("ifg_produz/preprocessed/curriculos.csv")
    )
