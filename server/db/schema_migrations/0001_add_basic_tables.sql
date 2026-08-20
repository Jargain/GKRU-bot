CREATE TABLE IF NOT EXISTS ban (
        case_uuid TEXT PRIMARY KEY,
        appeal_able TEXT,
        reason TEXT,
        duration INTEGER NOT NULL DEFAULT 0,
        moderator_uuid TEXT,
        time INTEGER
);
CREATE TABLE IF NOT EXISTS ban_queue (
        case_uuid TEXT PRIMARY KEY,
        discord_userid INTEGER,
        reason TEXT,
        duration INTEGER NOT NULL DEFAULT 0,
        time INTEGER
);
CREATE TABLE IF NOT EXISTS audit_log (
        discord_userid INTEGER PRIMARY KEY,
        action TEXT,
        time INTEGER,
);
CREATE TABLE IF NOT EXISTS ban_link (
        case_uuid TEXT PRIMARY KEY,
        roblox_userid INTEGER,
        roblox_username TEXT,
        discord_userid INTEGER,
        discord_username TEXT,
        rover_obtained TEXT,
        rover_obtain_date INTEGER,
);
CREATE TABLE IF NOT EXISTS restart (
        time INTEGER PRIMARY KEY,
        requester_id INTEGER,
        message_id INTEGER,
        channel_id INTEGER,
        arguments TEXT
);
CREATE TABLE IF NOT EXISTS moderators (
        moderator_uuid TEXT PRIMARY KEY,
        roblox_userid INTEGER,
        roblox_username TEXT,
        discord_userid INTEGER,
        discord_username TEXT
);

