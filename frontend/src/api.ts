import type { Schema } from "./types";

async function readSchema(response: Response): Promise<Schema> {
  if (response.ok) {
    return (await response.json()) as Schema;
  }
  const body = await response.json().catch(() => null);
  const detail = typeof body?.detail === "string" ? body.detail : null;
  throw new Error(detail ?? `Request failed (${response.status})`);
}

export async function loadDemo(): Promise<Schema> {
  return readSchema(await fetch("/api/demo"));
}

export async function inspectFile(file: File): Promise<Schema> {
  const form = new FormData();
  form.append("file", file);
  return readSchema(await fetch("/api/inspect", { method: "POST", body: form }));
}
