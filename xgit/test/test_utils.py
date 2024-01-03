import os
import random
import string
import tempfile
import contextlib
import subprocess

from loguru import logger
from typer.testing import CliRunner

from xgit.cli import app

runner = CliRunner(mix_stderr=False)


@contextlib.contextmanager
def temp_git_workspace(use_xgit: bool = False):
    original_dir = os.getcwd()
    with tempfile.TemporaryDirectory() as dir:
        try:
            os.chdir(dir)
            git = "xgit" if use_xgit else "git"
            subprocess.run([git, "init", dir], check=True)
            yield dir
        finally:
            os.chdir(original_dir)


@contextlib.contextmanager
def temp_xgit_workspace():
    with temp_git_workspace(use_xgit=True) as dir:
        yield dir


def gen_random_string(len: int = 1000):
    # 关于 `\r` 的事情有点脏，我不想管。有关换行符的事情，关心的朋友可以搜索 autocrlf
    # 具体来说，如果不去掉 `\r`，那么在下面测试的一些情况中（尤其是有和 stdout 交互的情况中） `\r` 会变成 `\n`
    # 这会导致内容不一致，进而导致 SHA 不正确。
    # 如果您感兴趣，可以把下面的 `.replace` 去掉试试！
    # 如果有更正确的方案，也请您告诉我~
    alphabet = string.octdigits + string.whitespace.replace("\r", "")
    return "".join(random.choice(alphabet) for _ in range(len))


def gen_random_sha():
    return "".join(random.choice(string.hexdigits) for _ in range(40))


def check_same_output(cmd: list[str]) -> bool:
    git_result = subprocess.run(["git"] + cmd, capture_output=True, check=False)
    xgit_result = runner.invoke(app, cmd)
    xgit_stdout = xgit_result.stdout.encode()

    if git_result.returncode != xgit_result.exit_code:
        logger.info(f"cmd: {cmd}")
        logger.info(f"exit_code not equal: {git_result.returncode} != {xgit_result.exit_code}")
        return False

    if git_result.returncode != 0:
        return True

    if git_result.stdout != xgit_stdout:
        logger.info(f"cmd: {cmd}")
        logger.info(f"stdout not equal: {git_result.stdout} != {xgit_stdout}")
        return False

    return True
