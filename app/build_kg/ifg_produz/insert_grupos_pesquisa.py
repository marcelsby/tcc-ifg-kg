import ast
import time
from pathlib import Path

import pandas as pd

from app.build_kg.database import (CypherCreateQueryBuilder, Neo4jConnection,
                                   Neo4jDataType, make_neo4j_bolt_connection,
                                   make_relationship_query, CypherJsonLikeProperty)
from app.build_kg.utils import (GeneralFilters,
                                cqb_add_property_when_value_not_absent,
                                remove_properties)
from app.utils.environment import Environment
from app.utils.storage import Storage


def execute(conn: Neo4jConnection,
            grupos_pesquisa_csv: Path,
            linhas_pesquisa_csv: Path,
            discentes_csv: Path,
            intermediaria_csv: Path):
    linhas_pesquisa_df = pd.read_csv(linhas_pesquisa_csv, delimiter=";")

    queries = linhas_pesquisa_df.apply(_create_linha_pesquisa_query, axis=1)

    start = time.perf_counter()
    conn.run_queries_batched(queries, 15, 200)
    end = time.perf_counter()

    print(f"[ifg_produz] Linhas de Pesquisa ({linhas_pesquisa_df.shape[0]} linhas): {end - start}s")

    intermediaria_df = pd.read_csv(intermediaria_csv, delimiter=";")

    queries = intermediaria_df.apply(_create_curriculo_to_linha_pesquisa_relationship_query, axis=1)

    start = time.perf_counter()
    conn.run_queries_batched(queries, 10, 200)
    end = time.perf_counter()

    print(f"[ifg_produz] Currículo -[:STUDY]-> Linha de Pesquisa ({intermediaria_df.shape[0]} linhas): {end - start}s")

    grupos_pesquisa_df = pd.read_csv(grupos_pesquisa_csv, delimiter=";")

    transactions = grupos_pesquisa_df.apply(_create_grupo_pesquisa_transaction, axis=1)

    start = time.perf_counter()
    conn.run_transactions_batched(transactions, 5, 200)
    end = time.perf_counter()

    print(f"[ifg_produz] Grupos de Pesquisa ({grupos_pesquisa_df.shape[0]} linhas): {end - start}s")

    discentes_df = pd.read_csv(discentes_csv, delimiter=";")

    transactions = discentes_df.apply(_create_discente_grupo_pesquisa_transaction, axis=1)

    start = time.perf_counter()
    conn.run_transactions_batched(transactions, 8, 200)
    end = time.perf_counter()

    print(f"[ifg_produz] Discentes dos Grupos de Pesquisa ({discentes_df.shape[0]} linhas): {end - start}s")


# Linha de pesquisa
def _create_linha_pesquisa_query(row):
    properties_keys = list(row.index)

    create_query_builder = CypherCreateQueryBuilder("LinhaPesquisa")

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


def _create_curriculo_to_linha_pesquisa_relationship_query(row):
    return make_relationship_query(
        "Curriculo",
        GeneralFilters.integer_codigo_filter(row["id_curriculo"]),
        "LinhaPesquisa",
        GeneralFilters.integer_codigo_filter(row["id_linha"]),
        "STUDY",
        [CypherJsonLikeProperty("at_research_group", row["id_grupo"], Neo4jDataType.INTEGER)]
    )


# Grupo de Pesquisa
def _create_grupo_pesquisa_transaction(row):
    transaction = []

    # Liderança
    if pd.notna(row["codigo_lider"]):
        transaction = [*transaction, *_create_grupo_pesquisa_leader_relationship_query(row)]

    # Currículos Membros
    transaction = [*transaction, *_create_grupo_pesquisa_members_relationship_queries(row)]

    # Linhas de pesquisa que este grupo estuda
    transaction = [*transaction, *_create_grupo_pesquisa_research_lines_queries(row)]

    # Grupo de Pesquisa
    transaction.insert(0, _create_grupo_pesquisa_query(row))

    return tuple(transaction)


def _create_grupo_pesquisa_query(row):
    properties_keys = list(row.index)

    properties_to_be_removed = ["codigo_lider", "codigos_linhas_de_pesquisa", "codigo_membros"]

    if pd.notna(row["codigo_lider"]):
        properties_to_be_removed.append("nome_lider")

    properties_keys = remove_properties(properties_to_be_removed, properties_keys)

    create_query_builder = CypherCreateQueryBuilder("GrupoPesquisa")

    for property_key in properties_keys:
        value_type = Neo4jDataType.STRING

        if property_key in ["codigo", "ano_formacao"]:
            value_type = Neo4jDataType.INTEGER

        cqb_add_property_when_value_not_absent(
            create_query_builder,
            property_key,
            row[property_key],
            value_type
        )

    return create_query_builder.build()


