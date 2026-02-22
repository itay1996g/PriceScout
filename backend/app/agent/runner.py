import json
from collections.abc import AsyncGenerator

import anthropic

from app.agent.prompts import SYSTEM_PROMPT
from app.config import settings


async def run_search_agent(query: str) -> AsyncGenerator[dict, None]:
    """Run the Claude agent and yield SSE events as dicts."""
    client = anthropic.Anthropic(api_key=settings.anthropic_api_key)

    yield {"status": "searching", "message": f"Researching: {query}..."}

    try:
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=4096,
            system=SYSTEM_PROMPT,
            tools=[
                {
                    "type": "web_search_20250305",
                    "name": "web_search",
                    "max_uses": 10,
                },
            ],
            messages=[{"role": "user", "content": query}],
        )

        yield {"status": "analyzing", "message": "Analyzing results..."}

        # Extract the text response from the message
        text_content = ""
        for block in response.content:
            if block.type == "text":
                text_content = block.text
                break

        # Parse the JSON from the response
        json_str = text_content
        if "```json" in json_str:
            json_str = json_str.split("```json")[1].split("```")[0]
        elif "```" in json_str:
            json_str = json_str.split("```")[1].split("```")[0]

        data = json.loads(json_str.strip())

        yield {"status": "complete", "data": data}

    except json.JSONDecodeError:
        yield {
            "status": "complete",
            "data": {
                "product_understood": query,
                "location": "Unknown",
                "results": [],
                "search_summary": "The agent returned results in an unexpected format. Please try again.",
                "raw_response": text_content,
            },
        }
    except anthropic.APIError as e:
        yield {
            "status": "error",
            "message": f"Search failed: {str(e)}",
        }
