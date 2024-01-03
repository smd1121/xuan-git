import subprocess
from pathlib import Path

from typer.testing import CliRunner

from xgit.test.test_utils import gen_random_sha, check_same_output, gen_random_string, temp_git_workspace

runner = CliRunner()


def test_cat_blob():
    with temp_git_workspace() as dir:
        file1 = Path(dir) / "test"
        with open(file1, "w", encoding="utf-8") as f:
            f.write(gen_random_string())

        file2 = Path(dir) / "a" / "b"
        file2.parent.mkdir(exist_ok=True, parents=True)
        file2.touch()

        subprocess.run(["git", "add", "."], check=True)
        subprocess.run(["git", "commit", "-m", "test"], check=True)

        to_test = ["-p", "-e", "-t", "-s", "blob"]

        # on tree object
        sha = subprocess.run(
            ["git", "rev-parse", "HEAD^{tree}"], check=True, capture_output=True, text=True
        ).stdout.strip()
        for i in to_test:
            assert check_same_output(["cat-file", i, sha])

        # on contents (including blob object)
        objs = subprocess.run(
            ["git", "ls-tree", "-r", "HEAD^{tree}"], check=True, capture_output=True, text=True
        ).stdout.strip()
        obj_lst = objs.split("\n")
        for obj in obj_lst:
            sha = obj.split()[2]
            for i in to_test:
                assert check_same_output(["cat-file", i, sha])

        # on not exist object
        random_sha = gen_random_sha()
        for i in to_test:
            assert check_same_output(["cat-file", i, random_sha])
