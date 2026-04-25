# commi

CLI that creates a git commit from your **staged** changes, using a
**local** GGUF model via
[llama-cpp-python](https://github.com/abetlen/llama-cpp-python).
Nothing runs in the background: each `commi` invocation loads the model,
generates one line, and exits.

## Requirements

- Python 3.10+
- Local model at `~/.config/commi/commi_model.gguf`

## Usage

```bash
git add .
poetry run commi
```

Example output:

```text
The commit was created successfully with the message "fix: some bug"
```

## Attention

- In development.  
- May not work as you expect and may cause errors.

## draft

- model: [Tavernari/git-commit-message](https://huggingface.co/Tavernari/git-commit-message)
- llama: [ggml-org/llama.cpp](https://github.com/ggml-org/llama.cpp)
