"""Git-related operations."""

from typing import cast

from git import Repo
from git.exc import GitCommandError, InvalidGitRepositoryError

from commi.exceptions import (
    GitCommitCreateError,
    GitDiffReadError,
    GitRepositoryNotFoundError,
)


def _open_repo() -> Repo:
    try:
        return Repo(search_parent_directories=True)
    except InvalidGitRepositoryError as error:
        raise GitRepositoryNotFoundError from error


def read_staged_diff() -> str:
    """Return staged git diff only."""
    repo = _open_repo()
    try:
        staged_diff = cast('str', repo.git.diff('--cached'))
        return staged_diff.strip()
    except GitCommandError as error:
        raise GitDiffReadError from error


def create_commit(message: str) -> None:
    """Create git commit with provided message."""
    repo = _open_repo()
    try:
        repo.index.commit(message=message)
    except GitCommandError as error:
        raise GitCommitCreateError from error
