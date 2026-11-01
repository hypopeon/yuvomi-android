# 0008. Staying in sync with upstream

**Status:** Accepted, 2026-11-01

## Context

Upstream promises `/api/v1` as its contract: breaking changes are named in the CHANGELOG,
a deprecated operation keeps working at least 90 days, and `/api/v1` would stay 12 months after
any `/api/v2`. Upstream releases often (16 to 230 releases a month in 2026). Response fields
that are not documented may change at any time.

## Decision

Six mechanisms, detailed in [`UPSTREAM-SYNC.md`](../UPSTREAM-SYNC.md):

1. **Pin.** `upstream/VERSION` names the upstream tag the app is built and tested against.
2. **Snapshots.** `upstream/sync.sh <tag>` regenerates, from upstream source at that tag:
   `upstream/openapi.json`, `app/src/main/assets/i18n/*.json` (only the namespaces we use) and
   `app/src/main/assets/tokens.json`.
3. **Weekly sync job.** A scheduled workflow runs the sync against the newest upstream release and
   opens a PR with the diff, a report of changed operations we use, and the CHANGELOG sections
   since the pin.
4. **Contract tests.** CI starts `ghcr.io/ulsklyc/yuvomi:<pinned tag>`, seeds it with upstream's
   own `scripts/seed-demo.js`, and runs the API client's integration tests against it.
5. **Runtime version gate.** After sign-in the app reads `/version`. Older than the minimum
   supported version blocks with a message; newer than the pin shows a quiet notice once.
6. **Parity tracker.** `docs/PARITY.md` records each upstream module's status in this app and the
   upstream version it was last checked against.

## Consequences

- A breaking change shows up within a week of its release, leaving most of the 90 days to react.
- Translations and colours follow upstream without manual copying.
- The sync PR is the one place a maintainer of this repo has to look each week.
