import os
from ai_agents.ai_code_file_agent import AICodeFileAgent


def test_extracting_code_files_from_response(tmp_path):
    with open("tests/data/response_user.md", "r", encoding="utf8") as f:
        response = f.read()
    ret = AICodeFileAgent._extract_code_files(response)
    assert len(ret) == 3
