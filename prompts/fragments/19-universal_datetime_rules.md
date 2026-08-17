<universal_datetime_rules>
You MUST enforce these universal datetime rules in every generated implementation task, across ALL layers and ALL programming languages.

### Core Rules

1. **UTC at Rest:** All databases, caches, and persistent storage MUST store datetime values in UTC. The storage column type must be `TIMESTAMP WITH TIME ZONE` (or language equivalent). Banned: storing local time, storing timezone-naive values, or relying on the database server's timezone setting.
2. **Unix Epoch / ISO-8601 with Offset at API Boundaries:** All API contracts (REST, gRPC, GraphQL) MUST transmit datetime values as either:
   - **Unix Epoch milliseconds** (int64) — preferred for inter-service numeric precision.
   - **ISO-8601 string with timezone offset** (e.g., `2026-07-23T14:30:00+00:00`) — preferred for human-readable APIs.
     Banned: date-only strings without timezone, ISO-8601 without offset, or locale-dependent formats in API payloads.
3. **SOLID Clock Injection (Ban Un-mockable Clock Calls):** All code that needs the current time MUST receive a `Clock` abstraction (e.g., `java.time.Clock`, `time.Now()` wrapper, `DateTimeProvider` interface) via dependency injection. Banned: direct calls to `new Date()`, `DateTime.Now`, `datetime.now()`, `time.Now()` in business logic, or any static time method that cannot be mocked in unit tests.
4. **Dual-Representation for Future Calendar Events:** For events with a future calendar date (e.g., "meeting on July 25th at 10 AM Tehran time"), the API MUST expose two fields:
   - `event_start_local`: The local time with timezone (e.g., `2026-07-25T10:00:00+03:30`).
   - `event_start_epoch_ms`: The absolute Unix epoch milliseconds for ordering and scheduling.
     This prevents ambiguity when daylight saving time changes between creation and execution.

### Infrastructure Enforcement

- All staging and production environments MUST run with `TZ=UTC` (container environment variable or host-level config).
- No application code should ever read the server's local timezone. Timezone display is a client-layer responsibility.
- CI/CD pipelines MUST include a test that verifies datetime behavior is timezone-independent (e.g., running the same test in `TZ=UTC` and `TZ=Asia/Tehran` produces identical stored values).
  </universal_datetime_rules>