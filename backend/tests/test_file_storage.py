from ampf_local import FileStorage


class T(FileStorage):
    pass


def test_default_ext(tmp_path):
    t = T(root_dir=tmp_path, default_ext="json")

    p = t._create_file_path("xxx")

    assert p == tmp_path.joinpath("xxx.json")


def test_no_default_ext(tmp_path):
    t = T(root_dir=tmp_path)

    p = t._create_file_path("xxx", "txt")

    assert p == tmp_path.joinpath("xxx.txt")


def test_subfolder(tmp_path):
    t = T(root_dir=tmp_path, subfolder_characters=2, default_ext="json")

    p = t._create_file_path("xxx")

    assert p == tmp_path.joinpath("xx", "xxx.json")
