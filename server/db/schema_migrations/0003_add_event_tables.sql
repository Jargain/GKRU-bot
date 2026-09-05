CREATE TABLE IF NOT EXISTS event_logs (
  timestamp INTEGER PRIMARY KEY,
    userid INTEGER,
    access INTEGER
);
CREATE TABLE IF NOT EXISTS admin_logs (
  timestamp INTEGER PRIMARY KEY,
    user_id INTEGER,
    access INTEGER,
    approver_id INTEGER,
    info TEXT
);