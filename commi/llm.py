"""LLM integration based on llama-cpp-python."""

from typing import Any, cast

from llama_cpp import Llama

from commi.execptions import LlmError

SYSTEM_PROMPT = (
    'You are a helpful assistant that writes git commit messages. '
    'Return only one short commit message in Conventional Commits style. '
    'No quotes, no markdown, no explanations.'
)
N_CTX = 4_096
MAX_TOKENS = 64
TEMPERATURE = 0


def _build_prompt(diff: str) -> str:
    return f'{SYSTEM_PROMPT}\n\nGit diff:\n\n{diff}\n\nCommit message:'


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
    return normalized


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
