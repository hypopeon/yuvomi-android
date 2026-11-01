# 0002. Design language

**Status:** Accepted, 2026-11-01

## Context

Upstream's `DESIGN.md` describes its look as "Apple's craft, Yuvomi's handwriting": the
*structure* follows Apple's HIG, the *skin* is Yuvomi's own. The skin is warm paper neutrals
(`#F5F3ED` light, `#191816` dark), one violet voice (`#6C3AED`), nine module family tones, and a
custom monoline icon set. The brief asks the app to adhere to the original and to feel native.

## Decision

**Material 3 structure, Yuvomi skin.**

- Components, navigation patterns, motion and type scale are Material 3 on the system font.
- Colours come from upstream's `public/styles/tokens.css`, extracted by the sync tooling into
  `app/src/main/assets/tokens.json` (light and dark). The Material colour scheme is built from
  them: `background` = `--color-bg`, `surface` = `--color-surface`, `primary` =
  `--color-accent`, `error` = `--color-danger`, text roles from `--color-text-*`.
- **Dynamic colour is off.** Upstream's "one voice" rule says the house never changes colour.
- **Module tones** (`--module-tasks`, `--module-dashboard`, ...) colour module icons and tile
  headers, as on the web.
- **Icons:** upstream's module glyphs (`public/nav-icons.js`) are converted to vector drawables
  by the sync tooling. Everything else uses Material Symbols, matching upstream's fallback to
  Lucide for non-module icons.
- **Information architecture is copied, not reinterpreted:** module names, order, empty states,
  read-only signs and confirmation wording follow the web app.
- Light and dark follow the system setting.

## Consequences

- The app reads as an Android app to Android users and as Yuvomi to Yuvomi users.
- Restyling stock Material components is cheap. No custom control has to be built and made
  accessible on its own.
- It is not pixel-identical to the PWA. Grouped inset lists become Material lists on
  `surfaceContainer`; capsule segmented controls become Material segmented buttons.
- A colour change upstream reaches the app through the weekly sync PR, not by hand.

## Alternatives considered

- **Replicating the HIG look in Compose:** closest to upstream, but reads as an iOS port on
  Android and makes every custom control ours to maintain.
- **Stock Material 3 with dynamic colour:** fastest, loses the brand.
