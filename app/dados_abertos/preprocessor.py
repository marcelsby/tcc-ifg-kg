from pathlib import Path

from app.utils.notebook_runner import get_notebooks_to_run, run_notebooks
from app.utils.storage import Storage


def preprocess():
    notebooks_dir = Path("./notebooks/dados_abertos")
    correct_execution_order_file = Storage.get_file("dados_abertos/notebooks_execution_order.json")

    notebooks_to_run = get_notebooks_to_run(notebooks_dir, correct_execution_order_file)

    run_notebooks(notebooks_to_run)


if __name__ == '__main__':
    preprocess()
