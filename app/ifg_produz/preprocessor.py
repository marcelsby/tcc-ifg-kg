from pathlib import Path

from app.utils.notebook_runner import get_notebooks_to_run, run_notebooks
from app.utils.storage import Storage


def preprocess():
    notebooks_dir = Path("./notebooks/ifg_produz")
    correct_execution_order_file = Storage.get_file("ifg_produz/notebooks_execution_order.json")

    notebooks_to_run = get_notebooks_to_run(notebooks_dir, correct_execution_order_file)
    params = {"p_notebooks_root": str(Path("./notebooks/ifg_produz").absolute())}

    run_notebooks(notebooks_to_run, params)


if __name__ == '__main__':
    preprocess()
