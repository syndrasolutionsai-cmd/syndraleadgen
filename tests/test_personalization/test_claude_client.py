import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from leadforge.personalization.claude_client import ask_claude_json


@pytest.mark.asyncio
async def test_ask_claude_json_parses_response():
    mock_message = MagicMock()
    mock_message.content = [MagicMock(text='{"result": "hello"}')]

    with patch("leadforge.personalization.claude_client.client") as mock_client:
        mock_client.messages.create = AsyncMock(return_value=mock_message)
        result = await ask_claude_json(
            system="You are helpful",
            user="Say hello",
            expected_keys=["result"],
        )
    assert result["result"] == "hello"


@pytest.mark.asyncio
async def test_ask_claude_json_raises_on_invalid_json():
    mock_message = MagicMock()
    mock_message.content = [MagicMock(text="not json at all")]

    with patch("leadforge.personalization.claude_client.client") as mock_client:
        mock_client.messages.create = AsyncMock(return_value=mock_message)
        with pytest.raises(ValueError, match="Failed to parse"):
            await ask_claude_json(system="s", user="u", expected_keys=["x"])
