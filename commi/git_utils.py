"""Git-related operations."""

from typing import cast

from git import Repo
from git.exc import GitCommandError, InvalidGitRepositoryError


class GitError(Exception):
    """Base git error."""


class GitRepositoryNotFoundError(GitError):
    """Raised when current directory is not a git repository."""

    def __init__(self) -> None:
        """Set predefined error message."""
        super().__init__('Current directory is not a git repository.')


class GitDiffReadError(GitError):
    """Raised when staged diff cannot be read."""

    def __init__(self) -> None:
        """Set predefined error message."""
        super().__init__('Failed to read staged diff.')


class GitCommitCreateError(GitError):
    """Raised when commit cannot be created."""

    def __init__(self) -> None:
        """Set predefined error message."""
        super().__init__('Failed to create commit.')


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
