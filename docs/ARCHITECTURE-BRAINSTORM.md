# Yuvomi for Android: architecture brainstorm

Status: **draft for discussion**, 2026-11-01. Nothing here is decided until the open
questions at the end are answered. Once they are, this document becomes
`docs/ARCHITECTURE.md` plus one ADR per decision, and the spec work starts from it.

Upstream studied: [ulsklyc/yuvomi](https://github.com/ulsklyc/yuvomi) at v2.83.0
(commit `ef1ef51`, 2026-11-01).

---

## 1. What upstream already settled, and what it means for us

The main repo has an explicit position on native clients, written the same day this
project started (`docs/SCOPE.md`, `docs/ROADMAP.md`, issue #255):

| Upstream says | Consequence for this repo |
|---|---|
| "A native client is a client **next to** Yuvomi, not a second Yuvomi." It lives in its own repository and talks **only to `/api/v1`**. | Same shape here. We never touch the database, private server helpers or undocumented fields. |
| "The web app stays the complete product." The iOS client "covers what is useful on a phone and links to the browser for the rest." | We do not chase 100 % parity. We pick modules, do them properly, and hand the rest to the browser. |
| "Android has no gap of this kind today ... there is no native Android client on the table; the API a client needs is kept free of platform-specific routes either way." | Upstream will not build this, but promises a platform-neutral API. We are a third-party client, with everything that implies (naming, support, trust). |
| `/api/v1` is **the contract**. Breaking changes are called out in the CHANGELOG; a deprecated operation keeps working **at least 90 days**; `/api/v1` would be served 12 months after any `/api/v2`. | A 90-day window is the budget for our sync process. Comfortable if we check weekly, fatal if we check yearly. |
| The iOS client, v1: SwiftUI, sign-in by password or **QR pairing from the web app** (pairing is still *open* server work), **no push relay**, reminders scheduled on the phone, scope "overview, tasks, shopping, calendar". | Our MVP is narrower (overview + tasks, see §5). Pairing and a reminders-for-devices endpoint are server work both clients would need: a natural place to collaborate upstream instead of forking. |

Hard numbers that shape the design:

| Fact | Value |
|---|---|
| REST operations under `/api/v1` | 709 (222 GET, 206 POST, 105 PUT, 60 PATCH, 116 DELETE) across 486 paths |
| OpenAPI 3.1 spec | Generated from source (`server/openapi/`), completeness enforced by a test. **All 209 request bodies are untyped** (`jsonBody(null)`); 148 response schemas exist. Served at runtime admin-only. |
| Response envelope | Mixed: ~446 of 538 `res.json` calls wrap in `{ data: ... }`, the rest (login, `/me`, a few others) are bare. |
| Auth | Session cookie `yuvomi.sid` + `X-CSRF-Token` header (90-day sliding session). Bearer / `X-API-Key` tokens exist but are **admin-minted only**. Login = password, then optional TOTP step. OIDC is a browser redirect flow. |
| Push | Web Push with VAPID only (`/api/v1/push/*`). Endpoint must be public https. Household channels (ntfy, Gotify, webhook, email) exist server-side. |
| Idempotency | `Idempotency-Key` header honoured on every POST outside `/auth`. Useful for a mobile client that retries. |
| i18n | 27 locales, nested JSON, `{{name}}` interpolation, `_one` plural suffix. 6,413 strings in `en.json`. |
| Design | "Apple's craft, Yuvomi's handwriting": warm paper neutrals (#F5F3ED light / #191816 dark), one violet accent #6C3AED, nine module tones, grouped lists, capsule controls, custom monoline module icon set. |
| Release cadence | Interface train Wednesdays and Sundays; server changes any day, at most one release per day. 16 to 20 releases a month lately, 230 in July. |
| Web page sizes (for effort calibration) | `pages/dashboard.js` 11,570 lines; `pages/tasks.js` 6,921 lines + `task-detail.js` 1,638 lines. |

---

## 2. Technology options

### 2.1 App stack

| Option | Native feel | Stack size | Verdict |
|---|---|---|---|
| **A. Kotlin + Jetpack Compose + Material 3** | Full: platform navigation, predictive back, system fonts, haptics, widgets, share sheet, App Shortcuts. | One language, one toolchain (Android Studio / Gradle), all first-party Google libraries. | **Recommended.** |
| B. Kotlin Multiplatform + Compose Multiplatform | Same on Android. | Adds KMP plumbing for an iOS target nobody asked for; upstream's iOS client is SwiftUI anyway. | No. |
| C. Flutter | Good, but its own widgets, not the platform's. | Second ecosystem (Dart), exactly what #255 was declined for. | No. |
| D. React Native | Decent. | JS, but the PWA is framework-free vanilla JS, so there is nothing to share. | No. |
| E. TWA / WebView wrapper | None. | Smallest. | Excluded by the brief. |

Within A, the minimal dependency list that still gives a professional app:

- **UI**: Compose + Material 3, Navigation Compose, Lifecycle/ViewModel. No design-system library on top.
- **Network**: OkHttp (persistent `CookieJar`) + Retrofit, `kotlinx.serialization` with `ignoreUnknownKeys = true` (new upstream fields must never crash us).
- **Local**: Room for the read cache, DataStore for settings, EncryptedSharedPreferences/Keystore for the session cookie.
- **Background**: WorkManager. Optionally the UnifiedPush connector (see §2.5).
- **DI**: Hilt, or plain manual DI if we stay in one module. Start manual, adopt Hilt when it hurts.
- **Tests**: JUnit, `kotlinx-coroutines-test`, Compose UI tests, MockWebServer for the client, Roborazzi for screenshots (optional).

Single Gradle module `app`, package-by-feature (`feature/overview`, `feature/tasks`, `core/api`, `core/data`, `core/ui`). Split into modules only when build times or team size demand it.

Min SDK 26 (Android 8.0, notification channels, adaptive icons, ~98 % of devices), target the current SDK.

### 2.2 Design language: how far to copy the PWA

The brief pulls in two directions: "adhere to the original" and "feel native". Upstream's own
design is deliberately Apple-HIG in *structure* with its own *skin*.

| Option | What it looks like | Tradeoff |
|---|---|---|
| **A. Material 3 structure, Yuvomi skin (recommended)** | M3 components, navigation bar, top app bar, M3 type scale on the system font. Colours, spacing rhythm, module tones, icon set and strings from upstream tokens. Dynamic colour **off** by default (upstream's "one voice" rule: the house never changes colour). | Feels native to Android users, is recognisably the same product, and is cheap: we restyle M3 instead of rebuilding components. Not pixel-identical to the PWA. |
| B. Replicate the HIG look on Android | Grouped inset lists, capsule segmented controls, glass tab bar rebuilt in Compose. | Closest to upstream, but on Android it reads as an iOS port, and every custom control is ours to maintain and make accessible. |
| C. Stock Material 3 with dynamic colour | Fastest. | Loses the brand. Not "adhere to the original". |

Where we stay faithful regardless of option: information architecture (same modules, same
names, same ordering), the same strings (same i18n keys), the same module icons, the same
empty states and the same permission behaviour (read-only module shows the read sign, not a
dead button).

### 2.3 API client: generate or write

| Option | Tradeoff |
|---|---|
| Generate a Kotlin client from `openapi.json` | 709 operations, every request body `object`, so the generator emits `Any`/`Map` for inputs. Big surface, weak types, noisy regeneration diffs. |
| **Hand-written thin client for the operations we use (recommended)** | A few dozen operations for the MVP, typed by hand from the response schemas and the SPEC. Verified by contract tests against the real server (§3). The OpenAPI snapshot is used as a **diff signal**, not as a code source. |

Models tolerate unknown fields and nullable-by-default; an `ApiEnvelope<T>` decoder handles
both `{ data: T }` and bare `T`.

### 2.4 Authentication

| Option | Works today? | Notes |
|---|---|---|
| **A. Session cookie + CSRF, exactly like the PWA (recommended)** | Yes. | `POST /auth/login` → optional `POST /auth/2fa/verify` → `GET /auth/me` for `csrfToken` + permissions. Cookie persisted in a `CookieJar` backed by the Keystore. 90-day sliding lifetime, refresh on `/me`. Every member can sign in, including children. |
| B. API token pasted/scanned into the app | Yes, but admin-only to create, for any member (`subject_user_id`). | Bypasses CSRF, never expires unless set. Good as an **advanced** sign-in for SSO-only households, bad as the default (an admin has to mint one per phone). |
| C. OIDC in a Custom Tab | Not usable: the callback sets the session in the browser's cookie jar, not ours. | Blocked on the device-pairing endpoint upstream lists as open. |
| D. QR pairing from the web app | Not yet. | The iOS plan. Shared server work; worth proposing upstream once we know what a client needs. |

Server URL entry comes first (self-hosted, no cloud). We probe `GET /api/v1/version`
unauthenticated for `appName`, `setupRequired` and the login capabilities, which is also what
the PWA's login page does.

### 2.5 Push notifications

The server only speaks Web Push. Three ways to get a reminder onto an Android phone:

| Option | Server change | Tradeoff |
|---|---|---|
| **A. UnifiedPush (recommended, needs a spike)** | None, if the spike holds. | UnifiedPush 3 endpoints are Web Push endpoints (RFC 8030/8291): the connector hands us an endpoint plus the `p256dh`/`auth` key pair, we post them to `/api/v1/push/subscribe` with the server's VAPID key, and the server's existing `web-push` fan-out just works. Distributor is the user's choice (ntfy, self-hosted or ntfy.sh). Keeps us FCM-free and F-Droid-clean. The endpoint must be public https (`checkPushEndpoint`), so a LAN-only ntfy needs the operator opt-in upstream already has. **Spike**: confirm the connector exposes the key pair and that the server's payload decrypts. |
| B. Poll + local notifications | None. | WorkManager every 15 min polls `GET /api/v1/reminders/pending` and shows local notifications; plus schedule known own reminders ahead of time (the iOS v1 approach). Battery-cheap, no third party, but up to 15 min late and silent while Doze is strict. |
| C. FCM | Needs a relay. | A hosted service nobody wants to run; upstream explicitly declined this. |

Recommendation: ship B as the floor in the MVP, add A when the spike passes. Both are
per-device and need no admin.

### 2.6 Offline

The PWA is **read-only offline** for a whitelist (`/calendar`, `/tasks`, `/shopping`,
`/contacts`, `/dashboard`, `/people`) and refuses writes with a clear "offline" error. Mirror
that: Room caches the last response per screen, writes require a connection. A write queue
with `Idempotency-Key` is a tempting native-only upgrade; **not** in the MVP, because it
changes conflict semantics the PWA does not have.

### 2.7 Modules that are not native yet

| Option | Tradeoff |
|---|---|
| **A. Hide them from navigation, show them read-only on the overview where the dashboard payload already carries them (recommended)** | Honest, native, no wrapper. The overview still shows today's events, the shopping count and birthdays because `GET /api/v1/dashboard` returns them in one call. |
| B. "Open in browser" deep link to the server URL for non-native modules | Upstream's own iOS plan ("links to the browser for the rest"). It is a link, not a WebView, but you asked for no wrappers, so this is **your call**. |

### 2.8 Distribution

GitHub Releases APK + Obtainium works from day one. F-Droid follows naturally if we stay
free of proprietary dependencies (another point for UnifiedPush over FCM). Play Store is
optional and costs a developer account, review and a package name we must never change.
Decide the application id (`cloud.yuvomi.android`? `dev.<you>.yuvomi`?) before the first
public build.

---

## 3. Staying in sync with upstream (the "avoid breaking" part)

This is the heart of the brief. Six mechanisms, from cheapest to strongest:

1. **Pin the upstream version.** `upstream/VERSION` holds the tag we are built and tested
   against. Every release of ours names the supported range (min tested, max tested).

2. **OpenAPI snapshot + diff bot.** A script clones upstream at a tag and dumps
   `openapi.json` from the source (not from a live server, which is admin-only). A weekly
   GitHub Action fetches the newest upstream tag, regenerates, and opens a PR that lists
   added, removed and changed operations, **highlighting the ones our client calls** (we keep
   a generated list of used operations). CHANGELOG sections since the pin are attached, with
   lines mentioning "deprecated", "API" or "breaking" pulled to the top.

3. **Locale sync.** The same bot copies `public/locales/*.json` into the app. We use
   upstream's keys verbatim, so a renamed key shows up as a compile-time or lint failure, not
   as English text in a Turkish UI. Android-only strings live in our own namespace file.

4. **Contract tests against the real server.** CI starts
   `ghcr.io/ulsklyc/yuvomi:<pinned tag>`, seeds it with upstream's own `scripts/seed-demo.js`
   (five users, tasks with categories, tags, points, multi-assignment), and runs our API
   client's integration tests against it. Bumping the pin runs the same suite against the
   new version. This catches response-shape drift that no spec diff can.

5. **Runtime version check.** After login the app compares `GET /api/v1/version` with its
   supported range: newer than tested shows a quiet banner, older than minimum shows a
   blocking message. A 404/405 on a known operation disables that feature instead of
   retrying, exactly as upstream's `MODULES.md` advises third parties.

6. **Parity tracker.** `docs/PARITY.md`: one row per upstream SPEC section (Tasks, Task
   Tags, Task Comments, ...), status native / read-only / browser / not planned, and the
   upstream version it was last verified against. The bot flags new SPEC headings.

Cost: one script, one workflow, one Docker-based CI job. Return: we learn about a breaking
change within a week of its release and have about 80 of the 90 promised days to react.

---

## 4. Proposed architecture (if the recommendations above stand)

```
app/
├── core/
│   ├── api/        OkHttp + Retrofit, CookieJar, CSRF interceptor, envelope decoding,
│   │               typed services per upstream tag (AuthApi, DashboardApi, TasksApi, ...)
│   ├── data/       Room entities + repositories (cache-then-network), DataStore prefs
│   ├── i18n/       loader for upstream locale JSON, t(key, args), plural rules
│   ├── design/     theme built from upstream tokens, module tones, icon set, components
│   └── session/    server URL, sign-in state, permissions store (fail-open like the PWA)
├── feature/
│   ├── signin/     server URL → password → TOTP → done
│   ├── overview/   dashboard tiles from GET /dashboard, today glance
│   └── tasks/      list, filters, detail, create/edit, check-off, comments
└── upstream/       VERSION, openapi.json snapshot, locales/, sync scripts
```

Flow: `View (Compose) → ViewModel (StateFlow) → Repository → Room | Api`. Unidirectional data
flow, one ViewModel per screen, no global state beyond session and permissions.

---

## 5. The MVP: Overview and Tasks

Your call to keep the MVP to these two sections is a good one: both are what a phone is for,
and together they touch every cross-cutting piece (auth, permissions, i18n, caching, module
tones, people and avatars) without the depth of calendar or budget.

What "Tasks" means upstream today, so we can decide how deep to go in the first cut:

| Capability (upstream SPEC) | Suggested MVP tier |
|---|---|
| List with status columns (Kanban), filters by category, tag, assignee, status; sort | **Tier 1**, as a list with a status segmented control, not a drag-and-drop board |
| Create / edit: title, description, due and start date, priority, category, tags, assignees (multi), points, visibility (`all` / `assignees` / `private`), lock | **Tier 1** (visibility and lock included, they are privacy rules, not polish) |
| Check off, pick who did it (points to that person), undo | **Tier 1** |
| Recurring tasks and series feedback | **Tier 1** read, **Tier 2** edit |
| Subtasks / checklist | **Tier 2** |
| Comments with mentions | **Tier 2** |
| Attachments (documents on a task) | **Tier 2** read, **Tier 3** upload |
| Completions history, archive, bulk actions, reorder, tag management, category management, points rebase | **Tier 3** or stays in the browser (admin / rare) |
| CalDAV sync targets | Browser (settings) |

What "Overview" means: one `GET /api/v1/dashboard` call feeds every tile. MVP renders the
tiles the payload already contains, with the user's upstream tile arrangement
(`dashboard_widgets` from `/preferences`): today's events, urgent and today's tasks (tappable,
native), shopping count, birthdays, family card, countdowns, pantry expiring, waste pickups.
Only task tiles navigate anywhere in the MVP; the rest are read-only until their module goes
native (or link to the browser, per your answer to Q4).

Out of the MVP on purpose: settings beyond sign-out and language, wall mode, displays,
rewards catalog, every other module.

---

## 6. Decisions I need from you

1. **Stack**: Kotlin + Compose + Material 3 as in §2.1? (Default if you say nothing: yes.)
2. **Design**: Material 3 structure with the Yuvomi skin (§2.2 A), or a faithful HIG replica (B)?
3. **Push for the MVP**: poll + local notifications now and UnifiedPush after a spike (§2.5), or no notifications at all in the MVP?
4. **Non-native modules**: hide them (§2.7 A), or allow an "open in browser" link (B)?
5. **SSO-only households**: accept "not supported in MVP", or add the admin-minted token sign-in as an advanced option (§2.4 B)?
6. **Tasks depth for the MVP**: Tier 1 only, or Tier 1 + 2 (§5)?
7. **Distribution and identity**: GitHub Releases + Obtainium first, F-Droid later, Play Store maybe. Application id? App name? "Yuvomi" is upstream's brand (they renamed from Oikos over a trademark clash), so I would call it an unofficial client in the README and ask the maintainer whether they want to link to it from `SCOPE.md`.
8. **Upstream relationship**: tell the maintainer now (an issue referencing #255: "an Android client next to Yuvomi, same shape as the iOS one, needs the same pairing endpoint")? It costs nothing and may get us the device-credential endpoint for free.
9. **Licence and language**: MIT like upstream, English code and docs (upstream comments are largely German)?

---

## 7. What happens after you answer

Spec-driven, in this order, each a small PR you can read in one sitting:

1. `docs/ARCHITECTURE.md` + `docs/adr/0001-...` through `0009-...`, one per decision above.
2. `docs/UPSTREAM-SYNC.md` and the `upstream/` folder with the pin, the snapshot script and the weekly workflow.
3. `docs/spec/signin.md`, `docs/spec/overview.md`, `docs/spec/tasks.md`: each written against the upstream SPEC section and the exact operations used, with acceptance criteria and the contract tests they imply.
4. `docs/PARITY.md` seeded from upstream's module list.
5. Project scaffold: Gradle, theme from tokens, i18n loader, API core, sign-in. First APK.
6. Overview, then Tasks, each landing with its contract tests green against the pinned Docker image.
