import { execFile } from "node:child_process";
import { promisify } from "node:util";

const execFileAsync = promisify(execFile);

function runGit(
  cwd: string,
  args: readonly string[]
): Promise<{ stdout: string; stderr: string }> {
  return execFileAsync("git", [...args], {
    cwd,
    encoding: "utf8",
    maxBuffer: 1024 * 1024 * 512
  });
}

export async function isInsideGitRepository(cwd: string): Promise<boolean> {
  try {
    const { stdout } = await runGit(cwd, [
      "rev-parse",
      "--is-inside-work-tree"
    ]);
    return stdout.trim() === "true";
  } catch {
    return false;
  }
}

export async function getStagedDiff(cwd: string): Promise<string> {
  const { stdout } = await runGit(cwd, [
    "diff",
    "--cached",
    "--no-ext-diff"
  ]);
  return stdout;
}

export async function createCommit(
  cwd: string,
  message: string
): Promise<void> {
  await runGit(cwd, ["commit", "-m", message]);
}
