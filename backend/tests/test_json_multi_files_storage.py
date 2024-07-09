from pydantic import BaseModel
from ampf_local.json_multi_files_storage import JsonMultiFilesStorage


class D(BaseModel):
    name: str
    value: str


def test_simple_key_all(tmp_path):
    t = JsonMultiFilesStorage[D](D, key_name="name", root_dir=tmp_path, subfolder_characters=2)
    d = D(name="foo", value="beer")
    t.put("foo", d)

    assert ["foo"] == list(t.keys())
    assert d == t.get("foo")

    t.delete("foo")
    assert [] == list(t.keys())
    assert t.get("foo") is None

def test_folder_key_all(tmp_path):
    t = JsonMultiFilesStorage[D](D, key_name="name", root_dir=tmp_path, subfolder_characters=2)
    d = D(name="foo", value="beer")
    t.put("kung/foo", d)

    assert ["kung/foo"] == list(t.keys())
    assert d == t.get("kung/foo")

    t.delete("kung/foo")
    assert [] == list(t.keys())
    assert t.get("kung/foo") is None
