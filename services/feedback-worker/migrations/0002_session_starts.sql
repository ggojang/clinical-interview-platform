CREATE TABLE IF NOT EXISTS test_session_starts (
  id TEXT PRIMARY KEY,
  client_session_id TEXT NOT NULL UNIQUE,
  created_at TEXT NOT NULL,
  event_type TEXT NOT NULL CHECK (event_type = 'session_started'),
  gpt_config_version TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS session_start_created_at_idx
  ON test_session_starts(created_at);
CREATE INDEX IF NOT EXISTS session_start_config_version_idx
  ON test_session_starts(gpt_config_version);
