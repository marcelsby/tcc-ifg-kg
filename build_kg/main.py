from pathlib import Path
import logging as log

import pandas as pd
from neo4j.exceptions import ServiceUnavailable

from database import (
    Neo4jConnection,
    CypherCreateQueryBuilder,
    Neo4jDataType,
    create_relationship_query,
)

conn = Neo4jConnection("bolt://localhost:7687", "neo4j", "test")
preprocessed_path = Path("../dados_abertos/data/preprocessed")


def insert_unidades():
    unidades_csv = preprocessed_path / "unidades.csv"
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
        try:
            conn.query(builded_query)
            log.info(f'SUCESSO ao inserir unidade: {row["sigla"]}')
        except ServiceUnavailable as e:
            log.error(
                f'ERRO ao inserir unidade: {row["sigla"]}. Mensagem de erro: {str(e)}'
            )


def insert_docentes():
    docentes_csv = preprocessed_path / "docentes.csv"
    docentes_df = pd.read_csv(docentes_csv, delimiter=";")

    create_query_builder = CypherCreateQueryBuilder(["Docente", "Servidor"])

    for index, row in docentes_df.iterrows():
        create_query = (
            create_query_builder.add_atribute("nome", row["nome"])
            .add_atribute("matricula", row["matricula"])
            .add_atribute("disciplina_ministrada", row["disciplina_ministrada"])
            .add_atribute(
                "data_ingresso", row["data_ingresso"], vtype=Neo4jDataType.DATE
            )
            .add_atribute("atribuicao", row["atribuicao"])
            .add_atribute("carga_horaria", row["carga_horaria"])
            .build()
        )

        relationship_query = create_relationship_query(
            "Docente",
            "matricula",
            row["matricula"],
            "Unidade",
            "nome",
            row["campus"],
            "PART_OF",
        )

        try:
            conn.query(create_query)
            conn.query(relationship_query)
            log.info(
                f'SUCESSO ao inserir docente e o seu relacionamento com uma unidade: {row["matricula"]}'
            )
        except ServiceUnavailable as e:
            log.error(
                f"ERRO ao inserir docente e o seu relacionamento com uma unidade. Mensagem de erro: {str(e)}"
            )


insert_unidades()
insert_docentes()
