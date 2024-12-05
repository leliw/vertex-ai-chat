import pytest
from app.knowledge_base.knowledge_base_model import KnowledgeBaseItem
from app.knowledge_base.knowledge_base_storage import KnowledgeBaseStorage


@pytest.fixture
def kb(embedding_model):
    kb = KnowledgeBaseStorage(embedding_model)
    # "universal-sentence-encoder"
    yield kb
    kb.drop()


@pytest.mark.asyncio
async def test_before_save(kb):
    item = {"title": "title", "content": "content"}
    item = await kb.on_before_save(item)
    assert "embedding" in item


@pytest.mark.asyncio
async def test_find_nearest(kb):
    ret = await kb.find_nearest("text", ["pytest"])

    assert ret is not None
    assert len(ret) == 0

    kb1 = KnowledgeBaseItem(
        title="Paris", content="Paris is the capital of France.", keywords=["pytest"]
    )
    await kb.save(kb1)
    kb2 = KnowledgeBaseItem(
        title="France", content="France is a country in Europe.", keywords=["pytest"]
    )
    await kb.save(kb2)

    ret = await kb.find_nearest("What is the capital of France?", ["pytest"])

    assert ret is not None
    assert len(ret) == 2
    assert ret[0].title == "France"
    assert ret[0].content == "France is a country in Europe."
    assert ret[1].title == "Paris"
    assert ret[1].content == "Paris is the capital of France."
