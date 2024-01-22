from app.build_kg.database import make_neo4j_bolt_connection
from app.build_kg.ifg_produz import (insert_cidades, insert_palavras_chaves,
                                     insert_unidades_federativas, insert_curriculos)
from app.utils.environment import Environment
from app.utils.storage import Storage


def insert():
    conn = make_neo4j_bolt_connection(Environment.neo4j_user, Environment.neo4j_password,
                                      Environment.neo4j_host, Environment.neo4j_port)

    insert_unidades_federativas.execute(
        conn,
        Storage.get_file("ifg_produz/preprocessed/unidades_federativas.csv")
    )

    insert_cidades.execute(
        conn,
        Storage.get_file("ifg_produz/preprocessed/cidades.csv")
    )

    insert_palavras_chaves.execute(
        conn,
        Storage.get_file("ifg_produz/preprocessed/palavras_chaves.csv")
    )

    insert_curriculos.execute(
        conn,
        Storage.get_file("ifg_produz/preprocessed/curriculos.csv")
    )


if __name__ == '__main__':
    insert()
