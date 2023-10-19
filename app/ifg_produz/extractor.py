import pandas as pd

from app.ifg_produz.db_connection import get_ifg_produz_db_connection_url
from app.utils.storage import Storage


def extract():
    extracted_path = Storage.get_dir("ifg_produz/extracted", create_if_not_exists=True)

    """
    SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' AND table_name not like 'dj%'
                                                   AND table_name not like 'auth%' and table_name not like 'celery%'
                                                 AND table_name not like 'hora_atualizacao'
    ORDER BY table_name
    """
    table_names = ['alunos', 'areas_de_atuacao', 'atividades', 'atuacao_profissional', 'banca', 'conferencia',
                   'curriculo', 'curriculo_grupos', 'formacaoacademica', 'grupos_de_pesquisa', 'linhas_de_pesquisa',
                   'notas_recomendacoes', 'orientacao', 'outras_producoes', 'participacao_evento',
                   'producaobibliografica', 'producaotecnica', 'projetos_pesquisa', 'registro', 'revista',
                   'textosjornais']

    for table_name in table_names:
        df = pd.read_sql_table(
            table_name,
            get_ifg_produz_db_connection_url(),
            schema="public",
        )

        df.to_csv(extracted_path / f"{table_name}.csv", sep=";", index=False)


if __name__ == '__main__':
    extract()
