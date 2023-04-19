from enum import Enum
from pathlib import Path


class FileExtension(str, Enum):
    JSON = "json"


class Storage:
    """
    Classe que age como uma interface para acessar o sistema de arquivos
    sem precisar se preocupar com caminhos relativos, etc...
    """

    _STORAGE_DIR = Path("./storage/")

    @classmethod
    def get_file(cls, file_path: str) -> Path | FileNotFoundError:
        requested_file = cls._get_path_from_storage(file_path)

        if not requested_file.is_file():
            raise FileNotFoundError("The specified file is not a file or does not exist.")

        return requested_file

    @classmethod
    def get_dir(cls, directory_path: str, need_create: bool = False) -> Path | NotADirectoryError:
        requested_directory = cls._get_path_from_storage(directory_path)

        if need_create:
            cls.mkdir(requested_directory)

        if not need_create and not requested_directory.is_dir():
            raise NotADirectoryError("The specified directory is not a directory or does not exist.")

        return requested_directory

    @classmethod
    def get_root(cls) -> Path:
        return cls.get_dir(".")

    @classmethod
    def mkdir(cls, directory_to_be_created: Path):
        directory_to_be_created.mkdir(parents=True, exist_ok=True)

    @classmethod
    def _get_path_from_storage(cls, file_or_dir) -> Path:
        return cls._STORAGE_DIR / file_or_dir