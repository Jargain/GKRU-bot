CREATE TABLE IF NOT EXISTS ban_table (
        case_uuid TEXT PRIMARY KEY,
        time INTEGER,
        ban_reason TEXT,
        ban_duration TEXT,
        appeal_able TEXT,
        roblox_username TEXT,
        roblox_userid TEXT,
        discord_username TEXT,
        discord_userid TEXT,
        unbanned INTEGER,
        unban_date INTEGER,
        unban_reason TEXT,
        moderator_uuid TEXT
);
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
        time INTEGER,
);

