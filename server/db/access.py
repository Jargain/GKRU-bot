import asyncio
import uuid
from time import time
from typing import Optional
from uuid import UUID

import aiosqlite
from aiosqlite import cursor
from discord import Message, Member, User
from loguru import logger

from server.db.connection import create_init_db

con: Optional[aiosqlite.Connection] = None

lookup_eligible = ["modlogs","moderators"]

async def start_db():
    global con
    con = await create_init_db()

async def stop_db():
    global con
    if not con:
        return
    await con.commit()
    await con.close()
    #i know there should be more here, but meh, good enough icl

async def log_restart(
        message: int,
        channel: int,
        user: int,
        arguments: str,
) -> None:
    logger.debug("Logging restart entry from db this time")
    cursor = await con.cursor()
    await cursor.execute(
    """
    INSERT INTO restart (time, requester_id, message_id, channel_id, arguments)
        VALUES (?,?,?,?,?)
    """, (int(time()), user, message, channel, arguments)
    )
    await con.commit()
    await cursor.close()

async def get_restart():
    cursor = await con.cursor()
    await cursor.execute("SELECT * FROM restart ORDER BY time DESC LIMIT 1")
    last_restart = await cursor.fetchone()
    await cursor.close()
    return last_restart

async def clear_restart():
    cursor = await con.cursor()
    await cursor.execute("""
    DELETE FROM restart
    """)
    await cursor.close()

async def log_audit(
        user_id: int,
        action: str
):
    cursor = await con.cursor()
    await cursor.execute("""
        INSERT INTO audit_log (discord_userid, action, time)
            VALUES (?, ?, ?)
    """, (user_id, action, int(time()))
    )
    await cursor.close()

async def get_audit_from(
        user_id: int
):
    cursor = await con.cursor()
    await cursor.execute("""SELECT * FROM audit_log WHERE discord_userid = ?""", [user_id] )
    audit_logs = await cursor.fetchall()
    await cursor.close()
    return audit_logs

async def get_audit_from_action(
        user_id: int,
        action: str
):
    cursor = await con.cursor()
    await cursor.execute("""SELECT * FROM audit_log WHERE discord_userid = ? AND action LIKE ?% """, (user_id, action))
    audit_logs = await cursor.fetchall()
    await cursor.close()
    return audit_logs

async def get_audit_action(
        action: str
):
    cursor = await con.cursor()
    await cursor.execute("""SELECT * FROM audit_log WHERE action LIKE ?% """, [action])
    audit_logs = await cursor.fetchall()
    await cursor.close()
    return audit_logs

async def create_link(
        member: Member | User,
        code_uuid: UUID
):
    cursor = await con.cursor()
    await cursor.execute("""
        INSERT INTO discord_link (code_uuid, username, userid)
            VALUES (?, ?, ?)
    """, (str(code_uuid.hex), member.name, member.id)
    )
    await cursor.close()

async def get_user_id_from_code(
        code: str
) -> int | None:
    cursor = await con.cursor()
    await cursor.execute("""
        SELECT * FROM discord_link WHERE code_uuid = ?
    """, [code])
    userid = await cursor.fetchone()
    await cursor.close()
    return userid[2] if userid is not None else None

async def get_code_from_user_id(
        userid: int
) -> UUID | None:
    cursor = await con.cursor()
    await cursor.execute("""
        SELECT * FROM discord_link WHERE userid = ?
    """, [userid])
    code = await cursor.fetchone()
    await cursor.close()
    return UUID(hex=code[0]) if code is not None else None


