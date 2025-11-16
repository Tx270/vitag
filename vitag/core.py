#!/usr/bin/env python3
import os
import sys
import json
import tempfile
import subprocess
from mutagen import File
from typing import Any, Dict, List
from mutagen.easyid3 import EasyID3KeyError
from pathlib import Path


class AudioSaveError(Exception):
    pass


class EditorDoesntExistError(Exception):
    pass


def get_files(files: List[Path]) -> List[Dict[str, Any]]:
    audio_list = []

    for f in files:
        audio = File(f, easy=True)

        if audio is None:
            print(f"Skipping unsupported or unreadable file: {f}")
            continue

        audio_list.append({
            "path": f,
            "audio": audio
        })

    return audio_list


def make_tmp_file(data: Dict[str, Any], editor: str) -> Dict[str, Any]:
    with tempfile.NamedTemporaryFile("w+", delete=False, suffix=".json") as tmp:
        json.dump(data, tmp, indent=2)
        path = tmp.name

    try:
        subprocess.run([editor, path])
    except FileNotFoundError as e:
        raise EditorDoesntExistError(e)

    with open(path) as f:
        result = json.load(f)

    return result


def write_tags(files: List[Dict[str, Any]], tags: Dict[str, Any], deleted_tags: List[str] = []) -> None:
    total = len(files) - 1
    for index, file in enumerate(files):
        audio = file["audio"]
        path = file["path"]
        backup = dict(audio)

        try:
            if not deleted_tags:
                audio.delete()

            for tag, value in tags.items():
                audio[tag] = value if isinstance(value, list) else [value]

            for tag in deleted_tags:
                audio.pop(tag, None)

            audio.save()

            sys.stdout.write(f"\r[{index}/{total}]")
            sys.stdout.flush()
        except Exception as e:
            sys.stdout.write("\r" + " " * 50 + "\r")
            sys.stdout.flush()

            audio.clear()
            audio.update(backup)

            if isinstance(e, EasyID3KeyError):
                msg = f"[red]Invalid ID3 key in [bold]{os.path.basename(path)}[/bold][/red]:\n{e}"
            else:
                msg = f"[red]Failed to save [bold]{os.path.basename(path)}[/bold][/red]:\n{e}"
            raise AudioSaveError(msg) from e
    sys.stdout.write("\r" + " " * 50 + "\r")
    sys.stdout.flush()


def list_changes(sorted_tags: Dict[str, Any], edited_tags: Dict[str, Any]) -> List[str]:
    changes = []
    for tag in sorted_tags.keys() | edited_tags.keys():
        old_value = sorted_tags.get(tag)
        new_value = edited_tags.get(tag)
        if old_value is None and new_value is not None:
            changes.append(f"Added tag '{tag}': {new_value}")
        elif new_value is None:
            changes.append(f"Removed tag '{tag}'")
        elif old_value != new_value:
            changes.append(f"Changed tag '{tag}': '{old_value}' => '{new_value}'")
    return changes


def main(paths: List[Path], verbose: bool, editor: str) -> str:
    files = get_files(paths)

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
    edited_tags = make_tmp_file(sorted_tags, editor)

    deleted_tags = []
    for tag in unique_tags:
        if tag not in edited_tags:
            deleted_tags.append(tag)

    final_tags = {}
    for tag, value in edited_tags.items():
        if value != "*":
            final_tags[tag] = value

    changes = list_changes(sorted_tags, edited_tags)

    if not changes:
        return "[yellow]No tags updated[/yellow]"

    if verbose:
        for change in changes:
            print(change)

    write_tags(files, final_tags, deleted_tags)

    return "[green]Audio tags updated successfully[/green]"
