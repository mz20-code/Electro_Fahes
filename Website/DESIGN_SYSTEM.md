# TechVerse / Precision Workshop

## Direction

An electronics counter for people who build and repair things: catalog first,
precise product photography, quiet surfaces, clear controls, restrained yellow.
Keep the existing TV logo unchanged. Do not replace it with a generic wordmark.

Applied skills: UI/UX Pro Max for e-commerce hierarchy, accessibility, interaction,
and responsive behavior; Brand for original identity, logo, and color consistency.
The generic store recommendations inform hierarchy, not a replacement brand palette.
The application remains Flask/Jinja with plain CSS and JavaScript.

## Theme tokens

| Role | Dark | Light |
| --- | --- | --- |
| Canvas | #101113 | #F6F6F1 |
| Surface | #191B1E | #FFFFFF |
| Raised surface | #24272B | #EDEDE7 |
| Text | #F4F4EF | #191B1E |
| Secondary text | #B0B2B6 | #5C6066 |
| Primary action | #FFE500 | #FFE500 |
| Text on primary | #151600 | #151600 |
| Accent text | #FFE500 | #675C00 |
| Input boundary | #6C7179 | #7D827A |

Use the semantic CSS variables in static/css/experience.css. Subtle decorative
card dividers and essential input boundaries use different contrast levels.

## Type and spacing

Use a local system sans-serif stack, with Tahoma/Segoe UI for Arabic.
No remote font requests. Headings are balanced and limited in line length.
Form controls use 16px text on small screens. Use 4/8px spacing increments.

## Components and behavior

- One clear primary action per task.
- Desktop category rail becomes wrapped, labeled category controls on phones.
- Product names remain available; do not truncate required specifications.
- Prices remain server-owned; no interface control changes price data.
- Product reference notices and source credits remain visible.
- Light/dark variants preserve semantic contrast instead of simply inverting colors.
- Every icon control has an accessible name; decorative SVGs are aria-hidden.
- Keyboard focus, live announcements, form summaries, and reduced motion are retained.
- No fake availability, discounts, star ratings, or customer statistics.

## Responsive rules

Primary adaptation points: 600, 800, 1050, 1200, and 1480px.
Product grids use 2 / 3 / 4 columns when space permits; list view is a separate
functional presentation. Layout uses logical directions for Arabic.

## Verification boundary

Automated rendered-markup and DOM behavior checks pass. These do not establish
real-browser rendering, visual polish at every viewport, or screen-reader behavior.
Review on actual phones/desktops before production deployment.

## Workbench edition (2026-11-01)

Redesign layer: `static/css/workbench.css`, loaded after `experience.css`.
Direction from UI UX Pro Max ("Feature-Rich Showcase" + bento blocks), kept on
the TechVerse palette rather than the tool's generic store palette.

- Home: hero with product "stage", bento service tiles (inverter guide in
  signal yellow, technicians, support), category tiles with real item counts
  linking to `?category=`, inverter brand/manual strip, then the catalog.
- Pill navigation with a yellow active state; rounded pill buttons with an
  arrow nudge on hover; cards lift 3px with a yellow border on hover.
- Product photos sit on a light "stage" in both themes; SKUs, prices, model
  names, and the phone number use a local monospace stack.
- Four-column footer (brand, explore, company, contact card).
- Fix: inverter model card images no longer overflow onto the card text.
- All motion is disabled under `prefers-reduced-motion: reduce`.
