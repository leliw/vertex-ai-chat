from pydantic import BaseModel
from ampf_local.json_one_file_storage import JsonOneFileStorage


class D(BaseModel):
    name: str
    value: str

def test_constructor(tmp_path):
    # test file name - Path with ext
    t1 = JsonOneFileStorage[D](D, key_name="name", file_name=tmp_path.joinpath("data.json"))
    assert t1.file_name == tmp_path.joinpath("data.json")
    # test file name - Path without ext
    t2 = JsonOneFileStorage[D](D, key_name="name", file_name=tmp_path.joinpath("data"))
    assert t2.file_name == tmp_path.joinpath("data.json")
    # test file name - string with ext
    t3 = JsonOneFileStorage[D](D, key_name="name", file_name=str(tmp_path.joinpath("data.json")))
    assert t3.file_name == tmp_path.joinpath("data.json")
    # test file name - string without ext
    t4 = JsonOneFileStorage[D](D, key_name="name", file_name=str(tmp_path.joinpath("data")))
    assert t4.file_name == tmp_path.joinpath("data.json")

def test_simple_key_all(tmp_path):
    t = JsonOneFileStorage[D](D, key_name="name", file_name=tmp_path.joinpath("data"))
    d = D(name="foo", value="beer")
    t.put("foo", d)

    assert ["foo"] == list(t.keys())
    assert d == t.get("foo")

    t.delete("foo")
    assert [] == list(t.keys())
    assert t.get("foo") is None

def test_folder_key_all(tmp_path):
    t = JsonOneFileStorage[D](D, key_name="name", file_name=tmp_path.joinpath("data"))
    d = D(name="foo", value="beer")
    t.put("kung/foo", d)

    assert ["kung/foo"] == list(t.keys())
    assert d == t.get("kung/foo")

    t.delete("kung/foo")
    assert [] == list(t.keys())
    assert t.get("kung/foo") is None
