from pathlib import Path

import pandas as pd

from database import Neo4jConnection, CypherCreateQueryBuilder

conn = Neo4jConnection("bolt://localhost:7687", "neo4j", "test")


def insert_unidades():
    unidades_csv = Path("../dados_abertos/data/preprocessed/unidades.csv")
    unidades_df = pd.read_csv(unidades_csv, delimiter=";")

    query_builder = CypherCreateQueryBuilder("Unidade")

    for index, row in unidades_df.iterrows():
        builded_query = (
            query_builder.add_atribute("nome", row["nome"])
            .add_atribute("sigla", row["sigla"])
            .add_atribute("logradouro", row["logradouro"])
            .add_atribute("numero", row["numero"])
            .add_atribute("bairro", row["bairro"])
            .add_atribute("cep", row["cep"])
            .add_atribute("cidade", row["cidade"])
            .add_atribute("site", row["site"])
            .add_atribute("telefone", row["telefone"])
            .add_atribute("email", row["email"])
            .add_atribute("cnpj", row["cnpj"])
            .add_atribute("uasg", row["uasg"])
            .build()
        )

        conn.query(builded_query)


insert_unidades()
