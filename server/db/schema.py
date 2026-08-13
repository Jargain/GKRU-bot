import hashlib
from loguru import logger
from sqlite3 import DatabaseError
import os
import aiosqlite
from config import schema_migrations_dir

async def get_schema_cursor(con: aiosqlite.Connection):
    await con.execute("""
    CREATE TABLE IF NOT EXISTS schema (
        schema INTEGER PRIMARY KEY,
        schema_name TEXT,
        schema_checksum TEXT
    );
    """)
    await con.commit()
    curs = await con.cursor()
    return curs or None

async def get_schema_id_from_file_name(name: str):
    version, name = name.split("_",1)
    return (version, name)

async def get_last_schema_num(con: aiosqlite.Connection):
    async with con.execute("SELECT schema, schema_name FROM schema ORDER BY schema DESC LIMIT 1") as cursor:
        row = await cursor.fetchone()
        return row if row else (0, None)

def get_checksum(item: str):
    with open(item, "rb") as f:
        return str(hashlib.file_digest(f, 'sha256').hexdigest())

async def build_schema_table():
    table = {}
    list = os.listdir(schema_migrations_dir)
    logger.debug(f"Create list: {list}")
    for item in list:
        value, name = await get_schema_id_from_file_name(item)
        item_path = f"{schema_migrations_dir}/{item}"
        with open(item_path) as f:
            content = f.read()
            checksum = get_checksum(item=item_path)
            item = {
                "checksum": checksum,
                "name": name,
                "content": content,
                "index": value
            }
            table[int(value)] = item
            logger.debug(f"'Created item: {item}")
    logger.debug(f"Created schema table")
    return table

async def run_schema(schema_item, con: aiosqlite.Connection):
    await con.executescript(schema_item["content"])

async def log_schema(schema_item, schema_cursor: aiosqlite.Cursor):
    schema = schema_item["index"]
    schema_name = schema_item["name"]
    schema_checksum = schema_item["checksum"]
    await schema_cursor.execute(
        f"""
        INSERT INTO schema (schema, schema_name, schema_checksum)
            VALUES (?, ?, ?)
        """,
        (schema, schema_name, schema_checksum)
    )

async def run_schemas_from(schema_start: int, schema_cursor: aiosqlite.Cursor, con: aiosqlite.Connection):
    schema_table = await build_schema_table()
    sorted_items = [schema_table[k] for k in sorted(schema_table.keys())]
    for schema_item in sorted_items[schema_start-1:]:
        await run_schema(schema_item=schema_item, con=con)
        await log_schema(schema_item=schema_item, schema_cursor=schema_cursor)
    await schema_cursor.close()
    await con.commit()

async def run_schemas(con: aiosqlite.Connection):
    schema_cursor = await get_schema_cursor(con)
    if not schema_cursor:
        logger.error("Unable to create schema cursor!")
        raise DatabaseError
    latest_schem_entry_val, name = await get_last_schema_num(con)
    start = latest_schem_entry_val+1 if latest_schem_entry_val else 1
    await run_schemas_from(start,schema_cursor, con)
    logger.debug("Ran schemas!")



