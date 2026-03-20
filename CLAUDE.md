# CLAUDE.md - Sigma Finance

## Project Overview
Sigma Finance is a dues payment management system for a Phi Beta Sigma fraternity chapter. React 19 SPA frontend with Flask REST API backend, deployed on Render.

## Tech Stack
- **Backend**: Flask 3.x, Python 3.11+, SQLAlchemy, PostgreSQL (prod), SQLite (local)
- **Frontend**: React 19, TypeScript, Vite, Tailwind CSS, Zustand
- **Payments**: Stripe (two accounts — dues + donations)
- **Email**: SendGrid (v6.12.4)
- **Cache**: Redis (prod), SimpleCache (local)
- **Hosting**: Render (web service + cron job)

## Key File Paths
- App factory: `sigma_finance/app.py`
- Config: `sigma_finance/config.py`
- Models: `sigma_finance/models.py`
- API routes: `sigma_finance/routes/api.py`
- Webhooks: `sigma_finance/routes/webhooks.py`
- Status updater: `sigma_finance/utils/status_updater.py`
- Stats/caching: `sigma_finance/services/stats.py`
- Reminder cron: `sigma_finance/utils/reminder.py`
- Frontend: `react-frontend/src/`
- Deployment: `render.yaml`

## Development Setup
```bash
# Backend
python -m venv .venv && .venv\Scripts\activate
pip install -r requirements.txt
flask run  # port 5000

# Frontend
cd react-frontend && npm install && npm run dev  # port 5173
```

Set `CONFIG_CLASS=sigma_finance.config.LocalConfig` for local dev.

## Deployment (Render)
- Single web service: builds React (`npm run build`), then runs Flask via gunicorn
- Secrets stored as Render Secret Files at `/etc/secrets/<name>`
- `read_render_secret(name)` in config.py reads secret files first, falls back to `os.getenv()`
- Cron job (`payment-reminders`) is a separate Render service with its own Secret Files
- `VITE_` env vars need `sync: false` in `render.yaml` to be available at build time

## Architecture Notes
- In production, only the API blueprint and webhook blueprint are registered
- Template-based routes (auth, treasurer, payments, reports, etc.) are debug-mode only
- React build is served as static files by Flask in production
- CSRF is exempt on API routes (React SPA uses session cookies)

## Authentication & Roles
- Session-based auth via Flask-Login + `@login_required`
- Role hierarchy:
  - **Treasurer-level** (`admin`, `treasurer`, `president`, `vice_1`): full member/payment management
  - **Report access** (above + `vice_2`, `secretary`): view reports
  - **Member**: own dashboard, payments, profile
- reCAPTCHA v3 on login/register (optional — skips if no token provided)

## Webhook Security
- **Stripe**: signature verified via `stripe.Webhook.construct_event()`
- **SendGrid (v6.12.4)**: ECDSA signature verified via `EventWebhook().verify_signature()`
  - `EventWebhookHeader.SIGNATURE` and `.TIMESTAMP` are plain strings — do NOT use `.value`
  - Argument order: `verify_signature(payload, signature, timestamp, ec_public_key)`

## Important Patterns

### Payment Plan Status
- Model default is lowercase `"active"` — always use `.ilike("active")` in queries to avoid case mismatch bugs

### Manual Payment Splits
When splitting a payment between two users:
1. UPDATE the original payment amount
2. INSERT a new payment for the other user
3. Run `update_financial_status(user_id)` for both users

### Financial Status
- Recalculated via `update_financial_status(user_id)` in `sigma_finance/utils/status_updater.py`
- A user is "financial" if they have a $200 one-time payment this year OR a completed payment plan this year
- Cache invalidation: call `invalidate_payment_cache()`, `invalidate_user_cache(user_id)`, `invalidate_plan_cache()` after payment changes

### Database Migrations
```bash
flask db upgrade  # runs via build command on Render
```

## Common Pitfalls
- Plan status case sensitivity: always query with `.ilike("active")`, never `== "Active"` or `== "active"`
- SendGrid library quirks: check the installed version (6.12.4) before assuming enum vs string behavior
- Render Secret Files vs env vars: secret files mount at `/etc/secrets/<name>`, changes require a redeploy to take effect

## DISTILLED_AESTHETICS_PROMPT = """
<frontend_aesthetics>
You tend to converge toward generic, "on distribution" outputs. In frontend design, this creates what users call the "AI slop" aesthetic. Avoid this: make creative, distinctive frontends that surprise and delight. Focus on:

Typography: Choose fonts that are beautiful, unique, and interesting. Avoid generic fonts like Arial and Inter; opt instead for distinctive choices that elevate the frontend's aesthetics.

Color & Theme: Commit to a cohesive aesthetic. Use CSS variables for consistency. Dominant colors with sharp accents outperform timid, evenly-distributed palettes. Draw from IDE themes and cultural aesthetics for inspiration.

Motion: Use animations for effects and micro-interactions. Prioritize CSS-only solutions for HTML. Use Motion library for React when available. Focus on high-impact moments: one well-orchestrated page load with staggered reveals (animation-delay) creates more delight than scattered micro-interactions.

Backgrounds: Create atmosphere and depth rather than defaulting to solid colors. Layer CSS gradients, use geometric patterns, or add contextual effects that match the overall aesthetic.

Avoid generic AI-generated aesthetics:
- Overused font families (Inter, Roboto, Arial, system fonts)
- Clichéd color schemes (particularly purple gradients on white backgrounds)
- Predictable layouts and component patterns
- Cookie-cutter design that lacks context-specific character

Interpret creatively and make unexpected choices that feel genuinely designed for the context. Vary between light and dark themes, different fonts, different aesthetics. You still tend to converge on common choices (Space Grotesk, for example) across generations. Avoid this: it is critical that you think outside the box!
</frontend_aesthetics>
"""
