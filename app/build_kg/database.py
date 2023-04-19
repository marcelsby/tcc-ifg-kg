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
    def __init__(self, uri, user, password):
        self._uri = uri
        self._user = user
        self._password = password
        self._driver = None

        try:
            self._driver = GraphDatabase.driver(
                self._uri, auth=(self._user, self._password)
            )
        except Exception as e:
            log.critical(str(e))

    def close(self):
        if self._driver is not None:
            self._driver.close()

    def query(self, query, db=None):
        assert self._driver is not None, "Driver not initialized!"

        session = None
        response = None

        try:
            session = (
                self._driver.session(database=db)
                if db is not None
                else self._driver.session()
            )
            response = list(session.run(query))
        except Exception as e:
            log.error(f"Erro ao executar a consulta: {str(e)}")
        finally:
            if session is not None:
                session.close()

        return response


def make_neo4j_bolt_connection(user: str, password: str, host: str = "localhost", port: int = 7687):
    uri = f"bolt://{host}:{str(port)}"

    return Neo4jConnection(uri, user, password)


class Neo4jDataType(Enum):
    STRING = auto()
    NUMBER = auto()
    DATE = auto()


class CypherCreateQueryBuilder:
    def __init__(self, label: str or [str]):
        if isinstance(label, list):
            self._label = ":".join(label)
        else:
            self._label = label

        self._attributes = []
        self._BASE_STMT = f"CREATE (n:{self._label}) SET "

    def add_atribute(self, key, value, value_type=Neo4jDataType.STRING):
        if value is None or value is np.nan:
            return self

        value = self._cast_attribute(value, value_type)

        self._attributes.append(f"n.{key} = {value}")

        return self

    def build(self) -> str:
        statement = ""

        if len(self._attributes) == 1:
            statement = self._BASE_STMT + self._attributes[0]
        elif len(self._attributes) > 1:
            statement = self._BASE_STMT + ", ".join(self._attributes)

        self.reset()

        return statement

    def reset(self):
        self._attributes = []

    @staticmethod
    def _cast_attribute(value, value_type: Neo4jDataType) -> str:
        if value_type is Neo4jDataType.STRING:
            return f'"{value}"'

        if value_type is Neo4jDataType.DATE:
            return f'date("{value}")'


def make_relationship_query(
        a_label, a_attr, a_value, b_label, b_attr, b_value, reltype
):
    return f'MATCH (a:{a_label}), (b:{b_label}) WHERE a.{a_attr} = "{a_value}" AND b.{b_attr} = "{b_value}" CREATE (a)-[r:{reltype}]->(b)'
