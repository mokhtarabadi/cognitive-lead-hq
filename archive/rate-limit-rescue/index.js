import { execFile } from "node:child_process"
import { appendFile, mkdir } from "node:fs/promises"
import { dirname } from "node:path"
import { homedir } from "node:os"

// The server loader sometimes cannot resolve @opencode/plugin from a
// path-installed plugin dir (observed: "Cannot find package"). Fall back
// to a passthrough shape — Plugin.define tags {id, setup}, nothing more.
let Plugin
try {
  ;({ Plugin } = await import("@opencode/plugin"))
} catch {
  Plugin = { define: (d) => d }
}

// Free-tier 429 rescue (Task 282). SCOPE: free-tier rate limits ONLY.
// Every other error passes through untouched.
const RETRY_DELAY_MS = 2_000

// Attempt ceiling: the engine gives up after 5 retries, but forcing
// retry:true extends the run (observed attempt 11 in production). Cap
// forced rescues per session so a dead endpoint cannot loop forever.
const MAX_RESCUES_PER_SESSION = 10
const rescueCounts = new Map()

export function resetRescueCounts() {
  rescueCounts.clear()
}

export function isFreeTierLimit(error, model) {
  if (!error) return false
  // Ground truth (opencode.log 2026-09-26): "AI.Error: Rate limit exceeded.
  // Please try again later." with cause "AI.Error.QuotaExceeded: ..." — no
  // HTTP status and no free/tier words in the text. Scope comes from the
  // model id (e.g. muse-spark-1.3-contributor-free), not the message.
  // The cause chain is walked so wrapped quota errors are not missed.
  let chain = ""
  for (let e = error, depth = 0; e && depth < 4; depth++) {
    chain += ` ${e.message ?? ""} ${e.type ?? ""} ${e.code ?? ""} ${e.name ?? ""}`
    e = e.cause
  }
  const hay = chain.toLowerCase()
  const rateish = error.status === 429 || /429|rate.?limit|quota/.test(hay)
  if (!rateish) return false
  const mid = `${model?.providerID ?? ""} ${model?.id ?? ""}`.toLowerCase()
  return mid.includes("free") || mid.includes("contributor") || /free|tier/.test(hay)
}

// Transient transport failures (explicit Manager order 2026-09-29): e.g.
// "ECONNRESET: The socket connection was closed unexpectedly". These are
// network faults, not quota — rr recovery is the fix, same 2s retry.
export function isTransportFault(error) {
  if (!error) return false
  const hay = `${error.message ?? ""} ${error.type ?? ""} ${error.code ?? ""} ${error.name ?? ""}`.toLowerCase()
  return /econnreset|socket hang up|etimedout|epipe|socket connection was closed|network socket/.test(hay)
}

export function reasonSuffix(command, kind) {
  // The bundled rr wrapper defaults bare invocation to `next`, but an
  // explicit subcommand is required once flags are appended. Custom
  // commands that already name their own subcommand only get the flag.
  const bin = String(command || "").trim().split(/\s+/)[0] || ""
  const base = bin.split("/").pop() || ""
  const needsSub = /^(rr|rr_balancer\.py)$/.test(base);
  return (needsSub ? " next" : "") + " --reason " + kind
}

export function resolveConfig(options) {
  const rawMax = options?.maxRescues ?? process.env.RATE_LIMIT_MAX_RESCUES ?? MAX_RESCUES_PER_SESSION
  const parsedMax = Number(rawMax)
  return {
    command: options?.command || process.env.RATE_LIMIT_COMMAND || `${homedir()}/.local/bin/rr`,
    metricsPath:
      options?.metricsPath ||
      process.env.RATE_LIMIT_METRICS ||
      `${homedir()}/.local/share/opencode/ratelimit-metrics.jsonl`,
    maxRescues:
      Number.isFinite(parsedMax) && parsedMax > 0 ? Math.floor(parsedMax) : MAX_RESCUES_PER_SESSION,
  }
}

export async function runCommand(command) {
  const [bin, ...args] = command.split(/\s+/).filter(Boolean)
  return new Promise((resolve) => {
    execFile(bin, args, { timeout: 60_000 }, (err, stdout, stderr) => {
      resolve({ ok: !err, code: err?.code ?? 0, stdout: String(stdout ?? "").slice(0, 500), stderr: String(stderr ?? "").slice(0, 500) })
    })
  })
}

export async function appendMetrics(path, record) {
  await mkdir(dirname(path), { recursive: true })
  await appendFile(path, JSON.stringify(record) + "\n", "utf8")
}

export async function handleRetry(event, options) {
  const quota = isFreeTierLimit(event?.error, event?.model)
  const transport = !quota && isTransportFault(event?.error)
  if (!quota && !transport) return "pass"
  const cfg = resolveConfig(options)
  // Attempt ceiling: stop forcing retries past maxRescues per session so a
  // dead endpoint ends instead of looping. No decision is set, so the engine
  // applies its own give-up policy. The capped hit is still logged.
  const sessionKey = event?.sessionID ?? ""
  if (sessionKey) {
    const count = (rescueCounts.get(sessionKey) ?? 0) + 1
    rescueCounts.set(sessionKey, count)
    if (rescueCounts.size > 1000) rescueCounts.delete(rescueCounts.keys().next().value)
    if (count > cfg.maxRescues) {
      try {
        await appendMetrics(cfg.metricsPath, {
          ts: new Date().toISOString(),
          kind: quota ? "quota" : "transport",
          capped: true,
          sessionID: event.sessionID,
          providerID: event.model?.providerID,
          modelID: event.model?.id,
          attempt: event.attempt,
          command: cfg.command,
          retryDelayMs: null,
        })
      } catch {
        // metrics are best-effort
      }
      return "capped"
    }
  }
  // Never let observability break the retry: command/metrics failures are
  // recorded but the 2s decision is always set on a free-tier match.
  const reason = quota ? "quota" : "transport"
  const finalCommand = cfg.command + reasonSuffix(cfg.command, reason)
  let cmdResult = { ok: false, code: -1, stdout: "", stderr: "hook-guard" }
  try {
    cmdResult = await runCommand(finalCommand)
  } catch (err) {
    cmdResult = { ok: false, code: -1, stdout: "", stderr: String(err?.message ?? err).slice(0, 200) }
  }
  try {
    await appendMetrics(cfg.metricsPath, {
      ts: new Date().toISOString(),
      kind: quota ? "quota" : "transport",
      sessionID: event.sessionID,
      providerID: event.model?.providerID,
      modelID: event.model?.id,
      status: event.error.status ?? null,
      // Full error shape (truncated) so quota numbers can be compared
      // against OpenCode's own accounting later.
      errorKeys: Object.keys(event.error ?? {}),
      errorType: event.error?.type ?? event.error?.name ?? null,
      errorCode: event.error?.code ?? null,
      message: String(event.error.message ?? "").slice(0, 300),
      attempt: event.attempt,
      proposedDelayMs: event.decision?.delay ?? null,
      command: finalCommand,
      commandOk: cmdResult.ok,
      commandCode: cmdResult.code,
      commandOut: cmdResult.stdout,
      retryDelayMs: RETRY_DELAY_MS,
    })
  } catch {
    // metrics are best-effort; the retry decision below still applies
  }
  event.decision = { retry: true, delay: RETRY_DELAY_MS }
  return "rescued"
}

export default Plugin.define({
  id: "rate-limit-rescue",
  async setup(ctx) {
    const options = ctx.options ?? {}
    await ctx.session.hook("retry", async (event) => {
      await handleRetry(event, options)
    })
  },
})
