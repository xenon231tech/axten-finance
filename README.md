# Axten

Axten — personal finance tracker in 14 languages: budgets, wallets, assets & live crypto prices. Free & private, no server needed.

Live: https://axten-xenon231techs-projects.vercel.app/

## Overview

Axten is a personal finance tracker that runs entirely in the browser. Track income and expenses, set budgets, manage wallets and assets, follow live crypto prices, and plan savings — in 14 languages and 29 currencies. There is no account and no server: all data stays on the user's device (browser localStorage).

## Features

- **Track money** — income & expenses, budgets per category, wallets (cash, bank, custom), assets & investments, debts, recurring bills
- **Crypto** — live prices (CoinGecko top 250), portfolio P/L, 7-day price charts, crypto converter, DCA reminders, price alerts & watchlist, buy/sell crypto transactions
- **Reports** — annual reports, per-category and per-wallet reports, expense calendar, category trends, net-worth trend, year-end closing
- **Import & export** — CSV import, JSON/CSV/Excel export, receipt photos, monthly journal, split bills
- **Simple mode** — hide advanced features for a cleaner view; collapsible sections; full feature directory on the home tab
- **Languages & currencies** — 14 languages, 29 currencies, live exchange rates
- **Privacy & security** — PIN lock (4–6 digits), hide balances, demo mode, onboarding tour, PWA install
- **Axten Pro** (one-time 100 Telegram Stars) — accent themes, unlimited wallets/goals/budgets, backup & restore via Telegram, advanced reports & insights, crypto price alerts
- **Donations** — voluntary support via Telegram Stars (does not unlock Pro)

## Tech stack

- **Frontend:** single-page app in one file (`index.html`) — HTML, CSS, vanilla JavaScript. No build step, no framework. Data in browser `localStorage`.
- **Crypto prices:** CoinGecko public API (top 250 coins, no key needed).
- **Backend (optional):** one Python serverless function (`api/create-invoice.py`) that creates Telegram Stars invoice links for Axten Pro and donations. Stateless — no database, no webhook.
- **Hosting:** Vercel (static site + serverless function).

## Project structure

```
axten-finance/
├── index.html            # The whole Axten app (single file)
├── privacy.html          # Privacy policy (bilingual ID + EN)
├── api/
│   └── create-invoice.py # Telegram Stars invoice backend (Vercel serverless)
├── vercel.json           # Vercel deploy config (static site + Python API)
├── .gitignore
├── LICENSE
└── README.md
```

## Run locally

No build step. Either:

- Open `index.html` directly in a browser, or
- Serve it (recommended, so the crypto price fetch works the same as in production):

```bash
python3 -m http.server 8000
# then open http://localhost:8000
```

The app works fully offline except for live crypto prices and exchange rates, which need internet.

## Deploy to Vercel

1. Import this repo in Vercel (or deploy from the CLI).
2. No build command is needed. Vercel serves `index.html` / `privacy.html` as static files and runs `api/create-invoice.py` as a serverless function.
3. Set the environment variable `TELEGRAM_BOT_TOKEN` (the @Axten_Bot token) in the Vercel project settings so the Stars backend works. **Never commit the token to the repo** — it only ever lives in the Vercel env vars.

## Telegram Stars backend

`api/create-invoice.py` is a stateless Vercel serverless function (Python, `BaseHTTPRequestHandler`). It:

- `GET /api/create-invoice` — health check, returns `{"ok": true, "service": "axten-stars-backend"}`.
- `POST /api/create-invoice` — creates a Telegram Stars invoice link via `createInvoiceLink` (currency `XTR`):
  - Default (no `kind`, or `kind: "pro"`): Axten Pro, fixed 100 Stars.
  - `{"kind": "donation", "amount": <1..10000>}`: voluntary donation of that many Stars.
- It reads the bot token only from the `TELEGRAM_BOT_TOKEN` environment variable. **No token or secret is stored in this repo.**
- The app opens the returned invoice link with `Telegram.WebApp.openInvoice`. Pro activates when the callback reports `"paid"`; a donation shows a thank-you message and unlocks nothing.

Telegram takes 15% of Stars payments; the developer receives 85%. Stars can be withdrawn via Fragment to a TON wallet (min 1,000 Stars, 21-day hold per Star).

## Privacy

All user data (transactions, budgets, wallets, assets, bills, PIN) is stored only in the device's browser `localStorage`. There is no account, no server sync, and no tracking. Only live crypto prices (CoinGecko) and exchange rates are fetched from the internet. Receipt photos never leave the device. See [privacy.html](privacy.html) for the full policy (v1.0, effective 18 November 2026).

## License

MIT — see [LICENSE](LICENSE). Copyright (c) 2026 Mohamad Ikhsan.
