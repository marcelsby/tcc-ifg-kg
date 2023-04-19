import warnings
from dataclasses import dataclass
from pathlib import Path

import requests

warnings.simplefilter("ignore")


@dataclass
class FileToDownload:
    url: str
    name_to_save: str


def download(url: str, dest_file: str, dest_path: Path):
    try:
        data_downloaded = requests.get(url, verify=False)

        with open(dest_path / dest_file, "wb") as file:
            file.write(data_downloaded.content)
    except Exception as e:
        print(e)
