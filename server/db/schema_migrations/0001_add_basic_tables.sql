CREATE TABLE IF NOT EXISTS mod_logs (
        case_uuid TEXT PRIMARY KEY,
        roblox_username TEXT,
        roblox_userid TEXT,
        discord_username TEXT,
        discord_userid TEXT,
        appeal_able TEXT,
        reason TEXT,
        action TEXT,
        duration INTEGER NOT NULL DEFAULT 0,
        moderator_uuid TEXT,
        time INTEGER
);
CREATE TABLE IF NOT EXISTS restart (
        time INTEGER PRIMARY KEY,
        requester_id INTEGER,
        message_id INTEGER,
        channel_id INTEGER,
        arguments TEXT
);

