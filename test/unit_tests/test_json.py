import json
from pathlib import Path

import pytest

from flaskr.file_validation import check_puzzle_json


@pytest.fixture
def test_data_dir():
    test_dir = Path(__file__).parent.parent
    test_data_directory = test_dir.joinpath("test_data")
    yield test_data_directory


@pytest.mark.parametrize("test_input", ["test.json", "valid.json"])
def test_valid_json(test_data_dir, test_input):
    with open(test_data_dir.joinpath(test_input), "rb") as local_file:
        json_input = json.load(local_file)
    check_puzzle_json(json_input)


@pytest.mark.parametrize(
    "test_input",
    [
        "invalid_clue_boxes.json",
        "invalid_clue_data.json",
        "missing_clues_1.json",
        "missing_clues_2.json",
        "missing_grid_size.json",
    ],
)
def test_invalid_json(test_data_dir, test_input):
    with open(test_data_dir.joinpath(test_input), "rb") as local_file:
        json_input = json.load(local_file)
    with pytest.raises(KeyError):
        check_puzzle_json(json_input)
