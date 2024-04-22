import csv
import datetime
import json
import time
import uuid
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import pandas as pd

from app.build_kg.database import (CypherJsonLikeProperty, Neo4jConnection,
                                   Neo4jDataType, make_neo4j_bolt_connection,
                                   make_relationship_query)
from app.build_kg.utils import GeneralFilters
from app.utils.environment import Environment
from app.utils.storage import Storage


def create_log_json(total_seconds: float, query_count: int, execution_details: dict):
    r = {
        "execution_id": str(uuid.uuid4()),
        "created_at": str(datetime.datetime.now()),
        "execution_duration": str(datetime.timedelta(seconds=total_seconds)),
        "query_count": query_count,
        "queries_per_second": query_count / total_seconds,
        "execution_details": execution_details
    }

    return f"\n{json.dumps(r)}"


def execute(conn: Neo4jConnection, disciplinas_ministradas_docentes_csv: Path, profiling=False):
    """
    rollback query:
    MATCH (n:DisciplinaMinistrada)<-[r:TAUGHT]-(:Docente) DETACH DELETE r;
    MATCH (n:DisciplinaMinistrada)-[r:TAUGHT_BY]->(:Docente) DETACH DELETE r

    example query:
    MATCH (a:DisciplinaMinistrada), (b:Docente) WHERE a.codigo = 117006 AND b.matricula = 2116924 CREATE (a)-[r:TAUGHT_BY {as_auxiliary: false}]->(b);
    MATCH (a:Docente), (b:DisciplinaMinistrada) WHERE a.matricula = 2116924 AND b.codigo = 117006 CREATE (a)-[r:TAUGHT {as_auxiliary: false}]->(b)
    """
    disciplinas_ministradas_docentes_df = pd.read_csv(disciplinas_ministradas_docentes_csv, delimiter=";")

    transactions = disciplinas_ministradas_docentes_df.apply(_create_disciplina_ministrada_docente_transaction, axis=1)

    batch_size = 3500
    max_workers = 100

    start = time.perf_counter()
    conn.run_transactions_batched(transactions, batch_size, max_workers)
    end = time.perf_counter()

    print(
        f"[dados_abertos] Disciplinas Ministradas Docentes ({disciplinas_ministradas_docentes_df.shape[0]} linhas): {end - start}s")


# TODO: usar como referência de use-case no refactor do database.py
# Todos os métodos do nosso "micro-ORM" ficaram muito focados em inserções únicas desconsiderando tarefas básicas e
# obrigatórias de otimização na escrita de consultas, que devem ser realizadas por parte de quem está escrevendo-as.
def execute_v2(conn: Neo4jConnection, disciplinas_ministradas_docentes_csv: Path):
    with open(disciplinas_ministradas_docentes_csv, newline="", mode="r") as csvfile:
        reader = csv.DictReader(csvfile, delimiter=";")
        data = [row for row in reader]

    queries = [
        "MATCH (a:DisciplinaMinistrada), (b:Docente) WHERE a.codigo = $codigo AND b.matricula = $matricula CREATE (a)-[r:TAUGHT_BY {as_auxiliary: $as_auxiliary}]->(b)",
        "MATCH (a:Docente), (b:DisciplinaMinistrada) WHERE a.matricula = $matricula AND b.codigo = $codigo CREATE (a)-[r:TAUGHT {as_auxiliary: $as_auxiliary}]->(b)"
    ]

    query_args = []

    def make_args(codigo_disciplina_ministrada, matricula, as_auxilary):
        return {
            "codigo": codigo_disciplina_ministrada,
            "matricula": matricula,
            "as_auxiliary": as_auxilary
        }

    for row in data:
        codigo_pauta = int(row["codigo_pauta"])

        if row["siape_docente_principal"]:
            matricula_docente_principal = int(row["siape_docente_principal"])
            query_args.append(make_args(codigo_pauta, matricula_docente_principal, False))

        if row["siape_docente_auxiliar"]:
            matricula_docente_auxiliar = int(row["siape_docente_auxiliar"])
            query_args.append(make_args(codigo_pauta, matricula_docente_auxiliar, True))

    batch_size = 3500
    max_workers = 100

    start = time.perf_counter()

    batches = conn.make_batches(query_args, batch_size)

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        for query in queries:
            futures = [executor.submit(conn.run_parametrized_query_with_args_list, query, batch) for batch in batches]

            for future in as_completed(futures):
                future.result()

    end = time.perf_counter()

    print(
        f"[dados_abertos] Disciplinas Ministradas Docentes ({len(data)} linhas): {end - start}s")

    with open("insertion_log.json", "a") as f:
        log = create_log_json(
            end - start,
            len(query_args) * 2,
            {
                "batch_size": batch_size,
                "max_workers": max_workers,
            }
        )

        f.write(log)


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
