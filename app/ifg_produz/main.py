from app.ifg_produz.extractor import extract
from app.ifg_produz.preprocessor import preprocess


def execute():
    extract()
    preprocess()


if __name__ == '__main__':
    execute()
