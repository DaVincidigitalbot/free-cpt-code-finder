# CLINICAL CASE LOG MEMORY

Last updated: 2026-04-06
Project: Avenyx.com
Repo location: `~/Desktop/Avenyx/`

## What exists
- Flask/Gunicorn app on Render
- SQLite currently in use, but persistence is fragile and PostgreSQL migration is still needed
- Chrome extension for ACGME export
- live Stripe subscription flow
- admin access endpoint exists

## Business state
- real users exist
- zero paying customers so far
- main diagnosis: distribution problem, not product problem
- currently secondary priority behind FreeCPTCodeFinder

## Account/subscription/admin state
- annual subscription pricing live at $49.99/year
- Stripe is connected in live mode
- admin access exists and is operational
- user/account/admin/subscription work matters because it underpins real user trust even if growth is lagging

## Current concerns
- SQLite is not the right long-term persistence layer
- distribution and acquisition are the bottleneck
- product stability matters because real users already exist

## Known limitations
- app is not yet on hardened persistent database infrastructure
- commercial traction remains weak despite product viability

## What to update after changes
- any admin workflow change
- any subscription logic change
- any database/auth/account system change
- any major user or distribution milestone
