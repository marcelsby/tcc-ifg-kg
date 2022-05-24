from utils.downloader import download
from pathlib import Path

base_url = "https://barramento.ifg.edu.br/ifg_barramento_ws/ws/"
dest_path = Path("../data/raw")

# Metadados dos arquivos que precisam de conversão de JSON -> CSV
download_metadata = [
    (base_url + "102", "servidores.json"),
    (base_url + "204", "cursos.json"),
    (base_url + "205", "disciplinas_ministradas.json"),
    (base_url + "207", "estagios_curriculares.json"),
    (base_url + "252", "discentes.json"),
    (base_url + "402", "docentes.json"),
    (base_url + "502", "unidades.json"),
    (base_url + "557", "editais_iniciacao_cientifica.json"),
]

for file in download_metadata:
    download(file[0], file[1], dest_path)
