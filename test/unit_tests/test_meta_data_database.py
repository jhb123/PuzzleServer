import pytest
from moto.dynamodb.models import DynamoDBBackend

from flaskr import PuzzleDatabase


class TestPuzzleDatabase:
    # @pytest.mark.parametrize("key, val", [
    #     ("id", "test"), ("username", "uname"), ("password", "pword"),
    #     ("email", "email@addr.com"), ("resetGuid", "123")
    # ])
    @pytest.mark.parametrize(
        "key, val",
        [
            ("id", "test"),
            ("puzzle", "file.json"),
            ("timeCreated", "1/1/1 1:11 UTC+1"),
            ("lastModified", "2/2/2 2:22 UTC+2"),
            ("icon", "file.png"),
        ],
    )
    def test_get_metadata_id(
        self,
        fake_crossword_db: PuzzleDatabase,
        db_backend: DynamoDBBackend,
        puzzle_test_data: dict,
        key,
        val,
    ):
        db_backend.put_item("crosswords", puzzle_test_data)
        data = fake_crossword_db.get_puzzle_meta_data("test")
        assert data[key] == val

    def test_getting_missing_metadata(self, fake_crossword_db):
        with pytest.raises(KeyError) as excinfo:
            fake_crossword_db.get_puzzle_meta_data("test")
        assert KeyError == excinfo.type

    @pytest.mark.parametrize(
        "key, val",
        [
            ("id", "test"),
            ("puzzle", "file.json"),
            ("timeCreated", "1/1/1 1:11 UTC+1"),
            ("lastModified", "2/2/2 2:22 UTC+2"),
            ("icon", "file.png"),
        ],
    )
    def test_upload_valid_meta_data(
        self, fake_crossword_db, db_backend: DynamoDBBackend, key, val
    ):
        fake_crossword_db.upload_puzzle_meta_data(
            puzzle_id="test",
            puzzle_json_fname="file.json",
            time_created="1/1/1 1:11 UTC+1",
            last_modified="2/2/2 2:22 UTC+2",
            puzzle_image_fname="file.png",
        )

        data = db_backend.get_item("crosswords", {"id": {"S": "test"}})
        # data_id: DynamoType = data.attrs["id"]
        # print(data_id.value)
        assert data.attrs[key].value == val

    @pytest.mark.parametrize("test_input", [None, 1, True, ["string"]])
    def test_upload_meta_data_bad_id(self, fake_crossword_db, test_input):
        with pytest.raises(TypeError) as excinfo:
            fake_crossword_db.upload_puzzle_meta_data(
                puzzle_id=test_input,
                puzzle_json_fname="file.json",
                time_created="1/1/1 1:11 UTC+1",
                last_modified="2/2/2 2:22 UTC+2",
                puzzle_image_fname="file.png",
            )
            assert TypeError == excinfo.type

    @pytest.mark.parametrize("test_input", [None, 1, True, "asdasd"])
    def test_get_meta_data_bad_id(self, fake_crossword_db, test_input):
        with pytest.raises(KeyError) as excinfo:
            fake_crossword_db.get_puzzle_meta_data(test_input)
            assert KeyError == excinfo.type

    @pytest.mark.parametrize("fname", ["file", "png", ".png", ".", "file."])
    def test_upload_meta_data_bad_puzzle_file(self, fake_crossword_db, fname):
        with pytest.raises(ValueError, match=r"Not a file") as excinfo:
            fake_crossword_db.upload_puzzle_meta_data(
                puzzle_id="file",
                puzzle_json_fname=fname,
                time_created="1/1/1 1:11 UTC+1",
                last_modified="2/2/2 2:22 UTC+2",
                puzzle_image_fname="file.png",
            )
            assert ValueError == excinfo.type

    @pytest.mark.parametrize("fname", ["file.png"])
    def test_upload_meta_data_wrong_puzzle_file_type(self, fake_crossword_db, fname):
        with pytest.raises(ValueError, match=r"puzzle must be a JSON file") as excinfo:
            fake_crossword_db.upload_puzzle_meta_data(
                puzzle_id="file",
                puzzle_json_fname=fname,
                time_created="1/1/1 1:11 UTC+1",
                last_modified="2/2/2 2:22 UTC+2",
                puzzle_image_fname="file.png",
            )
            assert ValueError == excinfo.type

    @pytest.mark.parametrize("fname", ["file", "png", ".png", ".", "file."])
    def test_upload_meta_data_bad_icon_file(self, fake_crossword_db, fname):
        with pytest.raises(ValueError, match=r"Not a file") as excinfo:
            fake_crossword_db.upload_puzzle_meta_data(
                puzzle_id="file",
                puzzle_json_fname="file.json",
                time_created="1/1/1 1:11 UTC+1",
                last_modified="2/2/2 2:22 UTC+2",
                puzzle_image_fname=fname,
            )
            assert ValueError == excinfo.type

    @pytest.mark.parametrize("fname", ["file.json"])
    def test_upload_meta_data_wrong_icon_file_type(self, fake_crossword_db, fname):
        with pytest.raises(
            ValueError, match=r"puzzle icon must be a PNG file"
        ) as excinfo:
            fake_crossword_db.upload_puzzle_meta_data(
                puzzle_id="file",
                puzzle_json_fname="filename.json",
                time_created="1/1/1 1:11 UTC+1",
                last_modified="2/2/2 2:22 UTC+2",
                puzzle_image_fname=fname,
            )
            assert excinfo.type == ValueError

    @pytest.mark.parametrize("test_input", [None, 1, True, ["string"]])
    def test_upload_meta_data_no_time_created(self, fake_crossword_db, test_input):
        with pytest.raises(TypeError) as excinfo:
            fake_crossword_db.upload_puzzle_meta_data(
                puzzle_id="test123",
                puzzle_json_fname="file.json",
                time_created=test_input,
                last_modified="2/2/2 2:22 UTC+2",
                puzzle_image_fname="file.png",
            )
            assert excinfo.type == TypeError

    @pytest.mark.parametrize("test_input", [None, 1, True, ["string"]])
    def test_upload_meta_data_bad_last_modified(self, fake_crossword_db, test_input):
        with pytest.raises(TypeError) as excinfo:
            fake_crossword_db.upload_puzzle_meta_data(
                puzzle_id="test123",
                puzzle_json_fname="file.json",
                time_created="1/1/1 1:11 UTC+1",
                last_modified=test_input,
                puzzle_image_fname="file.png",
            )
        assert excinfo.type == TypeError
