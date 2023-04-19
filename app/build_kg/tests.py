import unittest

from app.build_kg.database import (CypherCreateQueryBuilder,
                                   make_relationship_query)

builder = CypherCreateQueryBuilder("Teste")


class TestDatabaseModule(unittest.TestCase):
    def test_single_attribute_cyhper_create_query(self):
        query = builder.add_atribute("atributo", "valor").build()
        self.assertEqual(query, 'CREATE (n:Teste) SET n.atributo = "valor"')

    def test_multiple_attributes_cypher_create_query(self):
        query = (
            builder.add_atribute("atributo", "valor")
            .add_atribute("testando", "123")
            .build()
        )
        self.assertEqual(
            query, 'CREATE (n:Teste) SET n.atributo = "valor", n.testando = "123"'
        )

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
        self.assertEqual(
            query,
            'MATCH (a:Docente), (b:Unidade) WHERE a.matricula = "123456" AND b.nome = "CÂMPUS ÁGUAS LINDAS" CREATE (a)-[r:part_of]->(b)',
        )


if __name__ == "__main__":
    unittest.main()
