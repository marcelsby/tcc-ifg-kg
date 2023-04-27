def clean_collected() -> None:
    """
    Limpa os arquivos coletados do Portal de Dados Abertos, corrigindo inconsistências que
    impedem o sucesso do processo de conversão dos arquivos coletados.
    """
    from .barramento_ifg import clean as clean_barramento_ifg

    clean_barramento_ifg()
