from app.build_kg.database import Neo4jConnection, make_neo4j_bolt_connection
from app.build_kg.ifg_produz import (insert_areas_de_atuacao,
                                     insert_atuacao_profissional, insert_banca,
                                     insert_cidades, insert_curriculos,
                                     insert_formacao_academica,
                                     insert_grupos_pesquisa, insert_orientacao,
                                     insert_outras_producoes,
                                     insert_palavras_chaves,
                                     insert_participacao_evento,
                                     insert_producao_bibliografica,
                                     insert_producao_tecnica,
                                     insert_projeto_pesquisa, insert_registro,
                                     insert_textos_jornais,
                                     insert_unidades_federativas)
from app.utils.environment import Environment
from app.utils.storage import StorageWithBasePath


def insert(connection: Neo4jConnection):
    storage = StorageWithBasePath("ifg_produz/preprocessed/")

    insert_unidades_federativas.execute(
        connection,
        storage.get_file("unidades_federativas.csv")
    )

    insert_cidades.execute(
        connection,
        storage.get_file("cidades.csv")
    )

    insert_palavras_chaves.execute(
        connection,
        storage.get_file("palavras_chaves.csv")
    )

    insert_curriculos.execute(
        connection,
        storage.get_file("curriculos.csv")
    )

    insert_textos_jornais.execute(
        connection,
        storage.get_file("textos_jornais.csv")
    )

    insert_banca.execute(
        connection,
        storage.get_file("banca.csv")
    )

    insert_registro.execute(
        connection,
        storage.get_file("registro.csv")
    )

    insert_participacao_evento.execute(
        connection,
        storage.get_file("participacao_evento.csv")
    )

    insert_projeto_pesquisa.execute(
        connection,
        storage.get_file("projetos_pesquisa.csv")
    )

    insert_orientacao.execute(
        connection,
        storage.get_file("orientacao.csv")
    )

    insert_atuacao_profissional.execute(
        connection,
        storage.get_file("atuacao_profissional.csv"),
        storage.get_file("atividades_atuacao_profissional.csv")
    )

    insert_producao_tecnica.execute(
        connection,
        storage.get_file("producao_tecnica.csv")
    )

    insert_outras_producoes.execute(
        connection,
        storage.get_file("outras_producoes.csv")
    )

    insert_areas_de_atuacao.execute(
        connection,
        storage.get_file("areas_de_atuacao.csv")
    )

    insert_formacao_academica.execute(
        connection,
        storage.get_file("formacao_academica.csv")
    )

    insert_producao_bibliografica.execute(
        connection,
        storage.get_file("producao_bibliografica.csv"),
        storage.get_file("revista.csv"),
        storage.get_file("conferencia.csv")
    )

    insert_grupos_pesquisa.execute(
        connection,
        storage.get_file("grupos_de_pesquisa.csv"),
        storage.get_file("linhas_de_pesquisa.csv"),
        storage.get_file("alunos.csv"),
        storage.get_file("curriculo_grupos.csv")
    )


if __name__ == '__main__':
    conn = make_neo4j_bolt_connection(
        Environment.neo4j_user,
        Environment.neo4j_password,
        Environment.neo4j_host,
        Environment.neo4j_port
    )

    insert(conn)
