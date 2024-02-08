import time
from datetime import timedelta

from app.build_kg.dados_abertos import inserter as dados_abertos_inserter
from app.build_kg.database import make_neo4j_bolt_connection
from app.build_kg.ifg_produz import inserter as ifg_produz_inserter
from app.utils.environment import Environment


def execute():
    conn = make_neo4j_bolt_connection(
        Environment.neo4j_user,
        Environment.neo4j_password,
        Environment.neo4j_host,
        Environment.neo4j_port
    )

    start = time.perf_counter()

    dados_abertos_inserter.insert(conn)
    ifg_produz_inserter.insert(conn)

    end = time.perf_counter()

    print(f"Tempo para realizar todas as inserções: {timedelta(seconds=end - start)}")


if __name__ == '__main__':
    execute()
