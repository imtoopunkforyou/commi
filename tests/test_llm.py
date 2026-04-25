"""Tests for llm helpers."""

import pytest
from _pytest.monkeypatch import MonkeyPatch

import commi.llm as llm_module

EXPECTED_N_CTX = llm_module.N_CTX


class _FakeLlama:
    """Simple fake llama class."""

    def __init__(self, model_path: str, *, verbose: bool, n_ctx: int) -> None:
        assert model_path.endswith('commi_model.gguf')
        assert verbose is False
        assert n_ctx == EXPECTED_N_CTX

    def create_completion(self, **_: object) -> dict[str, object]:
        return {
            'choices': [
                {
                    'text': 'feat: add commit title generation\nextra text',
                },
            ],
        }


def test_generate_commit_message_uses_mocked_llm(
    monkeypatch: MonkeyPatch,
) -> None:
    """Generated message should be sanitized to one line."""
    monkeypatch.setattr(llm_module, 'Llama', _FakeLlama)

    message = llm_module.generate_commit_message(
        diff='diff --git a/a.py b/a.py',
        model_path='/model/commi_model.gguf',
    )

    assert message == 'feat: add commit title generation'


def test_generate_commit_message_fails_on_empty_content(
    monkeypatch: MonkeyPatch,
) -> None:
    """Should fail when model returns empty content."""

    class _EmptyContentLlama(_FakeLlama):
        def create_completion(self, **_: object) -> dict[str, object]:
            return {'choices': [{'text': '   '}]}

    monkeypatch.setattr(llm_module, 'Llama', _EmptyContentLlama)

    with pytest.raises(llm_module.LlmError, match='empty'):
        llm_module.generate_commit_message(
            diff='diff --git a/a.py b/a.py',
            model_path='/model/commi_model.gguf',
        )


def test_generate_commit_message_normalizes_output(
    monkeypatch: MonkeyPatch,
) -> None:
    """Should normalize valid output to strict one-line format."""

    class _NoisyLlama(_FakeLlama):
        def create_completion(self, **_: object) -> dict[str, object]:
            return {
                'choices': [
                    {
                        'text': (
                            'Commit message: Fix: Correct    issue!!!\nExtra'
                        ),
                    },
                ],
            }

    monkeypatch.setattr(llm_module, 'Llama', _NoisyLlama)

    message = llm_module.generate_commit_message(
        diff='diff --git a/a.py b/a.py',
        model_path='/model/commi_model.gguf',
    )

    assert message == 'fix: correct issue'


def test_generate_commit_message_keeps_unknown_commit_type(
    monkeypatch: MonkeyPatch,
) -> None:
    """Should keep the model output when the type is not in a fixed allowlist."""

    class _UnknownTypeLlama(_FakeLlama):
        def create_completion(self, **_: object) -> dict[str, object]:
            return {'choices': [{'text': 'improve: make code better'}]}

    monkeypatch.setattr(llm_module, 'Llama', _UnknownTypeLlama)

    message = llm_module.generate_commit_message(
        diff='diff --git a/a.py b/a.py',
        model_path='/model/commi_model.gguf',
    )

    assert message == 'improve: make code better'
