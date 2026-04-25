"""Project constants."""

from pathlib import Path

MODEL_PATH = Path('~/.config/commi/commi_model.gguf').expanduser()
PROMT = Path(__file__).parent / 'PROMT.md'
