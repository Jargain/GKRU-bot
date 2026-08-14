import asyncio
from asyncio import FIRST_COMPLETED, CancelledError

from discord import Client

import config
from loguru import logger
from server.db.access import start_db, stop_db
from bot.modules.startup import startup
from server.web.app import startServer
from utils.logging import setup_logging

client: Client

pending: set

headless = False

async def setup():
    logger.debug("Syncing main db")
    await start_db()
    logger.debug("Main Database Created.")

async def main_server():
    logger.info("Starting server inner...")
    try:
        await startServer()
    except Exception as e:
        logger.error(f"Failed to start server: {e}")
    return

async def main_bot():
    logger.info("Starting bot inner")
    await startup()
    return

async def cleanup():
    logger.debug("Stopping db...")
    await stop_db()
    logger.debug("Closing client...")
    if config.apiClient:
        await config.apiClient.close()
    logger.debug("Shutting lurkr down.")
    config.lurkr_close()
    logger.info("Shutdown inner ring complete.")

async def _run():
    try:
        await setup()
        BOTTASK = asyncio.create_task(main_bot())
        SERVERTASK = asyncio.create_task(main_server())
        global pending
        completed, pending = await asyncio.wait(
            [BOTTASK, SERVERTASK],
            return_when=FIRST_COMPLETED
        )
        for task in pending:
            task.cancel()

        await asyncio.gather(
            *pending,
            return_exceptions=True
        )

    except (KeyboardInterrupt, CancelledError):
        logger.debug("KeyboardInterrupt received, cleaning up...")
    finally:
        await cleanup()


if __name__ == "__main__":
    setup_logging()

    try:
        logger.debug("Starting setup process")
        asyncio.run(_run())

    except KeyboardInterrupt:
        logger.debug("Shut down finished.")
    except Exception as e:
        logger.error(f"Failed due to: {e}")
        import traceback
        traceback.print_exc()