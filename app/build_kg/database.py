import logging as log
from enum import Enum, auto
from typing import Any

from neo4j import Driver, GraphDatabase

log.basicConfig(
    level=log.INFO,
    format="[%(asctime)s] [%(levelname)s]: %(message)s",
    datefmt="%d/%m/%Y %I:%M:%S",
)


class DriverNotInitialized(Exception):
    def __init__(self):
        super().__init__("The driver is not initialized, then isn't possible complete the requested operation.")


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
        if self.is_driver_initialized:
            self.driver.close()

    def query(self, query, db=None):
        self.check_driver_initialized()

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

    @property
    def is_driver_initialized(self) -> bool:
        return self.driver is not None

    def check_driver_initialized(self) -> None | DriverNotInitialized:
        if not self.is_driver_initialized:
            raise DriverNotInitialized()
        else:
            return None

    @property
    def driver(self) -> Driver:
        return self._driver


def make_neo4j_bolt_connection(user: str, password: str, host: str = "localhost", port: int = 7687):
    uri = f"bolt://{host}:{str(port)}"

    return Neo4jConnection(uri, user, password)


class Neo4jDataType(Enum):
    STRING = auto()
    NUMBER = auto()
    BOOL = auto()
    DATE = auto()
    INTEGER = auto()


class CypherJsonLikeProperty:
    def __init__(self, key: str, value: Any, value_type: Neo4jDataType):
        self._key = key
        self._value = _cast_property_value(value, value_type)

    def get(self) -> str:
        return f"{self._key}: {self._value}"


class CypherQueryFilterType(str, Enum):
    EQUAL = "="


class CypherQueryFilter:
    def __init__(self, property_name: str, filter_type: CypherQueryFilterType, value: Any,
                 value_type: Neo4jDataType = Neo4jDataType.STRING, alias: str = "a"):
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

        self.reset()

        return f" {combination_operator} ".join(filters)

    def reset(self):
        self._filters = []


class CypherPropertiesBuilder:
    def __init__(self):
        self._properties: list[CypherJsonLikeProperty] = []

    def add_properties(self, new_properties: list[CypherJsonLikeProperty]):
        self._properties += new_properties

        return self

    def build(self):
        properties = [prop.get() for prop in self._properties]
        properties = "{" + ", ".join(properties) + "}"

        self.reset()

        return properties

    def reset(self):
        self._properties = []


def _cast_property_value(value, value_type: Neo4jDataType) -> str:
    if value_type is Neo4jDataType.STRING:
        return f'"{value}"'

    if value_type is Neo4jDataType.DATE:
        return f'date("{value}")'

    if value_type is Neo4jDataType.INTEGER:
        return f'{int(value)}'

    if value_type is Neo4jDataType.BOOL:
        if not isinstance(value, bool):
            raise TypeError(
                "The provided value isn't a explicitly boolean. Please provide a value that is a 'bool' instance.")
        else:
            return "true" if value else "false"


class CypherCreateQueryBuilder:
    def __init__(self, label: str | list[str]):
        if isinstance(label, list):
            self._label = ":".join(label)
        else:
            self._label = label

        self._properties = []
        self._BASE_STMT = f"CREATE (n:{self._label}) SET "

    def add_property(self, key, value, value_type=Neo4jDataType.STRING):
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


def make_relationship_query(a_label, a_filters: list[CypherQueryFilter] | CypherQueryFilter, b_label,
                            b_filters: list[CypherQueryFilter] | CypherQueryFilter, rel_label: str,
                            rel_props: list[CypherJsonLikeProperty] = None):
    if isinstance(a_filters, CypherQueryFilter):
        a_filters = [a_filters]

    if isinstance(b_filters, CypherQueryFilter):
        b_filters = [b_filters]

    a_filters = _replace_filters_alias(a_filters, "a")
    b_filters = _replace_filters_alias(b_filters, "b")

    filters_builder = CypherQueryFiltersBuilder()

    for query_filter in a_filters + b_filters:
        filters_builder.add_filter(query_filter)

    rel_props_str = ''

    if rel_props is not None:
        rel_props_builder = CypherPropertiesBuilder()
        rel_props_builder.add_properties(rel_props)
        rel_props_str = f" {rel_props_builder.build()}"

    return f'MATCH (a:{a_label}), (b:{b_label}) WHERE {filters_builder.build()} CREATE (a)-[r:{rel_label}{rel_props_str}]->(b)'


def run_transactions_batch(conn: Neo4jConnection, transactions_batch: list[tuple]):
    conn.check_driver_initialized()

    with conn.driver.session() as session:
        with session.begin_transaction() as tx:
            for transaction in transactions_batch:
                for query in transaction:
                    tx.run(query)


def _replace_filters_alias(query_filters: list[CypherQueryFilter], alias: str) -> list[CypherQueryFilter]:
    for query_filter in query_filters:
        query_filter.alias = alias

    return query_filters
