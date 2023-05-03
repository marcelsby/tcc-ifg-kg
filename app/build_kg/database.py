import logging as log
from enum import Enum, auto
from typing import Any

from neo4j import GraphDatabase
from pandas import isna

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
    INTEGER = auto()


class CypherQueryFilterType(str, Enum):
    EQUAL = "="


class CypherQueryFilter:
    def __init__(self, property_name: str, filter_type: CypherQueryFilterType, value: Any, value_type: Neo4jDataType = Neo4jDataType.STRING, alias: str = "a"):
        self._property = property_name
        self._value = _cast_property_value(value, value_type)
        self._filter_type = filter_type
        self._alias = alias

    def get(self) -> str:
        return f"{self._alias}.{self._property} {self._filter_type.value} {self._value}"

    @property
    def alias(self):
        return self._alias

    @alias.setter
    def alias(self, new_alias: str):
        self._alias = new_alias


class CypherQueryFiltersBuilder:
    def __init__(self):
        self._filters: list[CypherQueryFilter] = []

    def add_filter(self, query_filter: CypherQueryFilter):
        self._filters.append(query_filter)
        return self

    def add_filters(self, query_filters: list[CypherQueryFilter]):
        for query_filter in query_filters:
            self.add_filter(query_filter)

        return self

    def build(self, combination_operator="AND") -> str:
        if combination_operator not in {"AND", "OR"}:
            raise ValueError("Invalid operator, must be 'AND' or 'OR'")

        filters = []

        for query_filter in self._filters:
            filters.append(query_filter.get())

        return f" {combination_operator} ".join(filters)

    def reset(self):
        self._filters = []


def _cast_property_value(value, value_type: Neo4jDataType) -> str:
    if value_type is Neo4jDataType.STRING:
        return f'"{value}"'

    if value_type is Neo4jDataType.DATE:
        return f'date("{value}")'

    if value_type is Neo4jDataType.INTEGER:
        return f'{int(value)}'


class CypherCreateQueryBuilder:
    def __init__(self, label: str | list[str]):
        if isinstance(label, list):
            self._label = ":".join(label)
        else:
            self._label = label

        self._properties = []
        self._BASE_STMT = f"CREATE (n:{self._label}) SET "

    def add_property(self, key, value, value_type=Neo4jDataType.STRING):
        is_py_false_value = not bool(value)

        if is_py_false_value or isna(value):
            return self

        value = _cast_property_value(value, value_type)

        self._properties.append(f"n.{key} = {value}")

        return self

    def build(self) -> str:
        statement = ""

        if len(self._properties) == 1:
            statement = self._BASE_STMT + self._properties[0]
        elif len(self._properties) > 1:
            statement = self._BASE_STMT + ", ".join(self._properties)

        self.reset()

        return statement

    def reset(self):
        self._properties = []


def make_simple_relationship_query(a_label, a_filter: CypherQueryFilter, b_label, b_filter: CypherQueryFilter, reltype):
    a_filter.alias = "a"
    b_filter.alias = "b"

    filter_builder = CypherQueryFiltersBuilder()

    filter_builder.add_filters([a_filter, b_filter])

    return f'MATCH (a:{a_label}), (b:{b_label}) WHERE {filter_builder.build()} CREATE (a)-[r:{reltype}]->(b)'


def make_relationship_query(a_label, a_filters: list[CypherQueryFilter], b_label, b_filters: list[CypherQueryFilter], reltype):
    for query_filter in a_filters:
        query_filter.alias = "a"

    for query_filter in b_filters:
        query_filter.alias = "b"

    filter_builder = CypherQueryFiltersBuilder()

    for query_filter in a_filters + b_filters:
        filter_builder.add_filter(query_filter)

    return f'MATCH (a:{a_label}), (b:{b_label}) WHERE {filter_builder.build()} CREATE (a)-[r:{reltype}]->(b)'
