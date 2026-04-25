export function buildCommitPrompt(stagedDiff: string): string {
  return [
    "You are a tool that writes a single git commit message.",
    "",
    "Rules:",
    "- Output exactly one line.",
    "- No quotes, no markdown, no backticks, no explanations.",
    "- Prefer Conventional Commits style: type(scope): short description",
    "- Types include: feat, fix, docs, style, refactor, perf, test, chore, build, ci.",
    "If unsure, use chore.",
    "",
    "Staged diff (git diff --cached):",
    "",
    stagedDiff
  ].join("\n");
}
