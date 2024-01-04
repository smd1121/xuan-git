import os

from typer.testing import CliRunner

from xgit.test.test_utils import check_same_output

runner = CliRunner()


def test_ls_files():
    assert check_same_output(["ls-files"])

    cwd = os.getcwd()
    try:
        os.chdir("xgit")
        assert check_same_output(["ls-files", "--full-name"])
        assert check_same_output(["ls-files"])
    finally:
        os.chdir(cwd)
