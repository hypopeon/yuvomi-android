# 0006. Modules that are not native

**Status:** Accepted, 2026-11-01

## Context

Upstream has twenty modules; the MVP makes two native (ADR 0010). The overview payload also
carries data from other modules (events, meals, shopping, birthdays and more).

## Decision

- A module without a native screen is **opened in the user's browser** at the matching PWA route
  on the household's server (`https://<server>/calendar`, `/shopping`, ...), through
  **Android Custom Tabs**, falling back to the default browser. Never a WebView.
- The navigation shows the native modules first, then a **"More in the web app"** section listing
  every other module the user may access, each with an "opens in browser" mark.
- Overview tiles of non-native modules render their data natively and read-only; tapping one opens
  the corresponding PWA route in the browser.
- The browser has its own session. The user may have to sign in there once; the app does not
  try to hand over its cookie.

## Consequences

- Nothing in the household becomes unreachable from the app.
- The jump to the browser is visible and honest; it is never disguised as an in-app screen.

## Alternatives considered

- **Hiding non-native modules:** cleaner, but leaves users stranded.
- **WebView:** excluded by the brief.