def _create_grupo_pesquisa_leader_relationship_query(row):
    grupo_pesquisa_to_curriculo = make_relationship_query(
        "GrupoPesquisa",
        GeneralFilters.integer_codigo_filter(row["codigo"]),
        "Curriculo",
        GeneralFilters.integer_codigo_filter(row["codigo_lider"]),
        "LEADED_BY"
    )

    curriculo_to_grupo_pesquisa = make_relationship_query(
        "Curriculo",
        GeneralFilters.integer_codigo_filter(row["codigo_lider"]),
        "GrupoPesquisa",
        GeneralFilters.integer_codigo_filter(row["codigo"]),
        "LEADER_OF"
    )

    return [grupo_pesquisa_to_curriculo, curriculo_to_grupo_pesquisa]


def _create_grupo_pesquisa_members_relationship_queries(row):
    queries = []

    for member_code in ast.literal_eval(row["codigo_membros"]):
        queries.append(make_relationship_query(
            "Curriculo",
            GeneralFilters.integer_codigo_filter(member_code),
            "GrupoPesquisa",
            GeneralFilters.integer_codigo_filter(row["codigo"]),
            "PART_OF"
        ))

        queries.append(make_relationship_query(
            "GrupoPesquisa",
            GeneralFilters.integer_codigo_filter(row["codigo"]),
            "Curriculo",
            GeneralFilters.integer_codigo_filter(member_code),
            "HAS_MEMBER"
        ))

    return queries


def _create_grupo_pesquisa_research_lines_queries(row):
    queries = []

    for research_line_code in ast.literal_eval(row["codigos_linhas_de_pesquisa"]):
        queries.append(make_relationship_query(
            "GrupoPesquisa",
            GeneralFilters.integer_codigo_filter(row["codigo"]),
            "LinhaPesquisa",
            GeneralFilters.integer_codigo_filter(research_line_code),
            "HAS"
        ))

    return queries


# Discentes membros do Grupo de Pesquisa
def _create_discente_grupo_pesquisa_transaction(row):
    transaction = []

    transaction = [*transaction, *_create_discente_grupo_pesquisa_to_grupo_pesquisa_relationship_queries(row)]

    transaction.insert(0, _create_discente_grupo_pesquisa_query(row))

    return tuple(transaction)


def _create_discente_grupo_pesquisa_query(row):
    properties_keys = list(row.index)

    properties_keys.remove("codigo_grupo_de_pesquisa")

    create_query_builder = CypherCreateQueryBuilder("DiscenteGrupoPesquisa")

    for property_key in properties_keys:
        value_type = Neo4jDataType.STRING

        if property_key == "codigo":
            value_type = Neo4jDataType.INTEGER

        cqb_add_property_when_value_not_absent(
            create_query_builder,
            property_key,
            row[property_key],
            value_type
        )

    return create_query_builder.build()


def _create_discente_grupo_pesquisa_to_grupo_pesquisa_relationship_queries(row):
    discente_to_grupo_pesquisa = make_relationship_query(
        "DiscenteGrupoPesquisa",
        GeneralFilters.integer_codigo_filter(row["codigo"]),
        "GrupoPesquisa",
        GeneralFilters.integer_codigo_filter(row["codigo_grupo_de_pesquisa"]),
        "PART_OF"
    )

    grupo_pesquisa_to_discente = make_relationship_query(
        "GrupoPesquisa",
        GeneralFilters.integer_codigo_filter(row["codigo_grupo_de_pesquisa"]),
        "DiscenteGrupoPesquisa",
        GeneralFilters.integer_codigo_filter(row["codigo"]),
        "HAS_MEMBER"
    )

    return [discente_to_grupo_pesquisa, grupo_pesquisa_to_discente]


if __name__ == '__main__':
    execute(
        make_neo4j_bolt_connection(Environment.neo4j_user, Environment.neo4j_password,
                                   Environment.neo4j_host, Environment.neo4j_port),
        Storage.get_file("ifg_produz/preprocessed/grupos_de_pesquisa.csv"),
        Storage.get_file("ifg_produz/preprocessed/linhas_de_pesquisa.csv"),
        Storage.get_file("ifg_produz/preprocessed/alunos.csv"),
        Storage.get_file("ifg_produz/preprocessed/curriculo_grupos.csv")
    )
