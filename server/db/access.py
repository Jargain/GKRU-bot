import asyncio
from time import time
from typing import Optional

import aiosqlite
from discord import Message
from loguru import logger

from server.db.connection import create_init_db

con: Optional[aiosqlite.Connection] = None

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

