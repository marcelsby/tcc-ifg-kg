import json
from pathlib import Path


def run_notebook(notebook_to_run: Path, parameters: dict = None) -> None:
    """
    Executa o notebook passado como parâmetro.

    :param notebook_to_run: Notebook que será executado.

    :param parameters: Parâmetros que serão repassados para o notebook. Não é possível enviar o parâmetro
    "p_storage_dir", pois ele já é definido internamente.
    """
    import papermill as pm

    from app.utils.storage import Storage

    if parameters is None:
        parameters = {}

    final_parameters = {**parameters, "p_storage_dir": str(Storage.root)}

    print(f"Running notebook: {notebook_to_run.name}")
    pm.execute_notebook(
        notebook_to_run,
        None,
        parameters=final_parameters
    )


def run_notebooks(notebooks_to_run: list[Path], parameters: dict = None) -> None:
    """
    Executa os notebooks que foram passados como parâmetro de maneira sequencial, respeitando a ordem da lista.

    :param notebooks_to_run: Notebooks que serão executados.

    :param parameters: Parâmetros que serão repassados para o notebook. Não é possível enviar o parâmetro
    "p_storage_dir", pois ele já é definido internamente.
    """
    for notebook_to_run in notebooks_to_run:
        run_notebook(notebook_to_run, parameters)


def get_notebooks_to_run(notebooks_dir: Path, correct_execution_order_file: Path = None) -> list[Path]:
    """
    Lê o diretório passado no parâmetro e retorna todos os notebooks que encontrar. Caso o parâmetro
    `correct_execution_order_file` seja definido os notebooks são retornados de acordo com a ordem definida no arquivo;
    esse arquivo precisa ser um JSON onde o nome de cada notebook deve estar definido sem a extensão ".ipynb" como uma
    string em um array na raiz do JSON. Como a seguir:

    [
        'notebook1',
        'notebook2',
        'notebook3',
        'notebook4'
    ]

    :param notebooks_dir: O diretório onde se encontram os notebooks.

    :param correct_execution_order_file: Arquivo JSON que define a ordem correta para os notebooks serem executados.
    Caso os notebooks não necessitem da execução em uma ordem específica pode ser omitido.

    :return: Uma lista com os notebooks para serem executados.
    """
    found_notebooks: list[Path] = []

    for path in notebooks_dir.iterdir():
        if path.is_file() and path.name.endswith(".ipynb"):
            found_notebooks.append(path)

    notebooks_to_run = []

    if correct_execution_order_file is not None:
        with open(correct_execution_order_file) as file:
            correct_execution_order = json.load(file)

            for notebook_title in correct_execution_order:
                notebook_path = notebooks_dir / (notebook_title + ".ipynb")

                if notebook_path in found_notebooks:
                    notebooks_to_run.append(notebook_path)
    else:
        notebooks_to_run = found_notebooks

    return notebooks_to_run
