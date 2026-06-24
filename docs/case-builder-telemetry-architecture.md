# Case Builder Telemetry Architecture

Status: review only. Do not deploy until explicitly approved.

## Privacy Boundary

Telemetry is aggregate, anonymous, and CPT-focused only.

Never collect or store:
- Patient names
- MRNs
- Dates of service
- Operative notes
- Free text
- User-entered comments
- IP addresses
- Email addresses
- User identifiers

Important design decision: raw search text is not safe because a user can paste PHI into the search box. The telemetry client classifies searches instead of storing raw terms. It stores exact CPT queries, selected CPT/result codes, and whether the query was unmatched. Unknown raw text is recorded only as unmatched_private_query.

## Events

### case_snapshot

Emitted after Case Builder recalculation when telemetry is enabled.

Allowed fields:
- eventDate, rounded to UTC day
- primaryCpt
- secondaryCpt
- tertiaryCpt
- cptCombination
- cptCount
- modifierSelections
- modifierCount
- specialtyCategory
- ncciWarningCount
- payableExclusionCount
- selectedWrvu
- payableWrvu

### ncci_event

Emitted for payable exclusions or warnings produced by the modifier/NCCI engine.

Allowed fields:
- eventDate, rounded to UTC day
- cptPair
- column1
- column2
- modifierIndicator
- editSeverity: hard_stop or warning
- selectedWrvu
- payableWrvu
- suppressedWrvu

### search_event

Emitted for search result selection, failed search, or did-you-mean interaction.

Allowed fields:
- eventDate, rounded to UTC day
- searchKind: cpt_exact, controlled_cpt_selection, controlled_result_match, unmatched_private_query, or empty
- searchCode
- resultSelected
- resultCount
- success
- didYouMeanUsed

## Storage Architecture

Recommended production storage: Cloudflare Worker + D1.

Flow:
1. Browser telemetry client emits a small validated JSON batch only when FCCF_TELEMETRY_CONFIG.enabled === true.
2. Worker validates schema and allowlists every field.
3. Worker drops all request metadata, including IP-derived headers.
4. Worker writes daily aggregate counters into D1.
5. Dashboard reads aggregate views only.

Why not GA4 for this:
- GA4 is useful for page/event analytics but is weaker for auditable medical-coding workflow tables.
- Case Builder needs pair-level aggregates, NCCI suppression totals, and future modifier/global/LCD/NCD dimensions.
- D1 gives us deterministic retention, schema migration, and exportable reports without user identifiers.

## Retention Policy

Raw client event batches:
- Do not persist raw event rows in production.
- Validate and aggregate synchronously at ingest.
- If temporary queueing is needed, retain for 24 hours maximum and purge after aggregation.

Daily aggregate tables:
- Retain 24 months.
- Monthly rollups can be retained indefinitely because they contain only aggregate CPT/workflow counts.

Audit logs:
- Retain indefinitely for telemetry schema versions, deployment commits, activation dates, and rollback notes.

## Reporting

Daily:
- Top CPT combinations
- Top NCCI-triggered pairs
- Top suppressed wRVU pairs
- Most common modifiers
- Most searched CPTs
- Failed search count
- Case Builder sessions with any NCCI hard stop

Weekly:
- Same metrics with week-over-week changes
- New high-frequency CPT pairs not covered by current NCCI activation
- Modifier usage patterns that suggest education gaps

Monthly:
- NCCI roadmap input
- Top false-confusion risk workflows
- Search/content gaps
- Modifier/global/LCD/NCD warning opportunity list

## Future-Proofing

The event envelope includes schemaVersion and eventType. Future event types can be added without redesigning the storage layer:
- modifier1_override_event
- global_period_warning_event
- lcd_ncd_warning_event
- denial_guidance_event

Each new event must use the same privacy rule: CPT/category/counter data only, no identifiers, no dates of service, no free text.

## Estimated Storage Costs

Assumption: 10,000 Case Builder sessions/month, 3 CPT lines/session, 1.5 search events/session, 5 percent NCCI event rate.

Approximate D1 aggregate footprint:
- Daily aggregate rows: under 15,000/month
- Monthly storage: less than 25 MB
- 24-month retention: less than 600 MB

Expected cost:
- Cloudflare Workers Free/Paid tier: likely $0-$5/month at current traffic.
- Cloudflare D1: likely $0/month initially; low single-digit dollars/month if traffic grows materially.

## Activation Checklist

Before production activation:
1. Deploy Worker/D1 behind a staging endpoint.
2. Confirm Worker strips request headers and stores no raw events.
3. Run privacy validator against the client payload.
4. Enable telemetry for internal staging only.
5. Review dashboard output for 7 days.
6. Enable production with release notes only after approval.

Rollback:
- Set FCCF_TELEMETRY_CONFIG.enabled=false.
- Worker can remain deployed but receives no client events.
- Dashboard continues to show historical aggregates.
