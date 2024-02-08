import time
from pathlib import Path

import pandas as pd

from app.build_kg.database import (CypherJsonLikeProperty, Neo4jConnection,
                                   Neo4jDataType, make_neo4j_bolt_connection,
                                   make_relationship_query)
from app.build_kg.utils import GeneralFilters
from app.utils.environment import Environment
from app.utils.storage import Storage


def execute(conn: Neo4jConnection, disciplinas_ministradas_docentes_csv: Path):
    disciplinas_ministradas_docentes_df = pd.read_csv(disciplinas_ministradas_docentes_csv, delimiter=";")

    transactions = disciplinas_ministradas_docentes_df.apply(_create_disciplina_ministrada_docente_transaction, axis=1)

    start = time.perf_counter()
    conn.run_transactions_batched(transactions, 2700, 300)
    end = time.perf_counter()

    print(
        f"[dados_abertos] Disciplinas Ministradas Docentes ({disciplinas_ministradas_docentes_df.shape[0]} linhas): {end - start}s")


def _create_disciplina_ministrada_docente_transaction(row):
    transaction = []

    if pd.notna(row["siape_docente_principal"]):
        transaction = [*_create_teaching_relationship_queries(
            row["siape_docente_principal"],
            row["codigo_pauta"],
            False
        )]

    if pd.notna(row["siape_docente_auxiliar"]):
        transaction = [*transaction, *_create_teaching_relationship_queries(
            row["siape_docente_auxiliar"],
            row["codigo_pauta"],
            True
        )]

    return tuple(transaction)


def _create_teaching_relationship_queries(teacher_siape: int, ministered_subject_code: int, as_auxiliary: bool):
    disciplina_ministrada_to_docente = make_relationship_query(
        "DisciplinaMinistrada",
        GeneralFilters.integer_codigo_filter(ministered_subject_code),
        "Docente",
        GeneralFilters.integer_filter("matricula", teacher_siape),
        "TAUGHT_BY",
        [_RelationshipProps.as_auxiliary(as_auxiliary)]
    )

    docente_to_disciplina_ministrada = make_relationship_query(
        "Docente",
        GeneralFilters.integer_filter("matricula", teacher_siape),
        "DisciplinaMinistrada",
        GeneralFilters.integer_codigo_filter(ministered_subject_code),
        "TAUGHT",
        [_RelationshipProps.as_auxiliary(as_auxiliary)]
    )

    return disciplina_ministrada_to_docente, docente_to_disciplina_ministrada


class _RelationshipProps:

    @staticmethod
    def as_auxiliary(value: bool):
        return CypherJsonLikeProperty("as_auxiliary", value, Neo4jDataType.BOOL)


if __name__ == "__main__":
    execute(
        make_neo4j_bolt_connection(Environment.neo4j_user, Environment.neo4j_password,
                                   Environment.neo4j_host, Environment.neo4j_port),
        Storage.get_file("dados_abertos/preprocessed/disciplinas_ministradas_docentes.csv")
    )
