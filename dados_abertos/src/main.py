from pathlib import Path

from tqdm import tqdm

from preprocess import barramento_ifg_json_to_csv

transformed_path = Path("../data/transformed/")
raw_path = Path("../data/raw/")

if not transformed_path.is_dir():
    Path(transformed_path).mkdir()

barramento_ifg_params = [
    (
        "campus;nome;codigo;modalidade;formato;turno;periodo_de_ingresso;qtd_vagas_ano;nivel;ch_disciplinas;ch_complementar;ch_estagio;ch_optativas;ch_projeto_final;ch_total;qtd_semestres",
        "cursos.json",
        "cursos.csv",
    ),
    ("nome;matricula;curso;campus", "docentes.json", "docentes.csv"),
    (
        "nome;sigla;endereco;site;telefone;email;cnpj;uasg;autoridade_maxima_unidade",
        "unidades.json",
        "unidades.csv",
    ),
    (
        "campus;ano_ingresso;periodo_letivo_ingresso;curso;modalidade;formato;sexo;nivel;renda_per_capita;etnia;ano_nascimento;situacao",
        "discentes.json",
        "discentes.csv",
    ),
    (
        "cod_pauta;campus_ofertante;ano_letivo;periodo;turma;curso;modalidade;nivel;departamento;nome;ch;tipo;nome_docente;siape_docente;nome_auxiliar;siape_auxiliar",
        "disciplinas_ministradas.json",
        "disciplinas_ministradas.csv",
    ),
    (
        "campus;curso;modalidade;nivel;data1;data2;data3;ofertante;status;tipo;remunerado;valor_remuneracao",
        "estagios_curriculares.json",
        "estagios_curriculares.csv",
    ),
    (
        "nome;matricula;cargo;data_de_ingresso;atribuicao;carga_horaria",
        "servidores.json",
        "servidores.csv",
    ),
]


for param_list in tqdm(barramento_ifg_params):
    barramento_ifg_json_to_csv(
        param_list[0], raw_path / param_list[1], transformed_path / param_list[2]
    )


# TODO: transformar o json de editais de iniciação científica em csv
