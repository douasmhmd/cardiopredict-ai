"""OpenAI tool-calling helper for MedPredict AI."""

from __future__ import annotations

import json
from typing import Any, Callable, Dict, List, Optional, Tuple

from openai import OpenAI

from chatbot.functions import TOOLS


ToolHandler = Callable[[str, Dict[str, Any]], str]


def run_agent_turn(
    client: OpenAI,
    messages: List[Dict[str, Any]],
    tool_handler: ToolHandler,
    model: str = "gpt-4o",
    max_tool_rounds: int = 8,
) -> Tuple[str, List[Dict[str, Any]]]:
    """
    Run OpenAI chat completions with tools until the model stops calling tools.
    tool_handler(name, args_dict) -> tool result string
    Returns (last assistant text, full message list including new turns).
    """
    local = list(messages)
    final_text = ""

    for _ in range(max_tool_rounds):
        response = client.chat.completions.create(
            model=model,
            messages=local,
            tools=TOOLS,
            tool_choice="auto",
            temperature=0.35,
        )
        msg = response.choices[0].message

        assistant_payload: Dict[str, Any] = {
            "role": "assistant",
            "content": msg.content or "",
        }
        if msg.tool_calls:
            assistant_payload["tool_calls"] = [
                {
                    "id": tc.id,
                    "type": "function",
                    "function": {
                        "name": tc.function.name,
                        "arguments": tc.function.arguments or "{}",
                    },
                }
                for tc in msg.tool_calls
            ]
        local.append(assistant_payload)

        if msg.content:
            final_text = msg.content

        if not msg.tool_calls:
            break

        for tc in msg.tool_calls:
            name = tc.function.name
            try:
                args = json.loads(tc.function.arguments or "{}")
            except json.JSONDecodeError:
                args = {}
            try:
                result = tool_handler(name, args)
            except Exception as exc:
                result = f"Tool error: {exc}"
            local.append(
                {
                    "role": "tool",
                    "tool_call_id": tc.id,
                    "content": str(result)[:12000],
                }
            )

    return final_text, local


def openai_client(api_key: Optional[str]) -> Optional[OpenAI]:
    if not api_key:
        return None
    return OpenAI(api_key=api_key)
