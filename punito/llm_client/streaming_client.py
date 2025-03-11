import httpx
from dynaconf import Dynaconf
from pathlib import Path
from loguru import logger
import json

def stream_chat_completion(prompt: str) -> None:
    settings = Dynaconf(settings_files=[Path(__file__).resolve().parents[2] / "settings.toml"])['DEFAULT']

    payload = {
        "model": settings["MODEL"],
        "messages": [{"role": "system", "content": "You are expert at writing Mockito tests. Write test using given, when, then convention. Mock all dependencies. Use Spy only for Mappers"},
                     {"role": "user", "content": f"Write tests for this class {prompt}"}],
        "stream": True
    }

    headers = {
        "Content-Type": "application/json",
    }

    api_url = settings.BASE_URL + settings.COMPLETIONS_ENDPOINT

    try:
        logger.info("Sending request to API endpoint: {}", api_url)
        message = ""
        with httpx.stream("POST", api_url, json=payload, headers=headers, timeout=None) as response:
            logger.info("Response received. Collecting content...")
            for line in response.iter_lines():
                if line:  # Ignore empty lines
                    try:
                        data = json.loads(line.replace("data: ", ""))
                        content = data.get("choices", [{}])[0].get("delta", {}).get("content", "")
                        if content:
                            logger.debug(content)
                            message += content
                    except json.JSONDecodeError:
                        logger.warning("Failed to parse JSON: {}", line)
        logger.success("Result: \n{}", message)
    except httpx.HTTPError as e:
        logger.error("HTTP request failed: {}", str(e))
    except Exception as e:
        logger.exception("An unexpected error occurred: {}", str(e))
