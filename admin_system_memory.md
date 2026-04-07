# ADMIN SYSTEM MEMORY

Last updated: 2026-04-06
Scope: admin/security/account-control memory across active products, especially ClinicalCaseLog.

## What exists
- admin endpoint/access pattern for ClinicalCaseLog
- live Stripe-backed subscription environment
- operational need for secure admin and role-bound access
- expectation of secure admin RBAC direction even if not fully formalized in this repo

## Current state
- admin functionality exists and should be treated as sensitive production capability
- secure admin/account handling is part of the active system memory because account/admin changes have downstream billing and subscription consequences
- if RBAC/security changes are made, they must be documented here immediately

## Security posture reminders
- do not expose admin flows casually
- treat any admin/account/subscription changes as high-impact
- document privilege changes, account-role changes, or security-hardening decisions here

## Known limitations
- this memory file is partly anticipatory because admin logic lives more directly in ClinicalCaseLog repo than FreeCPTCodeFinder repo
- full RBAC implementation details are not captured here yet and must be added when touched

## What to update after changes
- RBAC/role changes
- admin auth changes
- security hardening decisions
- account management workflow changes
- subscription privilege logic
