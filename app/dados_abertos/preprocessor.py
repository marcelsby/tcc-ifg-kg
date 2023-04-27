from pathlib import Path

import papermill as pm

from app.utils.storage import Storage


def preprocess():
    da_notebooks_dir = Path("./notebooks/dados_abertos")

    notebooks_to_run: list[Path] = []

    for path in da_notebooks_dir.iterdir():
        if path.is_file() and path.name.endswith(".ipynb"):
            notebooks_to_run.append(path)

    parameters = {"p_storage_dir": str(Storage.root)}

    for notebook_to_run in notebooks_to_run:
        print(f"Running notebook: {notebook_to_run.name}")
        pm.execute_notebook(
            notebook_to_run,
            None,
            parameters=parameters
        )
