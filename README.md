# commi

CLI that creates a git commit from your **staged** changes, using a **local** GGUF model and [llama.cpp](https://github.com/ggml-org/llama.cpp) (`llama-cli`). Nothing runs in the background: each `commi` invocation starts `llama-cli`, generates one line, then exits.


# ⚠️ Attention
- In development.  
- May not work as you expect and may cause errors.

## draft
model: https://huggingface.co/Tavernari/git-commit-message
llama: https://github.com/ggml-org/llama.cpp
