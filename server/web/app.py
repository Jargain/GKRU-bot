import logging

from loguru import logger
from hypercorn import Config
from hypercorn.asyncio import serve
from quart import Quart
from routes import routes
import config

app = Quart("main")
app.register_blueprint(routes)


async def startServer():
    conf = Config()
    conf.bind = [config.bind_addr]
    conf.accesslog = logging.getLogger("hypercorn.access")
    conf.errorlog = logging.getLogger("hypercorn.error")

    logger.info(f"Running server on: {conf.bind}")
    await serve(app, conf, shutdown_trigger=config.api_shutdown.wait)


@app.while_serving
async def while_serving():
    for name in [
        "hypercorn.access",
        "hypercorn.error"
    ]:
        logg = logging.getLogger(name)
        logg.handlers.clear()
        logg.propagate = True
    yield