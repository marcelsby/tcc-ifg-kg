from app.build_kg.database import make_neo4j_bolt_connection
from app.build_kg.ifg_produz import (insert_areas_de_atuacao,
                                     insert_atuacao_profissional, insert_banca,
                                     insert_cidades, insert_curriculos,
                                     insert_formacao_academica,
                                     insert_orientacao,
                                     insert_outras_producoes,
                                     insert_palavras_chaves,
                                     insert_participacao_evento,
                                     insert_producao_tecnica,
                                     insert_projeto_pesquisa, insert_registro,
                                     insert_textos_jornais,
                                     insert_unidades_federativas)
from app.utils.environment import Environment
from app.utils.storage import Storage


def insert():
    conn = make_neo4j_bolt_connection(Environment.neo4j_user, Environment.neo4j_password,
                                      Environment.neo4j_host, Environment.neo4j_port)

    insert_unidades_federativas.execute(
        conn,
        Storage.get_file("ifg_produz/preprocessed/unidades_federativas.csv")
    )

    insert_cidades.execute(
        conn,
        Storage.get_file("ifg_produz/preprocessed/cidades.csv")
    )

    insert_palavras_chaves.execute(
        conn,
        Storage.get_file("ifg_produz/preprocessed/palavras_chaves.csv")
    )

    insert_curriculos.execute(
        conn,
        Storage.get_file("ifg_produz/preprocessed/curriculos.csv")
    )

    insert_textos_jornais.execute(
        conn,
        Storage.get_file("ifg_produz/preprocessed/textos_jornais.csv")
    )

    insert_banca.execute(
        conn,
        Storage.get_file("ifg_produz/preprocessed/banca.csv")
    )

    insert_registro.execute(
        conn,
        Storage.get_file("ifg_produz/preprocessed/registro.csv")
    )

    insert_participacao_evento.execute(
        conn,
        Storage.get_file("ifg_produz/preprocessed/participacao_evento.csv")
    )

    insert_projeto_pesquisa.execute(
        conn,
        Storage.get_file("ifg_produz/preprocessed/projetos_pesquisa.csv")
    )

    insert_orientacao.execute(
        conn,
        Storage.get_file("ifg_produz/preprocessed/orientacao.csv")
    )

    insert_atuacao_profissional.execute(
        conn,
        Storage.get_file("ifg_produz/preprocessed/atuacao_profissional.csv"),
        Storage.get_file("ifg_produz/preprocessed/atividades_atuacao_profissional.csv")
    )

    insert_producao_tecnica.execute(
        conn,
        Storage.get_file("ifg_produz/preprocessed/producao_tecnica.csv")
    )

    insert_outras_producoes.execute(
        conn,
        Storage.get_file("ifg_produz/preprocessed/outras_producoes.csv")
    )

    insert_areas_de_atuacao.execute(
        conn,
        Storage.get_file("ifg_produz/preprocessed/areas_de_atuacao.csv")
    )

    insert_formacao_academica.execute(
        conn,
        Storage.get_file("ifg_produz/preprocessed/formacao_academica.csv")
    )


if __name__ == '__main__':
    insert()
