from typing import Any, Dict, List, Optional, Iterator

from langchain_core.language_models import BaseChatModel
from langchain_core.messages import AIMessage, AIMessageChunk, BaseMessage
from langchain_core.outputs import ChatResult, ChatGeneration, ChatGenerationChunk
from langchain_core.callbacks import CallbackManagerForLLMRun
from punito.utils import get_default_settings

import httpx
import json
from loguru import logger


class LlamaChatModel(BaseChatModel):
    """LangChain wrapper for custom on-prem LLaMA model via HTTP API."""

    model_name: str
    base_url: str
    endpoint: str = "/completions"
    timeout: Optional[float] = None
    streaming: bool = False

    @property
    def _llm_type(self) -> str:
        return "custom-llama-chat"

    @property
    def _identifying_params(self) -> Dict[str, Any]:
        return {"model_name": self.model_name}

    def _convert_messages(self, messages: List[BaseMessage]) -> List[Dict[str, str]]:
        return [{"role": m.type, "content": m.content} for m in messages]

    def _generate(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> ChatResult:
        payload = {
            "model": self.model_name,
            "messages": self._convert_messages(messages),
            "stream": False
        }

        url = self.base_url + self.endpoint
        logger.info(f"Calling {url}")

        response = httpx.post(url, json=payload, timeout=self.timeout)
        response.raise_for_status()

        data = response.json()
        content = data["choices"][0]["message"]["content"]

        message = AIMessage(content=content)
        generation = ChatGeneration(message=message)
        return ChatResult(generations=[generation])

    def _stream(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> Iterator[ChatGenerationChunk]:
        payload = {
            "model": self.model_name,
            "messages": self._convert_messages(messages),
            "stream": True
        }

        url = self.base_url + self.endpoint
        logger.info(f"Streaming from {url}")

        with httpx.stream("POST", url, json=payload, timeout=self.timeout) as response:
            for line in response.iter_lines():
                if not line:
                    continue
                try:
                    data = json.loads(line.replace("data: ", ""))
                    content = data.get("choices", [{}])[0].get("delta", {}).get("content", "")
                    if content:
                        chunk = ChatGenerationChunk(
                            message=AIMessageChunk(content=content)
                        )
                        if run_manager:
                            run_manager.on_llm_new_token(content, chunk=chunk)
                        yield chunk
                except Exception as e:
                    logger.warning(f"Failed to parse stream chunk: {line}")

def create_llama_model_from_config(streaming = False, timeout = None) -> LlamaChatModel:
    settings = get_default_settings()
    return LlamaChatModel(
        model_name=settings["MODEL"],
        base_url=settings["BASE_URL"],
        endpoint=settings["ENDPOINT"],
        timeout=timeout,
        streaming=streaming,
    )