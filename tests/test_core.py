import pytest
from pathlib import Path
from mutagen.id3 import ID3
from vitag.core import write_tags, get_files, list_changes, AudioSaveError


@pytest.fixture
def sample_mp3():
    return Path(__file__).parent / "sample.mp3"


def test_get_files(sample_mp3):
    files = get_files([sample_mp3])
    assert len(files) == 1
    assert files[0]["path"] == sample_mp3


def test_write_tags_add_tag(sample_mp3):
    files = get_files([sample_mp3])
    tags = {"artist": "Test Artist", "album": "Test Album"}
    write_tags(files, tags, [])

    audio = ID3(sample_mp3)
    assert audio.get("TPE1").text[0] == "Test Artist"
    assert audio.get("TALB").text[0] == "Test Album"


def test_write_tags_invalid_key(sample_mp3):
    files = get_files([sample_mp3])
    tags = {"INVALID": "value"}
    with pytest.raises(AudioSaveError):
        write_tags(files, tags, [])


@pytest.mark.parametrize(
    "sorted_tags, edited_tags, expected",
    [
        ({"artist": "A"}, {"artist": "A", "album": "X"}, ["Added tag 'album': X"]),
        ({"artist": "A", "album": "X"}, {"artist": "A"}, ["Removed tag 'album'"]),
        ({"artist": "A", "album": "X"}, {"artist": "B", "album": "X"}, ["Changed tag 'artist': 'A' => 'B'"]),
        ({"artist": "A"}, {"artist": "A"}, []),
        ({"artist": "A"}, {"artist": "B", "album": "X"}, [
            "Added tag 'album': X",
            "Changed tag 'artist': 'A' => 'B'"
        ])
    ]
)
def test_list_changes(sorted_tags, edited_tags, expected):
    result = list_changes(sorted_tags, edited_tags)
    assert sorted(result) == sorted(expected)
