"""Typer CLI entrypoint."""

from pathlib import Path
from typing import NoReturn

import typer

from commi.constants import MODEL_PATH
from commi.exceptions import CommiRunError, GitError, LlmError
from commi.git_utils import create_commit, read_staged_diff
from commi.llm import generate_commit_message

app = typer.Typer(add_completion=False)


def _raise_error(message: str) -> NoReturn:
    raise CommiRunError(message)


def _resolve_model_path() -> Path:
    model_path = MODEL_PATH
    if not model_path.exists():
        _raise_error(f'Model was not found at {model_path}.')
    return model_path


def _run_once() -> str:
    diff = read_staged_diff()
    if not diff:
        _raise_error('No staged changes found. Run `git add .` first.')
    model_path = _resolve_model_path()
    message = generate_commit_message(diff=diff, model_path=str(model_path))
    create_commit(message=message)
    return message


@app.command()
def run() -> None:
    """Create commit message from staged diff and commit changes."""
    try:
        message = _run_once()
    except (CommiRunError, GitError, LlmError) as error:
        typer.echo(f'Error: {error}')
        raise typer.Exit(code=1) from error

    typer.echo(
        f'The commit was created successfully with the message "{message}"'
    )


def main() -> None:
    """Run CLI app."""
    app()
