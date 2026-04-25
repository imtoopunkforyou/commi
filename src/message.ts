function stripWrappingQuotes(line: string): string {
  let s = line.trim();
  if (
    (s.startsWith('"') && s.endsWith('"')) ||
    (s.startsWith("'") && s.endsWith("'"))
  ) {
    s = s.slice(1, -1).trim();
  }
  if (s.startsWith("`") && s.endsWith("`")) {
    s = s.slice(1, -1).trim();
  }
  return s;
}

export function extractCommitMessageFromModelOutput(stdout: string): string {
  const lines = stdout
    .replace(/\r\n/g, "\n")
    .split("\n")
    .map((l) => l.trim())
    .filter((l) => l.length > 0);

  const conventional = /^(feat|fix|docs|style|refactor|perf|test|chore|build|ci)(\([^)]*\))?!?:\s+.+/i;

  for (let i = lines.length - 1; i >= 0; i--) {
    const line = lines[i];
    if (line === undefined) {
      continue;
    }
    if (conventional.test(line)) {
      return line;
    }
  }

  for (let i = lines.length - 1; i >= 0; i--) {
    const line = lines[i];
    if (line === undefined) {
      continue;
    }
    if (line.includes(":") && line.length <= 240) {
      return line;
    }
  }

  const last = lines.at(-1);
  return last ?? "";
}

export function sanitizeCommitMessage(raw: string): string {
  const firstLine = raw
    .replace(/\r\n/g, "\n")
    .split("\n")
    .map((l) => l.trim())
    .find((l) => l.length > 0);

  if (!firstLine) {
    return "";
  }

  let msg = stripWrappingQuotes(firstLine);
  msg = msg.replace(/\s+/g, " ").trim();

  if (msg.length > 240) {
    msg = msg.slice(0, 240).trimEnd();
  }

  return msg;
}

export function fallbackCommitMessage(): string {
  return "chore: update staged changes";
}
