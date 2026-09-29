import { test } from "node:test"
import assert from "node:assert/strict"
import { readFile, rm, writeFile } from "node:fs/promises"
import { handleRetry, isFreeTierLimit, resolveConfig } from "./index.js"

const FREE = { providerID: "opencode", id: "muse-spark-1.3-contributor-free" }
const PAID = { providerID: "anthropic", id: "paid-model" }
const TMP = "/tmp/rlr-test-metrics.jsonl"

test("exact log shape on free model is rescued with 30s delay", async () => {
  await rm(TMP, { force: true })
  const event = {
    error: { message: "Rate limit exceeded. Please try again later." },
    attempt: 1,
    sessionID: "s1",
    model: FREE,
  }
  assert.equal(await handleRetry(event, { command: "echo rotated", metricsPath: TMP }), "rescued")
  assert.equal(event.decision.delay, 30_000)
  const line = JSON.parse(await readFile(TMP, "utf8"))
  assert.equal(line.modelID, FREE.id)
  assert.equal(line.retryDelayMs, 30_000)
  assert.equal(line.commandOk, true)
})

test("wrapped cause chain is detected", async () => {
  const event = {
    error: { message: "drain failed", cause: { name: "AI.Error.QuotaExceeded", message: "Rate limit exceeded" } },
    attempt: 2,
    sessionID: "s2",
    model: FREE,
  }
  assert.equal(await handleRetry(event, { command: "echo ok", metricsPath: TMP }), "rescued")
})

test("non-429 error passes untouched", async () => {
  const event = { error: { status: 500, message: "boom" }, attempt: 1, model: FREE }
  assert.equal(await handleRetry(event, {}), "pass")
  assert.equal(event.decision, undefined)
})

test("paid model 429 passes untouched", async () => {
  const event = { error: { status: 429, message: "Rate limit exceeded" }, attempt: 1, model: PAID }
  assert.equal(await handleRetry(event, {}), "pass")
})

test("command failure still sets the 30s decision", async () => {
  const event = {
    error: { status: 429, message: "free tier quota hit" },
    attempt: 1,
    sessionID: "s3",
    model: FREE,
  }
  assert.equal(await handleRetry(event, { command: "false", metricsPath: TMP }), "rescued")
  assert.equal(event.decision.delay, 30_000)
})

test("unwritable metrics path still sets the 30s decision", async (t) => {
  // A regular file as parent dir fails fast (ENOTDIR). NOTE: never use /proc
  // here — recursive mkdir under /proc hangs at kernel level (found 2026-09-29).
  const parent = "/tmp/rlr-parent-file"
  await writeFile(parent, "x")
  const event = {
    error: { status: 429, message: "free tier quota hit" },
    attempt: 1,
    sessionID: "s4",
    model: FREE,
  }
  assert.equal(await handleRetry(event, { command: "echo ok", metricsPath: `${parent}/child.jsonl` }), "rescued")
  assert.equal(event.decision.delay, 30_000)
})

test("env overrides resolve", () => {
  process.env.RATE_LIMIT_COMMAND = "my-cmd --flag"
  process.env.RATE_LIMIT_METRICS = "/tmp/custom.jsonl"
  const cfg = resolveConfig({})
  assert.equal(cfg.command, "my-cmd --flag")
  assert.equal(cfg.metricsPath, "/tmp/custom.jsonl")
  delete process.env.RATE_LIMIT_COMMAND
  delete process.env.RATE_LIMIT_METRICS
})

test("bare exceeded without rate words does not match", () => {
  assert.equal(isFreeTierLimit({ message: "threshold exceeded" }, FREE), false)
})

test("null event passes without throwing", async () => {
  assert.equal(await handleRetry(null, {}), "pass")
})

test("empty env falls back to defaults", () => {
  process.env.RATE_LIMIT_COMMAND = ""
  const cfg = resolveConfig({})
  assert.match(cfg.command, /rr$/)
  delete process.env.RATE_LIMIT_COMMAND
})

test("ECONNRESET transport fault is rescued with kind=transport", async () => {
  const event = {
    error: { message: "Opencode failed to send message with error: ECONNRESET: The socket connection was closed unexpectedly. For more information, pass `verbose: true` in the second argument to fetch()" },
    attempt: 1,
    sessionID: "st",
    model: FREE,
  }
  assert.equal(await handleRetry(event, { command: "echo rotated", metricsPath: "/tmp/rlr-t.jsonl" }), "rescued")
  assert.equal(event.decision.delay, 30_000)
  const line = JSON.parse(await readFile("/tmp/rlr-t.jsonl", "utf8"))
  assert.equal(line.kind, "transport")
})
