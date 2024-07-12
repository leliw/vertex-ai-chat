from pathlib import Path

import pytest
from ai_agents.ai_code_file_agent import AICodeFileAgent


def test_extracting_code_files_from_response(tmp_path):
    with open("tests/data/response_user.md", "r", encoding="utf8") as f:
        response = f.read()
    ret = AICodeFileAgent._extract_code_files(response)
    assert len(ret) == 3


@pytest.fixture
def test_dir(tmp_path):
    test_dir = tmp_path / "test_dir"
    test_dir.mkdir(exist_ok=True)
    with open(test_dir / "file1.py", "w", encoding="utf8") as f:
        f.write("print('Hello world1')")
    with open(test_dir / "file2.py", "w", encoding="utf8") as f:
        f.write("print('Hello world2')")
    sub_dir = test_dir / "sub_dir"
    sub_dir.mkdir(exist_ok=True)
    with open(sub_dir / "file3.py", "w", encoding="utf8") as f:
        f.write("print('Hello world3')")
    return test_dir


def test_read_files_one_file_path(test_dir):
    """Test reading one file passed as path."""
    ret = AICodeFileAgent._read_files(files=[test_dir / "file1.py"])
    assert len(ret) == 1
    assert ret[0][0] == test_dir / "file1.py"
    assert ret[0][1] == "print('Hello world1')"


def test_read_files_two_files_and_one_dir_path(test_dir):
    """Test reading two files and one directory passed as paths."""
    ret = AICodeFileAgent._read_files(
        files=[
            test_dir / "file1.py",
            test_dir / "file2.py",
            test_dir / "sub_dir",
        ]
    )
    assert len(ret) == 3


def test_read_files_two_files_and_one_dir_string(test_dir):
    """Test reading two files and one directory passed as strings."""
    ret = AICodeFileAgent._read_files(
        files=[
            str(test_dir / "file1.py"),
            str(test_dir / "file2.py"),
            str(test_dir / "sub_dir"),
        ]
    )
    assert len(ret) == 3


def test_read_files_with_root_dir(test_dir):
    """Test reading file with root directory.
    Return should be relative to root_dir."""
    ret = AICodeFileAgent._read_files(
        files=["file1.py", "file2.py", "sub_dir"], root_dir=test_dir
    )
    assert len(ret) == 3
    assert ret[0][0] == Path("file1.py")
    assert ret[0][1] == "print('Hello world1')"
