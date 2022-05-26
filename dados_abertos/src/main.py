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
        "cursos",
    ),
    ("nome;matricula;curso;campus", "docentes"),
    (
        "nome;sigla;endereco;site;telefone;email;cnpj;uasg;autoridade_maxima_unidade",
        "unidades",
    ),
    (
        "campus;ano_ingresso;periodo_letivo_ingresso;curso;modalidade;formato;sexo;nivel;renda_per_capita;etnia;ano_nascimento;situacao",
        "discentes",
    ),
    (
        "cod_pauta;campus_ofertante;ano_letivo;periodo;turma;curso;modalidade;nivel;departamento;nome;ch;tipo;nome_docente;siape_docente;nome_auxiliar;siape_auxiliar",
        "disciplinas_ministradas",
    ),
    (
        "campus;curso;modalidade;nivel;data1;data2;data3;ofertante;status;tipo;remunerado;valor_remuneracao",
        "estagios_curriculares",
    ),
    ("nome;matricula;cargo;data_de_ingresso;atribuicao;carga_horaria", "servidores"),
]


for param_list in tqdm(barramento_ifg_params):
    barramento_ifg_json_to_csv(param_list[0], param_list[1], raw_path, transformed_path)


# TODO: transformar o json de editais de iniciação científica em csv
