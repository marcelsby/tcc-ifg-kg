import unittest

from database import CypherCreateQueryBuilder

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


if __name__ == "__main__":
    unittest.main()
