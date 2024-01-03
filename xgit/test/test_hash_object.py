import tempfile
import subprocess

from typer.testing import CliRunner

from xgit.cli import app
from xgit.test.test_utils import gen_random_string, temp_xgit_workspace

runner = CliRunner()


def test_hash_value():
    content = gen_random_string()

    with tempfile.NamedTemporaryFile() as f:
        with open(f.name, "w", encoding="utf-8") as f:
            f.write(content)

        expected_by_file = subprocess.run(
            ["git", "hash-object", f.name], check=True, capture_output=True, text=True
        ).stdout
        result_by_file = runner.invoke(app, ["hash-object", f.name]).stdout
        assert result_by_file == expected_by_file

        expected_by_stdin = subprocess.run(
            ["git", "hash-object", "--stdin"], input=content, check=True, capture_output=True, text=True
        ).stdout
        result_by_stdin = runner.invoke(app, ["hash-object", "--stdin"], input=content).stdout
        assert result_by_stdin == expected_by_stdin


def test_hash_object_write():
    content = gen_random_string()

    with temp_xgit_workspace():
        with tempfile.NamedTemporaryFile() as f:
            with open(f.name, "w", encoding="utf-8") as f:
                f.write(content)

            result = runner.invoke(app, ["hash-object", "-w", f.name])
            object_id = result.stdout.strip()

            read_by_git = subprocess.run(
                ["git", "cat-file", "blob", object_id], check=True, capture_output=True, text=True
            ).stdout

            assert content == read_by_git
