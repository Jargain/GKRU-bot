from loguru import logger

import aiosqlite

from server.db.schema import run_schemas
from config import settings

async def setup_data_base_connection() -> aiosqlite.Connection | None:
    try:
        logger.debug(f"DB Path: {settings.db_path}")
        connection = await aiosqlite.connect(database=settings.db_path)
        if not connection:
            logger.error("DB Connection failed to start.")
        await connection.execute("PRAGMA journal_mode=WAL;")
        await connection.execute("PRAGMA synchronous=NORMAL;")
        await connection.commit()
        return connection
    except Exception as e:
        logger.error(f"Error found while running db: {e}")

    return #Always return none if no db connection could be made



async def create_init_db():
    con = await setup_data_base_connection()
    if not con:
        return
    await run_schemas(con)
    return con