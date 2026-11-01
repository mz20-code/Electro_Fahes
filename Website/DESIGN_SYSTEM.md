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

### CSS files

Shared on every page (loaded by `base.html`):

- `static/css/style.css`, `static/css/experience.css` — original base styles.
- `static/css/workbench.css` — design tokens, header, buttons, forms, footer,
  the shared page hero (`.pg-hero`) and the product card.

One file per page in `static/css/pages/`, linked from that page's template
through `{% block page_css %}`:

| Page | Template | CSS |
| --- | --- | --- |
| Home | welcome.html | pages/home.css |
| Sign in | login.html | pages/login.css |
| Create account | register.html | pages/register.css |
| Shop | shop.html (+ _catalog.html) | pages/shop.css |
| Product | product.html | pages/product.css |
| Inverter guide | ai_advisor.html | pages/advisor.css |
| Technicians | membership.html | pages/technicians.css |
| Technician application | technician_application.html | pages/technician-apply.css |
| Companies | companies.html | pages/companies.css |
| Company registration | company_register.html | pages/company-register.css |
| Cart | cart.html | pages/cart.css |
| Settings | settings.html | pages/settings.css |
| Contact | contact.html | pages/contact.css |
| Videos | learn.html | pages/learn.css |
| About / Privacy | text_page.html | pages/text-page.css |
| Errors | error.html | pages/error.css |
| Administration | admin_panel, admin_products, edit_product, import_products | pages/admin.css |
| Sources | sources.html, photo_sources.html | pages/sources.css |

### Page notes

- Home is a landing page only: hero, service tiles, categories, eight popular
  products, inverter brands, and a create-account band. The full catalog is on
  the Shop page (signed-in).
- Sign in and Create account have separate layouts (dark brand card vs. yellow
  step list).
- Product: sticky photo stage, price card, local-support row.
- Fix: inverter model card images no longer overflow onto the card text.
- All motion is disabled under `prefers-reduced-motion: reduce`.
