import logging as log
import csv

from neo4j import GraphDatabase

log.basicConfig(
    level=log.INFO,
    format="[%(asctime)s] [%(levelname)s]: %(message)s",
    datefmt="%d/%m/%Y %I:%M:%S",
)


class Neo4jConnection:
    def __init__(self, uri, user, pwd):
        self.__uri = uri
        self.__user = user
        self.__pwd = pwd
        self.__driver = None

        try:
            self.__driver = GraphDatabase.driver(
                self.__uri, auth=(self.__user, self.__pwd)
            )
            log.info(
                f"Conexão com a instância do Neo4j ({user}@{uri}) foi estabelecida com sucesso!"
            )
        except Exception as e:
            log.critical(str(e))

    def close(self):
        if self.__driver is not None:
            self.__driver.close()

    def query(self, query, db=None):
        assert self.__driver is not None, "Driver not initialized!"

        session = None
        response = None

        try:
            session = (
                self.__driver.session(database=db)
                if db is not None
                else self.__driver.session()
            )
            response = list(session.run(query))
        except Exception as e:
            log.error(f"Erro ao executar a consulta: {str(e)}")
        finally:
            if session is not None:
                session.close()
            return response


conn = Neo4jConnection("bolt://localhost:7687", "neo4j", "test")


def get_create_query(header, values, label: str):
    queries = []

    for i in range(len(values)):
        attr_count = 0
        cypher = f"CREATE (a:{label}) SET"
        for j in range(len(header)):
            cypher += generate_line(header[j], values[i][j], attr_count)
            attr_count += 1
        queries.append(cypher)

    return queries


def generate_line(key, value, attr_count):
    if attr_count == 0:
        return f' a.{key} = "{value}"'
    else:
        return f', a.{key} = "{value}"'


def insert_unidades():
    with open("../dados_abertos/data/transformed/unidades.csv", encoding="UTF-8") as f:
        unidades = csv.reader(f, delimiter=";")

        header = []
        data = []
        is_header = True

        for row in unidades:
            if is_header:
                is_header = not is_header

                for col in range(len(row)):
                    header.append(row[col])
            else:
                data.append(row)

        queries = get_create_query(header, data, "Unidade")

        for query in queries:
            conn.query(query)


insert_unidades()
