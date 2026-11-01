# Implementation plan

The order in which the specs get built. Each milestone is one or more small PRs, and a milestone
is done when its acceptance criteria pass in CI.

| Milestone | Delivers | Proves |
|---|---|---|
| **M0 Scaffold** | Gradle project (Kotlin DSL, version catalog), app module, theme from `assets/tokens.json`, i18n loader for `assets/i18n/`, API core (OkHttp, cookie jar, CSRF and idempotency interceptors, envelope and error decoding), navigation shell with Overview, Tasks and "More in the web app", CI: build, unit tests, lint, and the contract-test job against `ghcr.io/ulsklyc/yuvomi:<pin>` seeded with `seed-demo.js`. Module icons converted from `nav-icons.js` by the sync. | SIGNIN-A7, SIGNIN-A12, SIGNIN-A13, a contract smoke test of `GET /version` |
| **M1 Sign-in** | [signin.md](spec/signin.md) in full. | SIGNIN-A1 to A13 |
| **M2 Overview** | [overview.md](spec/overview.md) in full. Ticking off from the overview uses the tasks repository from M3's first PR, so M3.1 lands first or together. | OVERVIEW-A1 to A11 |
| **M3 Tasks tier 1** | [tasks.md](spec/tasks.md) R1 to R27. | TASKS-A1 to A10, A17, A18 |
| **M4 Tasks tier 2** | [tasks.md](spec/tasks.md) R28 to R40. | TASKS-A11 to A16 |

Before M0 starts: an Android SDK in CI (GitHub's `ubuntu-latest` runners carry one) and the
repository setting that lets Actions open pull requests (for the weekly sync).
