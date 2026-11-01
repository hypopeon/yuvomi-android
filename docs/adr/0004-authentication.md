# 0004. Authentication

**Status:** Accepted, 2026-11-01

## Context

Upstream offers three ways in:

- **Password sign-in** (`POST /auth/login`), followed by **TOTP** (`POST /auth/2fa/verify`) when
  the account has a second factor. It creates a server session in the `yuvomi.sid` cookie. State-
  changing requests then need the `X-CSRF-Token` header. Sessions slide over 90 days.
- **API tokens** (`Authorization: Bearer` or `X-API-Key`), which only an admin can create, for any
  member.
- **OIDC single sign-on**, a browser redirect flow that ends with a session cookie in the
  browser's own cookie jar.

Upstream lists device pairing for native clients as open server work.

## Decision

- Sign in with **server URL, username, password, then TOTP or a recovery code when asked**, exactly
  the PWA's flow.
- Keep the session cookie in an OkHttp `CookieJar` persisted with DataStore and encrypted with a
  Keystore key. Keep the CSRF token in memory, refreshed from every response's `X-CSRF-Token`
  header and from `/auth/me`.
- A `401` on anything except the sign-in calls ends the session locally and returns to sign-in,
  keeping the server URL and username.
- **Households that sign in only through SSO are unsupported in the MVP.** When the server answers
  `password_login_disabled`, the app says so and offers to open the web app in the browser.
- API tokens are not used.

## Consequences

- Every member, including children, can sign in on their own phone without an admin's help.
- The app behaves like one more browser session: it appears in the user's session list and is
  ended by "sign out other devices".
- SSO-only households cannot use the app until upstream ships device pairing.

## Alternatives considered

- **Admin-minted API token as an advanced sign-in:** workable for SSO-only households, declined
  for the MVP to keep one sign-in path.
- **OIDC in a Custom Tab:** the callback sets the cookie in the browser, not in the app.
