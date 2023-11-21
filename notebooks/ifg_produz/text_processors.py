import pandas as pd


def normalizar_string(s):
    if pd.notna(s):
        import re
        import unicodedata

        # Transforma todos os caracteres em minúsculas
        s = s.lower()

        # Remove acentos das letras
        s = unicodedata.normalize("NFD", s).encode("ascii", "ignore").decode("utf-8")

        # Substitui todos os caracteres que não são letras por um espaço em branco
        s = re.sub(r'[^A-Za-z]', ' ', s)

        # Substitui espaços consecutivos por apenas um espaço
        s = re.sub(r'\s{2,}', ' ', s)

        # Remove os espaços em branco do começo e fim
        s = s.strip()

    return s


def remover_stopwords(s):
    if pd.notna(s):
        from nltk.corpus import stopwords
        from nltk.tokenize import word_tokenize

        s_tokenizada = word_tokenize(s, "portuguese")
        s = " ".join([word for word in s_tokenizada if word not in stopwords.words("portuguese")])

    return s
