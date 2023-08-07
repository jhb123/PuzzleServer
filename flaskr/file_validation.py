def check_clue_boxes(clue_boxes: dict[str, dict]):
    valid_keys = {"first", "second", "third"}
    for clue_box in clue_boxes:
        if set(clue_box.keys()) != valid_keys:
            raise KeyError("Invalid clue box structure")


def check_clue_dict(clues: dict[str, dict]):
    valid_keys = {"clue", "clueBoxes", "clueName"}
    for clue_name in clues:
        if set(clues[clue_name].keys()) != valid_keys:
            raise KeyError("Invalid clue structure")
        check_clue_boxes(clues[clue_name]["clueBoxes"])


def check_private_clues(input_json: dict):
    if "_clues" not in input_json.keys():
        raise KeyError("_clues not in json")
    check_clue_dict(input_json["_clues"])


def check_public_clues(input_json: dict):
    if "clues" not in input_json.keys():
        raise KeyError("clues not in json")
    check_clue_dict(input_json["clues"])


def check_grid_size(input_json: dict):
    if "gridSize" not in input_json.keys():
        raise KeyError("gridSize not in json")


def check_puzzle_json(input_json: dict) -> bool:
    check_grid_size(input_json)
    check_public_clues(input_json)
    check_private_clues(input_json)
    return True


def get_file_extension(file_name: str):
    file_name_split = file_name.split(".")
    if (
        len(file_name_split) != 2
        or file_name_split[0] == ""
        or file_name_split[1] == ""
    ):
        raise ValueError("Not a file")
    if file_name_split[1].strip() != file_name_split[1]:
        raise ValueError("file extension has white space")
    return file_name_split[1]
