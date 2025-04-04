from typing import Any, Dict, List, Optional, Iterator
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import AIMessage, AIMessageChunk, BaseMessage
from langchain_core.outputs import ChatResult, ChatGeneration, ChatGenerationChunk
from langchain_core.callbacks import CallbackManagerForLLMRun
from langchain_core.runnables import RunnableConfig
import httpx, json
from loguru import logger
from punito.utils import get_default_settings


class LlamaChatModel(BaseChatModel):
    """
    Custom implementation of a LangChain-compatible chat model for LLaMA-based APIs.

    This class enables synchronous and streaming chat completions by sending HTTP
    requests to a specified LLaMA-compatible endpoint. It supports LangChain's
    `Runnable` protocol, making it composable in agent chains and pipelines.

    Parameters
    ----------
    model_name : str
        Name of the LLaMA model to use, passed in the payload as the "model" key.
    base_url : str
        Base URL of the inference server.
    endpoint : str, optional
        Endpoint path appended to `base_url`, by default "/completions".
    timeout : float or None, optional
        Request timeout in seconds.
    """

    model_name: str
    base_url: str
    endpoint: str = "/completions"
    timeout: Optional[float] = None

    @property
    def _llm_type(self) -> str:
        return "custom-llama-model"

    @property
    def _identifying_params(self) -> Dict[str, Any]:
        return {"model_name": self.model_name}

    def _generate(
            self,
            messages: List[BaseMessage],
            stop: Optional[List[str]] = None,
            run_manager: Optional[CallbackManagerForLLMRun] = None,
            **kwargs: Any,
    ) -> ChatResult:
        """
        Perform chat completion via HTTP POST request.
        """

        payload = {
            "model": self.model_name,
            "messages": _convert_messages(messages),
            "stream": False
        }

        url = self.base_url + self.endpoint

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
        """
        Stream chat completion results from the model via HTTP chunked response.

        Parameters
        ----------
        messages : list of BaseMessage
            Input messages for context.
        stop : list of str, optional
            Stop sequences (unused).
        run_manager : CallbackManagerForLLMRun, optional
            LangChain run manager to receive token callbacks.
        **kwargs : Any
            Additional generation parameters.

        Yields
        ------
        ChatGenerationChunk
            Partial chunks of the generated message.
        """
        payload = {
            "model": self.model_name,
            "messages": _convert_messages(messages),
            "stream": True
        }

        url = self.base_url + self.endpoint

        with httpx.stream("POST", url, json=payload, timeout=self.timeout) as response:
            for line in response.iter_lines():
                if not line or line == "data: [DONE]":
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
                except json.JSONDecodeError as e:
                    logger.warning(f"JSON decode error in stream chunk: {line}")
                except (KeyError, TypeError) as e:
                    logger.warning(f"Malformed stream chunk: {line} ({e.__class__.__name__})")

    def invoke(
            self,
            messages: List[BaseMessage],
            config: Optional[RunnableConfig] = None,
            **kwargs: Any,
    ) -> BaseMessage:
        """
        Generate a response for the given input messages.

        Parameters
        ----------
        messages : list of BaseMessage
            The list of messages to use as context for generation.
        config : Optional[RunnableConfig], optional
            Configuration for the Runnable.
        **kwargs : Any
            Additional keyword arguments passed to the generation method.

        Returns
        -------
        BaseMessage
            The generated AI message.
        """

        return self._generate(messages, **kwargs).generations[0].message

    def stream(
            self,
            messages: List[BaseMessage],
            config: Optional[RunnableConfig] = None,
            **kwargs: Any,
    ) -> Iterator[BaseMessage]:
        """
        Stream the generated response for the given input messages.

        Parameters
        ----------
        messages : list of BaseMessage
            The list of messages to use as context for streaming generation.
        config : Optional[RunnableConfig], optional
            Configuration for the Runnable.
        **kwargs : Any
            Additional keyword arguments passed to the streaming method.

        Yields
        ------
        BaseMessage
            A stream of partial AI messages (tokens or message chunks).
        """

        for chunk in self._stream(messages, **kwargs):
            yield chunk.message


def _convert_messages(messages: List[BaseMessage]) -> List[Dict[str, str]]:
    """
    Convert LangChain message objects to dict format required by the LLaMA API.
    """

    return [{"role": m.type, "content": m.content} for m in messages]


def create_llama_model_from_config(timeout=None) -> LlamaChatModel:
    """
    Create an instance of LlamaChatModel using default configuration.

    Parameters
    ----------
    timeout : float or None, optional
        Request timeout in seconds.

    Returns
    -------
    LlamaChatModel
        An initialized LlamaChatModel instance.
    """

    settings = get_default_settings()
    return LlamaChatModel(
        model_name=settings["MODEL"],
        base_url=settings["BASE_URL"],
        endpoint=settings["ENDPOINT"],
        timeout=timeout,
    )
