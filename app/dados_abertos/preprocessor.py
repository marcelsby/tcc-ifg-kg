import json
from pathlib import Path

import papermill as pm

from app.utils.storage import Storage


def preprocess():
    notebooks_dir = Path("./notebooks/dados_abertos")

    notebooks_to_run = _get_notebooks_to_run(notebooks_dir)

    parameters = {"p_storage_dir": str(Storage.root)}

    for notebook_to_run in notebooks_to_run:
        print(f"Running notebook: {notebook_to_run.name}")
        pm.execute_notebook(
            notebook_to_run,
            None,
            parameters=parameters
        )


def _get_notebooks_to_run(notebooks_dir: Path) -> list[Path]:
    found_notebooks: list[Path] = []

    for path in notebooks_dir.iterdir():
        if path.is_file() and path.name.endswith(".ipynb"):
            found_notebooks.append(path)

    notebooks_to_run = []

    with open(Storage.get_file("dados_abertos/notebooks_execution_order.json")) as correct_execution_order_file:
        correct_execution_order = json.load(correct_execution_order_file)

        for notebook_title in correct_execution_order:
            notebook_path = notebooks_dir / (notebook_title + ".ipynb")

            if notebook_path in found_notebooks:
                notebooks_to_run.append(notebook_path)

    return notebooks_to_run


if __name__ == '__main__':
    preprocess()
