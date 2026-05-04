from __future__ import annotations

import logging
import time

import httpx

from config import (
    GROQ_API_KEY,
    GROQ_MODEL,
    INFERENCE_MODE,
    MAX_TOKENS,
    OLLAMA_BASE_URL,
    OLLAMA_MODEL,
    TEMPERATURE,
)

logger = logging.getLogger(__name__)


async def infer(prompt: str, system: str = '') -> str:
    logger.info('infer start mode=%s model=%s', INFERENCE_MODE, GROQ_MODEL if INFERENCE_MODE == 'groq' else OLLAMA_MODEL)
    if INFERENCE_MODE == 'groq' and GROQ_API_KEY:
        return await _groq_infer(prompt, system)
    return await _ollama_infer(prompt, system)


async def qwen_request(prompt: str, max_tokens: int = 100) -> str:
    """Compatibility wrapper used by pipelines to request model responses."""
    # Use infer under the hood; respect max_tokens by passing in as option via system
    # (the underlying infer implementations already use MAX_TOKENS settings)
    try:
        return await infer(prompt)
    except Exception as e:
        raise


async def _ollama_infer(prompt: str, system: str) -> str:
    messages = []
    if system:
        messages.append({'role': 'system', 'content': system})
    messages.append({'role': 'user', 'content': prompt})

    start = time.monotonic()
    async with httpx.AsyncClient(timeout=45.0) as client:
        response = await client.post(
            f'{OLLAMA_BASE_URL}/api/chat',
            json={
                'model': OLLAMA_MODEL,
                'messages': messages,
                'stream': False,
                'options': {
                    'temperature': TEMPERATURE,
                    'num_predict': MAX_TOKENS,
                },
            },
        )
        response.raise_for_status()
        content = response.json()['message']['content'].strip()
        logger.info('ollama_infer ok duration_ms=%s', int((time.monotonic() - start) * 1000))
        return content


async def _groq_infer(prompt: str, system: str) -> str:
    messages = []
    if system:
        messages.append({'role': 'system', 'content': system})
    messages.append({'role': 'user', 'content': prompt})

    start = time.monotonic()
    async with httpx.AsyncClient(timeout=45.0) as client:
        response = await client.post(
            'https://api.groq.com/openai/v1/chat/completions',
            headers={
                'Authorization': f'Bearer {GROQ_API_KEY}',
                'Content-Type': 'application/json',
            },
            json={
                'model': GROQ_MODEL,
                'messages': messages,
                'max_tokens': MAX_TOKENS,
                'temperature': TEMPERATURE,
            },
        )
        response.raise_for_status()
        content = response.json()['choices'][0]['message']['content'].strip()
        logger.info('groq_infer ok duration_ms=%s', int((time.monotonic() - start) * 1000))
        return content
