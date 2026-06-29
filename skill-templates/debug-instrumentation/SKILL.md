---
name: debug-instrumentation
description: Mandatory workflow for diagnosing complex bugs, deadlocks, race conditions, and silent failures via strategic logging and tracing.
---

# Debug Instrumentation & Tracing Protocol

You are debugging a complex issue (e.g., deadlock, infinite loop, race condition, or silent failure). Standard static analysis has failed or is insufficient. You MUST gain runtime visibility.

**CRITICAL GUARDRAIL:** Do NOT blindly guess the solution. Do NOT attempt to refactor architectural logic without logs proving where the failure occurs.

## Workflow

### 1. Identify Choke Points

Locate the areas of the codebase relevant to the bug. Look for:

- Mutexes, Locks, or synchronized blocks.
- Database transaction boundaries.
- Asynchronous boundaries (Promises, Coroutines, Goroutines).
- Deeply nested loops or recursive calls.

### 2. Inject Strategic Logs (Instrumentation)

Use the `apply_patch` tool to inject temporary, highly visible logging statements into the code.

- Log _before_ and _after_ acquiring a lock or starting a transaction.
- Log the current thread ID, process ID, or unique request ID.
- Log variable states at the start and end of loops.
- Example: `console.log('[DEBUG-TRACE] Attempting to acquire lock A...');`

### 3. Execution & Capture

Run the application, test suite, or specific reproduction script using your `bash` tool.

- Ensure you capture `stdout` and `stderr`.
- If testing for a deadlock, set a strict timeout on your bash command (e.g., `timeout 10s npm test`) so the agent loop does not hang indefinitely.

### 4. Analyze Runtime Data

Read the captured log output. Look for:

- A "before lock" log that has no matching "after lock" log (Deadlock indicator).
- Logs arriving out of expected sequential order (Race condition indicator).
- Repeating log sequences that never terminate (Infinite loop indicator).

### 5. Implement Fix & Clean Up

- Once the root cause is identified from the logs, use `apply_patch` to fix the actual bug.
- **CRITICAL:** You MUST remove all temporary `[DEBUG-TRACE]` logs you injected before finishing the task. Never commit temporary instrumentation to the codebase.
