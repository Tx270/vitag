import os
import json
import tempfile
import subprocess
from json import JSONDecodeError
from mutagen import File
from mutagen.easyid3 import EasyID3KeyError


def getFiles(directory):
    files = []
    for f in os.listdir(directory):
        if not f.endswith((".mp3", ".flac")):
            continue
        path = os.path.join(directory, f)
        audio = File(path, easy=True)
        if audio is None:
            print(f"Skipping unsupported or unreadable file: {f}")
            continue
        files.append({"path": path, "audio": audio})
    return files


def makeTempFile(data):
    with tempfile.NamedTemporaryFile("w+", delete=False, suffix=".json") as tmp:
        json.dump(data, tmp, indent=2)
        path = tmp.name

    subprocess.run([os.environ.get("EDITOR", "vi"), path])

    try:
        with open(path) as f:
            result = json.load(f)
    except JSONDecodeError:
        print("Not valid JSON")
        exit()

    return result


def writeTags(files, tags, deleted_tags=[]):
    for f in files:
        audio = f["audio"]
        path = f["path"]
        backup = dict(audio)

        if not deleted_tags:
            audio.delete()

        for tag, value in tags.items():
            audio[tag] = value if isinstance(value, list) else [value]

        for tag in deleted_tags:
            audio.pop(tag, None)

        try:
            audio.save()
        except EasyID3KeyError as e:
            print(f"Failed to save {os.path.basename(path)} due to invalid ID3 key: {e}")
            audio.clear()
            audio.update(backup)
            return
        except Exception as e:
            print(f"Failed to save {os.path.basename(path)}: {e}")
            audio.clear()
            audio.update(backup)


def vitagFolder(path):
    files = getFiles(path)

    song_tags_list = []
    for f in files:
        tags = {}
        for tag, value in f["audio"].items():
            tags[tag] = value[0] if len(value) == 1 else value
        song_tags_list.append(tags)

    all_tags = set()
    for tags in song_tags_list:
        all_tags.update(tags.keys())

    unique_tags = {}
    for tag in all_tags:
        values = []
        for tags in song_tags_list:
            if tag in tags:
                values.append(tags[tag])

        if len(values) > 0 and all(v == values[0] for v in values):
            unique_tags[tag] = values[0]
        else:
            unique_tags[tag] = "*"

    sorted_tags = dict(sorted(unique_tags.items()))
    edited_tags = makeTempFile(sorted_tags)

    deleted_tags = []
    for tag in unique_tags:
        if tag not in edited_tags:
            deleted_tags.append(tag)

    final_tags = {}
    for tag, value in edited_tags.items():
        if value != "*":
            final_tags[tag] = value

    writeTags(files, final_tags, deleted_tags)

def vitagFile(path):
    audio = File(path, easy=True)
    if audio is None:
        print("Unsupported or unreadable file")
        return

    tags = {}
    for t, v in audio.items():
        if len(v) == 1:
            tags[t] = v[0]
        else:
            tags[t] = v

    edited = makeTempFile(tags)

    final_tags = {}
    for t, v in edited.items():
        if v != "*":
            final_tags[t] = v

    writeTags([{"path": path, "audio": audio}], final_tags)
