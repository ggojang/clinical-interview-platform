CREATE TABLE IF NOT EXISTS test_access_events (
  id TEXT PRIMARY KEY,
  created_at TEXT NOT NULL,
  event_type TEXT NOT NULL CHECK (event_type = 'tracked_entry_opened')
);

CREATE INDEX IF NOT EXISTS test_access_created_at_idx
  ON test_access_events(created_at);
