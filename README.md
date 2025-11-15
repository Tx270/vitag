# vitag
![Python](https://img.shields.io/badge/python-3.10+-blue) ![License](https://img.shields.io/badge/license-MIT-blue.svg) ![PyPI](https://img.shields.io/pypi/v/vitag.svg)

A minimal CLI tool inspired by [vidir](https://github.com/trapd00r/vidir), enabling fast batch editing of audio metadata in your favorite text editor (default is your $EDITOR system var).

## Features

- Collects audio files from given paths
- Extracts tags using `mutagen` and writes them into a temp file
- Lets you edit tags in your preferred editor
- Validates changes, detects conflicts, and applies updates automatically

## Requirements

- `Python 3.10+`
- [`mutagen`](https://pypi.org/project/mutagen/)
- [`typer`](https://pypi.org/project/typer/)

## Instalation

![status](https://img.shields.io/badge/status-WIP-yellow)

Install through [pip](https://pip.pypa.io/en/stable/):

```bash
$ pip install vitag
```

Or clone the repository:
```bash
$ git clone https://github.com/Tx270/vitag
$ cd vitag
# build locally and install with pip
$ pip install .
# or manually install dependencies and run
$ pip install mutagen typer
$ python3 "./cli.py"
```

## Usage

For more info check `--help`

```bash
vitag [PATH ...] \
    [--recursive] \
    [--editor <cmd>] \
    [--verbose]
```

## Examples

```bash
# Edit all audio files in a folder
vitag "Album 1"

# Edit multiple paths at once with custom editor
vitag "01 Song.mp3" "Album 2/" --editor nano

# Recursive scan (for example useful for albums with many disks)
vitag "Album 1/" -r
```

## Roadmap

- Extensions:
    - [ ]  Add `--extension` option to filter file types
    - [ ]  Test with more audio formats
    - [ ]  Add supported audio formats to the README file
- UI/UX:
    - [ ]  Add progress bars for loading and saving tags
- Distribution:
    - [ ]  Upload package to PyPI
- Features:
    - [ ]  Add cover art support


## License

See [LICENSE](https://github.com/Tx270/vitag/blob/main/LICENSE)
