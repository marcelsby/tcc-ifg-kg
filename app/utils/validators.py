import json
from pathlib import Path


def validate_json_file(file_to_validate: Path):
    with open(file_to_validate) as f:
        json.load(f)
