import json

from alive_progress import alive_bar

from app.utils.downloader import FileToDownload, download
from app.utils.storage import Storage


def _get_files_to_collect() -> list[FileToDownload]:
    collect_metadata_file = Storage.get_file("dados_abertos/collect_metadata.json")

    with open(collect_metadata_file, "r") as f:
        collect_metadata_json = json.load(f)

    collect_metadata = []

    for file_to_collect in collect_metadata_json["files_to_collect"]:
        collect_metadata.append(
            FileToDownload(file_to_collect["url"],
                           file_to_collect["name_to_save"])
        )

    return collect_metadata


def collect():
    destination_path = Storage.get_dir("dados_abertos/raw", need_create=True)
    files_to_collect: list[FileToDownload] = _get_files_to_collect()

    with alive_bar(len(files_to_collect), title="Collecting files") as bar:
        for file in files_to_collect:
            download(file.url, file.name_to_save, destination_path)
            bar()
