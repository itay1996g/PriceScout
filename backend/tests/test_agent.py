from app.agent.prompts import SYSTEM_PROMPT


def test_system_prompt_includes_json_schema():
    assert "product_understood" in SYSTEM_PROMPT
    assert "results" in SYSTEM_PROMPT
    assert "seller_name" in SYSTEM_PROMPT


def test_system_prompt_instructs_top_3():
    assert "top 3" in SYSTEM_PROMPT
