from .collector import collect
from .converters import convert
from .preprocessor import preprocess


def execute():
    collect()
    convert()
    preprocess()


if __name__ == '__main__':
    execute()
