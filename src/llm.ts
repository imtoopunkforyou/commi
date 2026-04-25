import { access, mkdtemp, rm, writeFile } from "node:fs/promises";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { spawn } from "node:child_process";
import { constants as fsConstants } from "node:fs";

function resolveLlamaExecutable(): string {
  // `process.env` is typed with an index signature; bracket access satisfies TS4111.
  const fromEnv = process.env["COMMI_LLAMA_CLI"]?.trim();
  if (fromEnv !== undefined && fromEnv.length > 0) {
    return fromEnv;
  }
  return "llama-cli";
}

const MAX_STREAM_CHARS = 512 * 1024;

function appendCapped(target: string, chunk: string, maxChars: number): string {
  const next = target + chunk;
  if (next.length <= maxChars) {
    return next;
  }
  return next.slice(next.length - maxChars);
}

function spawnLlama(
  executable: string,
  args: readonly string[]
): Promise<{ code: number | null; stdout: string; stderr: string }> {
  return new Promise((resolve, reject) => {
    const child = spawn(executable, [...args], {
      stdio: ["ignore", "pipe", "pipe"]
    });

    let stdout = "";
    let stderr = "";

    child.stdout.setEncoding("utf8");
    child.stderr.setEncoding("utf8");

    child.stdout.on("data", (chunk: string) => {
      stdout = appendCapped(stdout, chunk, MAX_STREAM_CHARS);
    });
    child.stderr.on("data", (chunk: string) => {
      stderr = appendCapped(stderr, chunk, MAX_STREAM_CHARS);
    });

    child.on("error", (err: unknown) => {
      reject(err instanceof Error ? err : new Error(String(err)));
    });

    child.on("close", (code) => {
      resolve({ code, stdout, stderr });
    });
  });
}

function looksLikeContextExceeded(stderr: string, stdout: string): boolean {
  const haystack = `${stderr}\n${stdout}`.toLowerCase();
  return (
    haystack.includes("exceed context window") ||
    haystack.includes("context size exceeded") ||
    haystack.includes("kv cache") ||
    haystack.includes("failed to parse prompt") ||
    haystack.includes("n_ctx") ||
    haystack.includes("context shift") ||
    haystack.includes("prompt is too long")
  );
}

export async function assertModelFileReadable(
  modelPath: string
): Promise<void> {
  try {
    await access(modelPath, fsConstants.R_OK);
  } catch {
    throw new Error(
      `Model file not found or not readable: ${modelPath}\n` +
        "Place your GGUF at ~/.config/commi/commi_model.gguf"
    );
  }
}

export async function generateCommitMessageWithLlamaCpp(
  modelPath: string,
  prompt: string
): Promise<string> {
  const executable = resolveLlamaExecutable();

  const dir = await mkdtemp(join(tmpdir(), "commi-"));
  const promptFile = join(dir, "prompt.txt");

  try {
    await writeFile(promptFile, prompt, { encoding: "utf8" });

    const args = [
      "-m",
      modelPath,
      "-f",
      promptFile,
      "-no-cnv",
      "--no-display-prompt",
      "--simple-io",
      "-n",
      "128",
      "--log-disable"
    ] as const;

    let result: { code: number | null; stdout: string; stderr: string };

    try {
      result = await spawnLlama(executable, [...args]);
    } catch (err: unknown) {
      if (
        err instanceof Error &&
        "code" in err &&
        (err as NodeJS.ErrnoException).code === "ENOENT"
      ) {
        throw new Error(
          `Cannot run "${executable}". Install llama.cpp and ensure ` +
            '`llama-cli` is on your PATH, or set COMMI_LLAMA_CLI to the binary path.',
          { cause: err }
        );
      }
      throw err;
    }

    if (result.code !== 0) {
      const tail = `${result.stderr}\n${result.stdout}`.trimEnd();
      if (looksLikeContextExceeded(result.stderr, result.stdout)) {
        throw new Error(
          "The staged diff is too large for the model context on this machine.\n" +
            "commi does not truncate diffs. Split your changes into smaller staged commits " +
            "or use a model/hardware setup with a larger context window.\n\n" +
            (tail.length > 0 ? `llama-cli output:\n${tail}\n` : "")
        );
      }

      throw new Error(
        `llama-cli exited with code ${String(result.code)}.\n${tail}`
      );
    }

    return result.stdout;
  } finally {
    await rm(dir, { recursive: true, force: true });
  }
}
