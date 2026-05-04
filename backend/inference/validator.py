from __future__ import annotations

from collections.abc import Callable
import logging

from config import MAX_RETRIES
from inference.client import infer

logger = logging.getLogger(__name__)


def _preview(text: str, limit: int = 200) -> str:
    return (text[:limit] + '...') if len(text) > limit else text


async def validated_infer(
    prompt: str,
    whitelist: set[str],
    system: str = '',
    max_retries: int = MAX_RETRIES,
    transform: Callable[[str], str] = lambda x: x.strip().upper(),
) -> tuple[str, int]:
    current_prompt = prompt
    raw = ''
    for attempt in range(1, max_retries + 1):
        logger.info('validated_infer attempt=%s', attempt)
        raw = await infer(current_prompt, system)
        result = transform(raw)
        
        # Check if the result directly matches or contains a whitelist word
        if result in whitelist:
            logger.info('validated_infer accepted direct=%s raw=%s', result, _preview(raw))
            return result, attempt
        
        matches = [w for w in whitelist if w in result]
        if len(matches) == 1:
            logger.info('validated_infer accepted contains=%s raw=%s', matches[0], _preview(raw))
            return matches[0], attempt

        logger.warning(
            'validated_infer retrying raw=%s result=%s whitelist=%s',
            _preview(raw),
            result,
            sorted(whitelist),
        )
        valid_options = ' / '.join(sorted(whitelist))
        current_prompt = (
            f'{prompt}\n\n'
            f"[Your previous response was: '{raw}']\n"
            f'[That is not valid. You must respond with ONLY one of: {valid_options}]\n'
            'Try again. One word only.'
        )

    return 'UNRESOLVED', max_retries


async def validated_infer_with_raw(
    prompt: str,
    whitelist: set[str],
    system: str = '',
    max_retries: int = MAX_RETRIES,
    transform: Callable[[str], str] = lambda x: x.strip().upper(),
) -> tuple[str, int, str]:
    current_prompt = prompt
    raw = ''
    for attempt in range(1, max_retries + 1):
        logger.info('validated_infer_with_raw attempt=%s', attempt)
        raw = await infer(current_prompt, system)
        result = transform(raw)
        if result in whitelist:
            logger.info('validated_infer_with_raw accepted direct=%s raw=%s', result, _preview(raw))
            return result, attempt, raw

        matches = [w for w in whitelist if w in result]
        if len(matches) == 1:
            logger.info('validated_infer_with_raw accepted contains=%s raw=%s', matches[0], _preview(raw))
            return matches[0], attempt, raw

        valid_options = ' / '.join(sorted(whitelist))
        current_prompt = (
            f'{prompt}\n\n'
            f"[Your previous response was: '{raw}']\n"
            f'[That is not valid. You must respond with ONLY one of: {valid_options}]\n'
            'Try again. One word only.'
        )

    return 'UNRESOLVED', max_retries, raw


async def length_gated_infer(
    prompt: str,
    max_words: int,
    system: str = '',
    max_retries: int = MAX_RETRIES,
) -> tuple[str, int]:
    current_prompt = prompt
    raw = ''
    for attempt in range(1, max_retries + 1):
        logger.info('length_gated_infer attempt=%s', attempt)
        raw = await infer(current_prompt, system)
        if len(raw.split()) <= max_words:
            logger.info('length_gated_infer accepted words=%s', len(raw.split()))
            return raw.strip(), attempt

        current_prompt = (
            f'{prompt}\n\n'
            f'[Your response was {len(raw.split())} words. Maximum allowed: {max_words} words.]\n'
            '[Remove the least important part and try again.]'
        )

    words = raw.split()
    logger.warning('length_gated_infer failed words=%s max_words=%s', len(words), max_words)
    return ' '.join(words[:max_words]) + ('...' if len(words) > max_words else ''), max_retries
