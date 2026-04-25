import { homedir } from "node:os";
import { join } from "node:path";
import { createCommit, getStagedDiff, isInsideGitRepository } from "./git.js";
import {
  assertModelFileReadable,
  generateCommitMessageWithLlamaCpp
} from "./llm.js";
import { buildCommitPrompt } from "./prompt.js";
import {
  extractCommitMessageFromModelOutput,
  fallbackCommitMessage,
  sanitizeCommitMessage
} from "./message.js";

const modelPath = join(homedir(), ".config", "commi", "commi_model.gguf");

async function main(): Promise<void> {
  const cwd = process.cwd();

  if (!(await isInsideGitRepository(cwd))) {
    console.error("commi: not a git repository (or git failed).");
    process.exitCode = 1;
    return;
  }

  const stagedDiff = await getStagedDiff(cwd);
  if (stagedDiff.trim().length === 0) {
    console.error(
      "commi: nothing to commit — staged diff is empty. Run git add first."
    );
    process.exitCode = 1;
    return;
  }

  await assertModelFileReadable(modelPath);

  const prompt = buildCommitPrompt(stagedDiff);
  const rawStdout = await generateCommitMessageWithLlamaCpp(modelPath, prompt);
  const extracted = extractCommitMessageFromModelOutput(rawStdout);
  let message = sanitizeCommitMessage(extracted);
  if (message.length === 0) {
    message = fallbackCommitMessage();
  }

  await createCommit(cwd, message);
  console.log(
    `The commit was created successfully with the message "${message}"`
  );
}

void main().catch((err: unknown) => {
  if (err instanceof Error) {
    console.error(`commi: ${err.message}`);
  } else {
    console.error("commi: unexpected error");
  }
  process.exitCode = 1;
});
