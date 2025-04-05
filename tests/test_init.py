import pytest
import os

# use pathlib for easier path manipulation
from pathlib import Path

from pygit import cli
from pygit import cmds


def test_init_default_path(tmp_path: Path, monkeypatch):
    """test init command in the current dir
    
    use pytest's built-in fixture tmp_path to create a tmp dir. 
        pytest will create a tmp dir in tmp_path before this test
        pytest will automatically clean up and delete the tmp dir after this test
    use pytest's built-in fixture monkeypatch to change the current dir"""

    # use monkeypatch to change to a tmp_path
    print(f"Temporary dir for this test is: {tmp_path}")
    monkeypatch.chdir(tmp_path)
    assert not (tmp_path / ".pygit").exists()

    # run the init command 
    parser = cli.create_parser()
    args = parser.parse_args(['init'])
    cmds.init(args)

    # check if .pygit directory and its contents were created
    pygit_dir = tmp_path / ".pygit"
    assert pygit_dir.is_dir()

    assert (pygit_dir / "objects").is_dir()
    assert (pygit_dir / "refs").is_dir()
    assert (pygit_dir / "refs" / "heads").is_dir()

    assert (pygit_dir / "HEAD").is_file()

    head_content = (pygit_dir / "HEAD").read_text()
    assert head_content == "ref: refs/heads/main\n"

def test_init_specific_path(tmp_path: Path, monkeypatch):
    """test init command in a specific dir"""

    monkeypatch.chdir(tmp_path)
    sub_dir = tmp_path / "my_test_dir"
    print(f"Temporary dir for this test is: {sub_dir}")
    assert not (sub_dir / ".pygit").exists()

    # run the init command
    parser = cli.create_parser()
    args = parser.parse_args(['init', str(sub_dir)]) # pass the specific path
    cmds.init(args)

    # check if .pygit dir and its contents were created
    assert sub_dir.is_dir()

    pygit_dir = sub_dir / ".pygit"
    assert pygit_dir.is_dir()

    assert (pygit_dir / "objects").is_dir()
    assert (pygit_dir / "refs").is_dir()
    assert (pygit_dir / "refs" / "heads").is_dir()

    assert (pygit_dir / "HEAD").is_file()

    head_content = (pygit_dir / "HEAD").read_text()
    assert head_content == "ref: refs/heads/main\n"


