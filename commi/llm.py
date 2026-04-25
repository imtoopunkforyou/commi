"""LLM integration based on llama-cpp-python."""

import re
from pathlib import Path
from typing import Any, cast

from llama_cpp import Llama

from commi.execptions import LlmError

N_CTX = 4_096
MAX_TOKENS = 64
TEMPERATURE = 0
DEFAULT_COMMIT_MESSAGE = 'chore: update files'
COMMIT_MESSAGE_PATTERN = re.compile(
    r'^(feat|fix|refactor|docs|test|chore|perf|build|ci|style): '
    r'[a-z0-9][a-z0-9 -]{1,57}[a-z0-9]$'
)
MAX_COMMIT_MESSAGE_LENGTH = 60


def _read_system_prompt() -> str:
    prompt_path = Path(__file__).resolve().parent / 'PROMT.md'
    prompt_lines = prompt_path.read_text(encoding='utf-8').splitlines()
    content_lines = [
        line for line in prompt_lines if line and not line.startswith('#')
    ]
    return '\n'.join(content_lines).strip()


def _build_prompt(diff: str) -> str:
    system_prompt = _read_system_prompt()
    return f'{system_prompt}\n\nGit diff:\n\n{diff}\n\n'


def _prepare_diff(diff: str, max_diff_chars: int) -> str:
    if len(diff) <= max_diff_chars:
        return diff
    return diff[-max_diff_chars:]


def _attempt_completion(llm: Llama, diff: str, max_diff_chars: int) -> object:
    return llm.create_completion(
        prompt=_build_prompt(_prepare_diff(diff, max_diff_chars)),
        max_tokens=MAX_TOKENS,
        temperature=TEMPERATURE,
    )


def _request_completion(
    llm: Llama,
    diff: str,
    limits: tuple[int, ...] = (12_000, 8_000, 4_000, 2_000),
) -> object:
    max_diff_chars = limits[0]
    try:
        return _attempt_completion(
            llm=llm, diff=diff, max_diff_chars=max_diff_chars
        )
    except Exception as error:  # pragma: no cover
        if (
            len(limits) == 1
            or 'exceed context window' not in str(error).lower()
        ):
            raise LlmError.generation_failed(str(error)) from error
    return _request_completion(llm=llm, diff=diff, limits=limits[1:])


def _extract_message(response: dict[str, Any]) -> str:
    try:
        message = response['choices'][0]['text']
    except (KeyError, IndexError, TypeError) as error:
        raise LlmError.invalid_response() from error
    if not isinstance(message, str):
        raise LlmError.invalid_response()
    lines = message.splitlines()
    non_empty_lines = [line for line in lines if line.strip()]
    first_line = non_empty_lines[0] if non_empty_lines else ''
    normalized = first_line.strip().strip('"\'`').strip()
    if normalized.lower().startswith('commit message:'):
        normalized = normalized.split(':', maxsplit=1)[1].strip()
    if not normalized:
        raise LlmError.empty_message()
    return _normalize_commit_message(normalized)


def _normalize_commit_message(message: str) -> str:
    text = ' '.join(message.split())
    text = text.strip('"\'`').strip()
    text = text.rstrip('.,;!?')
    text = text.lower()

    if ':' not in text:
        return DEFAULT_COMMIT_MESSAGE

    commit_type, summary = text.split(':', maxsplit=1)
    commit_type = commit_type.strip()
    summary = summary.strip()

    allowed_types = {
        'feat',
        'fix',
        'refactor',
        'docs',
        'test',
        'chore',
        'perf',
        'build',
        'ci',
        'style',
    }
    if commit_type not in allowed_types:
        return DEFAULT_COMMIT_MESSAGE

    # Keep only characters allowed by the strict validation regex.
    summary = re.sub(r'[^a-z0-9 -]+', '', summary)
    summary = ' '.join(summary.split()).strip('- ').strip()

    candidate = f'{commit_type}: {summary}'
    if len(candidate) > MAX_COMMIT_MESSAGE_LENGTH:
        max_summary_length = MAX_COMMIT_MESSAGE_LENGTH - len(commit_type) - 2
        summary = summary[:max_summary_length].rstrip(' -')
        candidate = f'{commit_type}: {summary}'

    if COMMIT_MESSAGE_PATTERN.fullmatch(candidate):
        return candidate

    return DEFAULT_COMMIT_MESSAGE


def generate_commit_message(diff: str, model_path: str) -> str:
    """Generate commit message from staged diff."""
    if not diff:
        raise LlmError.empty_diff()

    llm = Llama(model_path=model_path, verbose=False, n_ctx=N_CTX)
    response_raw = _request_completion(llm=llm, diff=diff)

    if not isinstance(response_raw, dict):
        raise LlmError.invalid_response()
    response = cast('dict[str, Any]', response_raw)

    return _extract_message(response)
