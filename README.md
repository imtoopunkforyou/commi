# commi

CLI that creates a git commit from your **staged** changes, using a **local** GGUF model and [llama.cpp](https://github.com/ggml-org/llama.cpp) (`llama-cli`). Nothing runs in the background: each `commi` invocation starts `llama-cli`, generates one line, then exits.


# ⚠️ Attention
- In development.  
- May not work as you expect and may cause errors.

## Requirements

- Node.js 18+
- `git` on your `PATH`
- `llama-cli` from llama.cpp on your `PATH` (or set `COMMI_LLAMA_CLI` to the full path of the binary)
- Model file at:

  `~/.config/commi/commi_model.gguf`

Loading a GGUF can take noticeable time on the first run of a session; `commi` still exits as soon as `llama-cli` finishes.

## Install

From npm (after publish):

```bash
npm install -g commi
```

From a clone:

```bash
npm install
npm run build
npm link
```

## Usage

```bash
git add .
commi
```

Example:

```text
The commit was created successfully with the message "fix: handle empty input"
```

`commi` reads the full staged diff (`git diff --cached --no-ext-diff`) and sends it to the model. It does **not** truncate the diff. If the prompt does not fit the model context, the command fails with a clear message; split your staged changes into smaller commits or use a setup with a larger context window.

## Environment

| Variable | Meaning |
| --- | --- |
| `COMMI_LLAMA_CLI` | Path to the `llama-cli` binary if it is not on `PATH` |

## Status

In development. May not behave as you expect.
model: https://huggingface.co/Tavernari/git-commit-message
