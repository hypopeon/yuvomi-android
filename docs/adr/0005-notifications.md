# 0005. Notifications

**Status:** Accepted, 2026-11-01

## Context

Upstream delivers reminders through Web Push (VAPID) and household channels (ntfy, Gotify,
webhook, email). A native app could subscribe through UnifiedPush, or poll
`GET /reminders/pending` and post local notifications.

## Decision

**No notifications in the MVP.** The app neither registers for push nor polls for reminders.
Users who want reminders keep the PWA installed or use a household channel such as ntfy.

## Consequences

- No background work, no battery cost, no notification permission prompt.
- The `POST_NOTIFICATIONS` permission is not declared.
- The brainstorm's two options remain on file for a later decision: polling with local
  notifications, and UnifiedPush feeding the server's existing Web Push fan-out (needs a spike).

## Alternatives considered

See `ARCHITECTURE-BRAINSTORM.md`, section 2.5.
