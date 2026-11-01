# TechVerse — UI/UX Edition

## Start on Windows

1. Extract the entire ZIP. Do not run the website from inside WinRAR.
2. Open the extracted Techverse_UIUX folder.
3. Double-click START_WINDOWS.bat.
4. Open http://127.0.0.1:5000 in your browser. Keep the terminal open.

The launcher finds its own Website folder, creates the Python environment,
and installs Website/requirements.txt. The first start needs internet.
Python 3.11 or later is recommended. If the launcher cannot find Python,
install it from python.org with “Add Python to PATH” enabled.

PowerShell alternative, from the extracted root folder:

```powershell
.\START_WINDOWS.bat
```

On macOS/Linux, run:

```bash
bash START_MAC_LINUX.sh
```

## Keep your existing accounts and inventory

The release ZIP contains application source and assets, not the old computer's
Python environment, private database, session key, or payment/account records.
Your uploaded original remains the source for those private files.

Before upgrading, stop the old website and back up its Website/instance folder.
Then either:

- Copy the updated application files into your existing Website folder and
  leave its instance folder in place; or
- Copy your old Website/instance folder into this package's Website folder
  before the first start.

Do not replace a working database with a newly generated empty database.
Keep any existing Website/.env file; this release does not change API keys,
payment credentials, or existing account passwords.

For a fresh installation, the application creates its own private instance
folder on first start. Register an account normally. The existing manage.py
commands remain available for administration.

## What changed

- Catalog-first layout with the original yellow, white, and charcoal identity.
- Consistent dark/light styling, typography, spacing, and controls.
- Product cards, product detail pages, account screens, and contact page.
- Category icons, removable category filter, clear-search button, grid/list view.
- Search and sort state preserved in the URL; view preference remembered locally.
- Keyboard-operable mobile navigation and clearer active states.
- Inline form errors, linked error summaries, password confirmation, and submit feedback.
- Three-step inverter guide and a “Choose another model” control.
- Cart image fix for products uploaded through Administration.
- Responsive CSS, reduced-motion support, local assets, no external font dependency.

Existing sign-in gating, English/Arabic translation, inventory prices and photos,
manual references, private conversations, technician approval/payment logic,
CSV administration, and account storage are retained.

## Verification

- 161 Python regression tests passed.
- DOM interaction tests passed for English/Arabic search, filtering, sorting,
  pagination, layout switching, navigation, themes, cart, forms, and advisor.
- JavaScript syntax and launcher shell syntax checked.
- Real-browser visual/viewport testing was not available in the editing environment.
- Live card payments and external AI calls were not exercised.

No hosting or publication was performed. This is the updated runnable Flask package.
