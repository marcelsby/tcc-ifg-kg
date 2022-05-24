from pathlib import Path
from preprocess import json_to_csv

transformed_path = Path("../data/transformed/")
raw_path = Path("../data/raw/")

if not transformed_path.is_dir():
    Path(transformed_path).mkdir()

json_to_csv(
    "campus;nome;codigo;modalidade;formato;turno;periodo_de_ingresso;qtd_vagas_ano;nivel;ch_disciplinas;ch_complementar;ch_estagio;ch_optativas;ch_projeto_final;ch_total;qtd_semestres\n",
    raw_path / "cursos.json",
    transformed_path / "cursos.csv",
)

json_to_csv(
    "nome;matricula;curso;campus\n",
    raw_path / "docentes.json",
    transformed_path / "docentes.csv",
)

json_to_csv(
    "nome;sigla;endereco;site;telefone;email;cnpj;uasg;autoridade_maxima_unidade\n",
    raw_path / "unidades.json",
    transformed_path / "unidades.csv",
)

