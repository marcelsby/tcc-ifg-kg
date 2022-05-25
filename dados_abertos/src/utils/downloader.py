from pathlib import Path
import requests
import urllib3
from urllib3.exceptions import InsecureRequestWarning


urllib3.disable_warnings(InsecureRequestWarning)


def download(url: str, dest_file: str, dest_path: Path):
    try:
        if not Path(dest_path).is_dir():
            Path(dest_path).mkdir(parents=True)

        data_downloaded = requests.get(url, verify=False)

        with open(dest_path / dest_file, "wb") as file:
            file.write(data_downloaded.content)
    except Exception as e:
        print(e)
