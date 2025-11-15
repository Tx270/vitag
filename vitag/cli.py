#!/usr/bin/env python3
import sys
import os
from pathlib import Path
import platform
import typer
from rich import print
from json import JSONDecodeError
from .core import main as process
from .core import AudioSaveError, EditorDoesntExistError

app = typer.Typer(add_completion=False)


def detect_editor() -> str:
    env_editor = os.environ.get("VISUAL") or os.environ.get("EDITOR")
    if env_editor:
        return env_editor

    if platform.system() == "Windows":
        return "notepad"
    else:
        return "vi"


def read_stdin() -> list[Path]:
    data = sys.stdin.read().strip().splitlines()
    return [Path(line) for line in data if line]


def expand_paths(paths: list[str], recursive: bool = False) -> list[Path]:
    result = []
    allowed = (".mp3", ".flac")

    def is_allowed(path: Path) -> bool:
        return path.suffix.lower() in allowed

    for p in paths:
        if p == "-":
            stdin_paths = []
            for f in read_stdin():
                resolved = f.resolve()
                if is_allowed(resolved):
                    stdin_paths.append(resolved)
            result.extend(stdin_paths)
            continue

        path = Path(p).resolve()

        if not path.exists():
            raise FileNotFoundError(f"[bold red]Path does not exist[/bold red]:\n\"{path}\"")

        if path.is_dir():
            iterator = path.rglob("*") if recursive else path.iterdir()
            for child in iterator:
                if child.is_file() and is_allowed(child):
                    result.append(child.resolve())
        else:
            if is_allowed(path):
                result.append(path)

    return result


@app.command()
def main(
    paths: list[str] = typer.Argument(
        None, help="Files or directories. '-' reads file list from stdin."
    ),
    verbose: bool = typer.Option(
        False, "--verbose", "-v", help="Enable verbose output"
    ),
    editor: str = typer.Option(
        detect_editor, "--editor", "-e", help="Choose a custom editor"
    ),
    recursive: bool = typer.Option(
        False, "--recursive", "-r", help="Descend into directories"
    ),
) -> None:
    if not paths:
        paths = ["."]

    try:
        files = expand_paths(paths, recursive)
    except FileNotFoundError as e:
        print(str(e))
        raise typer.Exit(code=1)

    if not files:
        print("[red bold]No valid audio files detected in input![/red bold]")
        raise typer.Exit(code=1)

    try:
        result = process(files, verbose, editor)
        print(result)
    except JSONDecodeError:
        print("[red bold]You broke the json file![/red bold]")
        raise typer.Exit(code=1)
    except AudioSaveError as e:
        print(str(e))
        raise typer.Exit(code=1)
    except EditorDoesntExistError:
        print("[red bold]Editor you passed does not exists![/red bold]")
        raise typer.Exit(code=1)


if __name__ == "__main__":
    app()
