import logging as log
from enum import Enum, auto

import numpy as np
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


class Neo4jDataType(Enum):
    STRING = auto()
    NUMBER = auto()
    DATE = auto()


class CypherCreateQueryBuilder:
    def __init__(self, label: str or [str]):
        if isinstance(label, list):
            self.__label = ":".join(label)
        else:
            self.__label = label

        self.__attributes = []
        self.__BASE_STMT = f"CREATE (n:{self.__label}) SET "

    def add_atribute(self, key, value, vtype=Neo4jDataType.STRING):
        if value is None:
            return self
        elif value is np.nan:
            return self

        if vtype is Neo4jDataType.STRING:
            value = f'"{value}"'
        elif vtype is Neo4jDataType.DATE:
            value = f'date("{value}")'

        self.__attributes.append(f"n.{key} = {value}")

        return self

    def build(self) -> str:
        statement = ""

        if len(self.__attributes) == 1:
            statement = self.__BASE_STMT + self.__attributes[0]
        elif len(self.__attributes) > 1:
            statement = self.__BASE_STMT + ", ".join(self.__attributes)

        self.reset()

        return statement

    def reset(self):
        self.__attributes = []


def create_relationship_query(
    a_label, a_attr, a_value, b_label, b_attr, b_value, reltype
):
    return f'MATCH (a:{a_label}), (b:{b_label}) WHERE a.{a_attr} = "{a_value}" AND b.{b_attr} = "{b_value}" CREATE (a)-[r:{reltype}]->(b)'
