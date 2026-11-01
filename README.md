# Yuvomi for Android (unofficial)

> **An unofficial proof of concept.** This is not part of the
> [Yuvomi](https://github.com/ulsklyc/yuvomi) project and is not endorsed by it. Yuvomi's web app
> remains the complete product; this repository explores a native Android client next to it.

A native Android client for a self-hosted Yuvomi family planner. It talks only to your own
server's documented `/api/v1`, with no cloud of ours in between, and opens the web app in your
browser for everything it does not do natively yet.

**Status:** architecture and specs are done; implementation has not started. See the
[plan](docs/PLAN.md).

## MVP

- Sign in with your Yuvomi username and password, plus your second factor if you use one.
- **Overview:** your own tile arrangement from the web app, today at a glance, tasks you can tick
  off right there.
- **Tasks:** list, filters, create and edit with every field the web app has, tick off and name
  who did it, recurring tasks, subtasks, checklists and comments.
- Everything else opens in your browser.

Not in the MVP: notifications, single sign-on, any other module as a native screen.

## How it is built

Kotlin, Jetpack Compose and Material 3, dressed in Yuvomi's own colours, which are taken from
upstream's design tokens, as are all 27 of its languages. Details:

- [Architecture](docs/ARCHITECTURE.md) and the [decision records](docs/adr/)
- Specs: [sign-in](docs/spec/signin.md), [overview](docs/spec/overview.md),
  [tasks](docs/spec/tasks.md)
- [Parity with upstream](docs/PARITY.md)

## Staying in sync with upstream

`upstream/VERSION` pins the Yuvomi release this app is built against (currently **2.83.0**). A
weekly workflow checks for a newer release, regenerates the OpenAPI snapshot, strings and colours
from upstream's source, and opens a pull request that reports which of the operations this app
uses changed. See [UPSTREAM-SYNC.md](docs/UPSTREAM-SYNC.md).

```bash
./upstream/sync.sh          # re-sync the pinned version
./upstream/sync.sh 2.84.0   # move the pin
```

## Licence

MIT, like upstream. Translations and design tokens under `app/src/main/assets/` come from
[ulsklyc/yuvomi](https://github.com/ulsklyc/yuvomi) (MIT, © 2026 ulsklyc).
