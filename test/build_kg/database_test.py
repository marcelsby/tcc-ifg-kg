from dataclasses import dataclass

import pytest

from app.build_kg.database import (CypherCreateQueryBuilder, Neo4jConnection,
                                   make_neo4j_bolt_connection,
                                   make_relationship_query)


@dataclass
class DBCredentials:
    user = "neo4j"
    password = "123@qwe"
    host = "0.0.0.0"
    port = 1234


class TestDatabase:

    @pytest.fixture
    def db_credentials(self) -> DBCredentials:
        return DBCredentials()

    @pytest.fixture
    def builder(self):
        return CypherCreateQueryBuilder("Test")

    def test_single_attribute_cyhper_create_query(self, builder):
        query = builder.add_atribute("atributo", "valor").build()
        assert query == 'CREATE (n:Test) SET n.atributo = "valor"'

    def test_multiple_attributes_cypher_create_query(self, builder):
        query = (
            builder.add_atribute("atributo", "valor")
            .add_atribute("testando", "123")
            .build()
        )

        assert query == 'CREATE (n:Test) SET n.atributo = "valor", n.testando = "123"'

    def test_create_relationship_query(self):
        query = make_relationship_query(
            "Docente",
            "matricula",
            "123456",
            "Unidade",
            "nome",
            "CÂMPUS ÁGUAS LINDAS",
            "part_of",
        )

        assert query == 'MATCH (a:Docente), (b:Unidade) WHERE a.matricula = "123456" AND b.nome = "CÂMPUS ÁGUAS LINDAS" CREATE (a)-[r:part_of]->(b)'

    def test_make_neo4j_bolt_connection_with_default_parameters(self, mocker, db_credentials):
        # Given
        neo4j_connection_mock = mocker.MagicMock(return_value=None)
        mocker.patch.object(Neo4jConnection, "__init__", new=neo4j_connection_mock)

        # When
        make_neo4j_bolt_connection(db_credentials.user, db_credentials.password)

        # Then
        expected_uri = "bolt://localhost:7687"
        neo4j_connection_mock.assert_called_once_with(expected_uri, db_credentials.user, db_credentials.password)

    def test_make_neo4j_bolt_connection_providing_all_parameters(self, mocker, db_credentials):
        # Given
        neo4j_connection_mock = mocker.MagicMock(return_value=None)
        mocker.patch.object(Neo4jConnection, "__init__", new=neo4j_connection_mock)

        # When
        make_neo4j_bolt_connection(db_credentials.user, db_credentials.password,
                                   db_credentials.host, db_credentials.port)

        # Then
        expected_uri = "bolt://0.0.0.0:1234"
        neo4j_connection_mock.assert_called_once_with(
            expected_uri, db_credentials.user, db_credentials.password)
