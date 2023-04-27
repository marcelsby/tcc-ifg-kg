from .collected_cleaners import clean_collected
from .collector import collect
from .converters import convert
from .preprocessor import preprocess


def execute():
    collect()
    clean_collected()
    convert()
    preprocess()


if __name__ == '__main__':
    execute()
