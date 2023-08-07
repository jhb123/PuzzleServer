import pytest

from flaskr.file_validation import get_file_extension


@pytest.mark.parametrize(
    "test_input",
    [
        None,
        "file",
        "png",
        ".png",
        ".",
        "file.",
        "a.b.c",
        ".a.b",
        ".a.",
        ".a",
        "file. jpeg",
        "file.jpeg ",
    ],
)
def test_invalid_filename(test_input):
    with pytest.raises(ValueError) as excinfo:
        get_file_extension(test_input)
    assert excinfo.type == ValueError


@pytest.mark.parametrize(
    "test_input, file_ext",
    [("file.jpeg", "jpeg"), ("file.png", "png"), ("file name.png", "png")],
)
def test_valid_filename(test_input, file_ext):
    assert get_file_extension(test_input) == file_ext
