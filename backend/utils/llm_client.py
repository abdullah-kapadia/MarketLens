from __future__ import annotations

import asyncio
import json
import logging
import os
from dataclasses import dataclass
from typing import Any, Literal

import anthropic
import openai
from dotenv import load_dotenv


logger = logging.getLogger(__name__)

load_dotenv()


class LLMUnavailableError(RuntimeError):
    pass


@dataclass
class ContentBlock:
    type: Literal["text", "tool_use"]
    text: str | None = None
    name: str | None = None
    input: dict | None = None
    id: str | None = None


@dataclass
class UnifiedResponse:
    content: list[ContentBlock]
    stop_reason: Literal["end_turn", "tool_use", "max_tokens"]
    model: str
    provider: Literal["anthropic", "openai"]

    @classmethod
    def from_anthropic(cls, response) -> "UnifiedResponse":
        blocks: list[ContentBlock] = []
        for block in response.content:
            if block.type == "text":
                blocks.append(ContentBlock(type="text", text=block.text))
            elif block.type == "tool_use":
                blocks.append(
                    ContentBlock(type="tool_use", name=block.name, input=block.input, id=block.id)
                )
        return cls(
            content=blocks,
            stop_reason=response.stop_reason,
            model=response.model,
            provider="anthropic",
        )

    @classmethod
    def from_openai(cls, response) -> "UnifiedResponse":
        blocks: list[ContentBlock] = []
        msg = response.choices[0].message
        if msg.content:
            blocks.append(ContentBlock(type="text", text=msg.content))
        if msg.tool_calls:
            for tc in msg.tool_calls:
                blocks.append(
                    ContentBlock(
                        type="tool_use",
                        name=tc.function.name,
                        input=json.loads(tc.function.arguments),
                        id=tc.id,
                    )
                )
        stop = "tool_use" if msg.tool_calls else "end_turn"
        return cls(content=blocks, stop_reason=stop, model=response.model, provider="openai")


def anthropic_to_openai_tools(tools: list[dict]) -> list[dict]:
    converted = []
    for tool in tools:
        converted.append(
            {
                "type": "function",
                "function": {
                    "name": tool["name"],
                    "description": tool.get("description", ""),
                    "parameters": tool.get("input_schema", {}),
                },
            }
        )
    return converted


def convert_messages_to_openai(messages: list[dict]) -> list[dict]:
    converted = []
    for msg in messages:
        role = msg.get("role")
        content = msg.get("content")
        
        # Handle assistant messages (may have text and/or tool_use blocks)
        if role == "assistant":
            assistant_msg = {"role": "assistant", "content": None}
            tool_calls = []
            text_parts = []
            
            if isinstance(content, list):
                for block in content:
                    if block.get("type") == "tool_use":
                        tool_calls.append({
                            "id": block.get("id"),
                            "type": "function",
                            "function": {
                                "name": block.get("name"),
                                "arguments": json.dumps(block.get("input", {}))
                            }
                        })
                    elif block.get("type") == "text":
                        text_parts.append(block.get("text", ""))
            else:
                text_parts.append(str(content) if content else "")
            
            if text_parts:
                assistant_msg["content"] = "\n".join(text_parts)
            if tool_calls:
                assistant_msg["tool_calls"] = tool_calls
            
            converted.append(assistant_msg)
        
        # Handle user messages (may have text and/or tool_result blocks)
        elif role == "user":
            if isinstance(content, list):
                for block in content:
                    if block.get("type") == "tool_result":
                        converted.append({
                            "role": "tool",
                            "tool_call_id": block.get("tool_use_id"),
                            "content": json.dumps(block.get("content")),
                        })
                    elif block.get("type") == "text":
                        converted.append({"role": "user", "content": block.get("text", "")})
            else:
                converted.append({"role": "user", "content": str(content) if content else ""})
    return converted


class LLMClient:
    def __init__(self) -> None:
        self.anthropic_client = anthropic.AsyncAnthropic()
        self.openai_client = openai.AsyncOpenAI() if os.getenv("OPENAI_API_KEY") else None
        self.primary = os.getenv("MODEL_PRIMARY", "gpt-5-nano-2025-08-07")
        self.fallback = os.getenv("MODEL_FALLBACK", "claude-sonnet-4-20250514")
        self.anthropic_available = bool(os.getenv("ANTHROPIC_API_KEY"))

    async def create_message(
        self,
        messages: list[dict],
        tools: list[dict],
        system: str,
        temperature: float = 0.3,
        max_tokens: int = 4096,
    ) -> UnifiedResponse:
        if self._is_openai_primary():
            if not self.openai_client:
                raise LLMUnavailableError("OpenAI client not configured")
            try:
                return await self._call_openai(messages, tools, system, temperature, max_tokens, model=self.primary)
            except Exception as e:
                logger.warning("OpenAI failed: %s. Falling back to Anthropic.", e)
                if not self.anthropic_available:
                    raise LLMUnavailableError("Both LLM providers unavailable") from e
                return await self._call_anthropic_with_retry(messages, tools, system, temperature, max_tokens)

        return await self._call_anthropic_with_retry(messages, tools, system, temperature, max_tokens)

    def _is_openai_primary(self) -> bool:
        return self.primary.lower().startswith("gpt")

    async def _call_anthropic_with_retry(
        self, messages: list[dict], tools: list[dict], system: str, temperature: float, max_tokens: int
    ) -> UnifiedResponse:
        try:
            return await self._call_anthropic(messages, tools, system, temperature, max_tokens)
        except (anthropic.APITimeoutError, anthropic.APIConnectionError, anthropic.InternalServerError) as e:
            logger.warning("Anthropic failed: %s. Retrying once...", e)
            try:
                return await self._call_anthropic(messages, tools, system, temperature, max_tokens)
            except Exception:
                if self.openai_client:
                    logger.warning("Anthropic retry failed. Falling back to OpenAI.")
                    return await self._call_openai(messages, tools, system, temperature, max_tokens, model=self.fallback)
                raise LLMUnavailableError("Both LLM providers unavailable") from e

    async def _call_anthropic(
        self, messages: list[dict], tools: list[dict], system: str, temperature: float, max_tokens: int
    ) -> UnifiedResponse:
        response = await asyncio.wait_for(
            self.anthropic_client.messages.create(
                model=self.primary,
                max_tokens=max_tokens,
                system=system,
                messages=messages,
                tools=tools,
                temperature=temperature,
            ),
            timeout=10.0,
        )
        return UnifiedResponse.from_anthropic(response)

    async def _call_openai(
        self,
        messages: list[dict],
        tools: list[dict],
        system: str,
        temperature: float,
        max_tokens: int,
        model: str,
    ) -> UnifiedResponse:
        if not self.openai_client:
            raise LLMUnavailableError("OpenAI client not configured")

        openai_messages = [{"role": "system", "content": system}]
        openai_messages.extend(convert_messages_to_openai(messages))
        openai_tools = anthropic_to_openai_tools(tools)

        response = await asyncio.wait_for(
            self.openai_client.chat.completions.create(
                model=model,
                messages=openai_messages,
                tools=openai_tools,
                temperature=temperature,
                max_tokens=max_tokens,
            ),
            timeout=15.0,
        )
        return UnifiedResponse.from_openai(response)
