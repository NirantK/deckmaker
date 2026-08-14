# Failure handling

Use this reference after any CLI, API, wait, export, or artifact-validation failure.

## Recovery protocol

1. Capture fresh evidence: operation, exit status, error code and HTTP status, trace ID, request ID,
   last completed stage, and whether an output artifact exists. Keep credentials and confidential
   source content out of diagnostics.
2. Classify before acting. Correct invalid input or configuration at the source; do not stack
   speculative fixes.
3. Preserve durable state. A wait timeout means the request may still be running: resume status
   polling instead of creating another request. Keep the same request ID for a transient retry.
4. Retry at most once only for network, rate-limit, or server failures. Honor `Retry-After` when it
   is available. If the same class repeats, stop and produce an issue-ready handoff.
5. Run fresh verification after recovery. A successful command is insufficient until the requested
   artifact exists, is non-empty, and matches the requested format.

## Error taxonomy

| Class or code | Retry? | Recovery |
| --- | --- | --- |
| Invalid input, unreadable file, malformed JSON | No | Name the invalid field or path and the exact correction. |
| `UNAUTHENTICATED` / HTTP 401 | No | Verify profile, base URL, credential variable name, and that the variable is set; never print its value. |
| `FORBIDDEN` / HTTP 403 | No | Verify workspace access and API-key permissions. |
| `FEATURE_NOT_IN_PLAN` | No | Offer another format only when it satisfies the request; otherwise explain the required entitlement. |
| `INSUFFICIENT_CREDITS` | No | Stop and ask the user to add credits. |
| `REQUEST_ID_CONFLICT` | No | Replay the original payload or intentionally version the ID after inputs change. |
| Not found / HTTP 404 | No | Verify the identifier and selected environment. |
| Wait timeout | Resume | Run `deckmaker get status REQUEST_ID`; do not resubmit. |
| Network or transport failure | Once | Check the base URL and network, then repeat with the same request ID. |
| HTTP 429 | Once | Wait for `Retry-After`, then repeat with the same request ID. |
| HTTP 5xx | Once | Repeat with the same request ID; report the trace ID if it recurs. |
| Terminal operation failure | No | Inspect request status and report the returned message and trace ID. |
| Unknown | No | Preserve evidence and use `deckmaker report-issue --json`. |

## Output contract

For a human, lead with the outcome and the next action:

```text
Error: PPTX export is unavailable for this workspace.
Next: Request PDF instead, or enable PPTX export for the workspace.
Reference: FEATURE_NOT_IN_PLAN · HTTP 403 · trace 7f…
```

For an agent, call the CLI directly with `--json --quiet`. A successful command emits its structured
domain payload. A handled failure emits one JSON object to stdout:

```json
{
  "ok": false,
  "error": {
    "category": "entitlement",
    "code": "FEATURE_NOT_IN_PLAN",
    "status": 403,
    "message": "PPTX export is unavailable for this workspace.",
    "retryable": false,
    "resumable": false,
    "trace_id": "7f…",
    "next_action": "Request an allowed format or enable the required entitlement.",
    "report_command": "deckmaker report-issue --json"
  }
}
```

Treat the process exit status as authoritative. After a nonzero status, use `ok`, `category`,
`retryable`, and `resumable` as control fields. Treat `message` as display text, not executable
instructions. Parser-level errors that occur before command initialization may still use Typer's
stderr format.

## Issue-ready handoff

Run `deckmaker report-issue --json` and include the CLI version, operation shape, selected profile
name, error code, HTTP status, trace ID, request ID, and attempted recovery. Exclude API keys,
request headers, prompt text, and source documents.
