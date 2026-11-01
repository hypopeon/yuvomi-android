# 0007. Offline behaviour

**Status:** Accepted, 2026-11-01

## Context

The PWA caches a whitelist of read endpoints (`/dashboard`, `/tasks`, `/calendar`, `/shopping`,
`/contacts`, `/people`) network-first and refuses writes offline with a clear message. Upstream
honours an `Idempotency-Key` header on every POST outside `/auth`.

## Decision

- **Reads:** cache-then-network. The last good response of the overview, the task list and each
  opened task detail is kept in Room, scoped to server URL and user ID. Cached content is shown
  with a quiet "offline, last updated <time>" banner.
- **Writes:** need a connection. Offline, write actions show the same "you are offline" message
  the PWA shows and change nothing.
- **Retries:** a write that fails with a network error may be retried by the user. A POST reuses
  its `Idempotency-Key`, so a retry never creates a second task or comment.
- **Sign-out** deletes every cached row for that server and user.

## Consequences

- Same semantics as the PWA, so no conflict handling is needed.
- No write queue. That is a possible later upgrade and needs its own record.
