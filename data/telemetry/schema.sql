-- Privacy-safe Case Builder telemetry schema.
-- Stores aggregate CPT/workflow signals only. Do not store IPs, emails, user ids,
-- patient identifiers, operative notes, dates of service, free text, or comments.

CREATE TABLE IF NOT EXISTS telemetry_import_audit (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  schema_version TEXT NOT NULL,
  deployed_commit TEXT,
  activated_at TEXT NOT NULL,
  activated_by TEXT,
  notes TEXT
);

CREATE TABLE IF NOT EXISTS telemetry_daily_case_combinations (
  event_date TEXT NOT NULL,
  cpt_combination TEXT NOT NULL,
  primary_cpt TEXT NOT NULL,
  secondary_cpt TEXT,
  tertiary_cpt TEXT,
  specialty_category TEXT,
  cpt_count INTEGER NOT NULL DEFAULT 0,
  modifier_count INTEGER NOT NULL DEFAULT 0,
  ncci_warning_count INTEGER NOT NULL DEFAULT 0,
  payable_exclusion_count INTEGER NOT NULL DEFAULT 0,
  selected_wrvu_sum REAL NOT NULL DEFAULT 0,
  payable_wrvu_sum REAL NOT NULL DEFAULT 0,
  sessions INTEGER NOT NULL DEFAULT 0,
  PRIMARY KEY (event_date, cpt_combination, specialty_category)
);

CREATE TABLE IF NOT EXISTS telemetry_daily_ncci_events (
  event_date TEXT NOT NULL,
  cpt_pair TEXT NOT NULL,
  column1 TEXT NOT NULL,
  column2 TEXT NOT NULL,
  modifier_indicator TEXT NOT NULL,
  edit_severity TEXT NOT NULL CHECK (edit_severity IN ('hard_stop','warning')),
  selected_wrvu_sum REAL NOT NULL DEFAULT 0,
  payable_wrvu_sum REAL NOT NULL DEFAULT 0,
  suppressed_wrvu_sum REAL NOT NULL DEFAULT 0,
  events INTEGER NOT NULL DEFAULT 0,
  PRIMARY KEY (event_date, cpt_pair, modifier_indicator, edit_severity)
);

CREATE TABLE IF NOT EXISTS telemetry_daily_modifier_usage (
  event_date TEXT NOT NULL,
  modifier TEXT NOT NULL,
  cpt_combination TEXT,
  events INTEGER NOT NULL DEFAULT 0,
  PRIMARY KEY (event_date, modifier, cpt_combination)
);

CREATE TABLE IF NOT EXISTS telemetry_daily_searches (
  event_date TEXT NOT NULL,
  search_kind TEXT NOT NULL,
  search_code TEXT,
  result_selected TEXT,
  success INTEGER NOT NULL DEFAULT 0,
  did_you_mean_used INTEGER NOT NULL DEFAULT 0,
  searches INTEGER NOT NULL DEFAULT 0,
  PRIMARY KEY (event_date, search_kind, search_code, result_selected, success, did_you_mean_used)
);

CREATE TABLE IF NOT EXISTS telemetry_daily_workflow_summary (
  event_date TEXT PRIMARY KEY,
  case_builder_sessions INTEGER NOT NULL DEFAULT 0,
  total_cpts_entered INTEGER NOT NULL DEFAULT 0,
  total_modifiers_used INTEGER NOT NULL DEFAULT 0,
  total_ncci_warnings INTEGER NOT NULL DEFAULT 0,
  total_payable_exclusions INTEGER NOT NULL DEFAULT 0,
  selected_wrvu_sum REAL NOT NULL DEFAULT 0,
  payable_wrvu_sum REAL NOT NULL DEFAULT 0,
  suppressed_wrvu_sum REAL NOT NULL DEFAULT 0
);

CREATE INDEX IF NOT EXISTS idx_telemetry_case_combo_sessions
  ON telemetry_daily_case_combinations (sessions DESC);

CREATE INDEX IF NOT EXISTS idx_telemetry_ncci_suppressed
  ON telemetry_daily_ncci_events (suppressed_wrvu_sum DESC);

CREATE INDEX IF NOT EXISTS idx_telemetry_searches
  ON telemetry_daily_searches (searches DESC);
