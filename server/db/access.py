import asyncio

from connection import create_init_db

import logging
logging.basicConfig(level=logging.DEBUG)

asyncio.run(create_init_db())

