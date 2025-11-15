from typer.testing import CliRunner
from vitag.cli import app

runner = CliRunner()


def test_cli_no_files(tmp_path):
    result = runner.invoke(app, [str(tmp_path)])
    assert "No valid audio files detected" in result.stdout or result.exit_code == 1


def test_cli_help():
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "Files or directories" in result.output
