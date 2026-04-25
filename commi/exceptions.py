"""Project exceptions."""

from types import MappingProxyType


class CommiRunError(Exception):
    """Raised when CLI run fails."""


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


ERROR_MESSAGES = MappingProxyType(
    {
        'empty_diff': 'Diff is empty.',
        'generation_failed': 'Failed to generate commit message.',
        'invalid_response': 'LLM returned invalid response.',
        'empty_message': 'Generated commit message is empty.',
    },
)


class LlmError(Exception):
    """Raised when LLM generation fails."""

    def __init__(self, error_key: str, detail: str = '') -> None:
        """Set normalized error message by key."""
        message = ERROR_MESSAGES[error_key]
        if detail:
            message = f'{message} Details: {detail}'
        super().__init__(message)

    @classmethod
    def invalid_response(cls) -> 'LlmError':
        """Create invalid response error."""
        return cls('invalid_response')

    @classmethod
    def empty_message(cls) -> 'LlmError':
        """Create empty message error."""
        return cls('empty_message')

    @classmethod
    def empty_diff(cls) -> 'LlmError':
        """Create empty diff error."""
        return cls('empty_diff')

    @classmethod
    def generation_failed(cls, detail: str) -> 'LlmError':
        """Create generation failed error."""
        return cls('generation_failed', detail)
