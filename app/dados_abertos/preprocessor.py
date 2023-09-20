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
    notebooks_to_run = []

    for path in notebooks_dir.iterdir():
        if path.is_file() and path.name.endswith(".ipynb"):
            notebooks_to_run.append(path)

    # Resolvendo dependências de maneira manual, pois são poucas.
    notebook_disciplinas_ministradas_index = notebooks_to_run.index(
        notebooks_dir / "Preprocessing Disciplinas Ministradas.ipynb"
    )

    notebook_cursos_index = notebooks_to_run.index(
        notebooks_dir / "Preprocessing Cursos.ipynb"
    )

    if notebook_cursos_index > notebook_disciplinas_ministradas_index:
        notebooks_to_run.insert(notebook_cursos_index + 1, notebooks_to_run.pop(notebook_disciplinas_ministradas_index))

    return notebooks_to_run
