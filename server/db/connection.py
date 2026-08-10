from logging import error

import aiosqlite

from server.db.schema import run_schemas
from utils.errors import handle_sqlite

db_path = "../../main.db"

async def setup_data_base_connection() -> aiosqlite.Connection | None:
    try:
        connection = await aiosqlite.connect(database=db_path)
        if not connection:
            error("DB Connection failed to start.")
        return connection
    except Exception as e:
        handle_sqlite(error=e)

    return #Always return none if no db connection could be made



async def create_init_db():
    con = await setup_data_base_connection()
    if not con:
        return
    await run_schemas(con)
    return con