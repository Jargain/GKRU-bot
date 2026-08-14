import asyncio
import os
import subprocess
import sys
from pathlib import Path
from typing import Optional

import bot
from discord import Client, Intents, LoginFailure, HTTPException, GatewayNotFound, BaseActivity, CustomActivity, \
    PartialEmoji, Status
from discord.ext.commands import Bot
from loguru import logger

import config
from server.db import access

path = Path('..')
venv_path = Path('../.venv')

async def retry(token: str, max_retry, wait, client: Client):
    tries = 0
    logger.info(f"Starting Attempt {tries+1} for bot start...")
    logger.debug(f"max_retry = {max_retry}, client.is_closed() = {client.is_closed()}")
    while tries < max_retry:
        try:
            await client.start(
                token=token,
                reconnect=True
            )
            break
        except LoginFailure:
            logger.error("Token not valid! Aborting...")
        except HTTPException:
            logger.error("HTTP Error during startup! Aborting...")
        except GatewayNotFound:
            logger.error("Discord down, wrap it up")
        finally:
            if client.is_closed():
                tries+=1
                if tries < max_retry:
                    logger.debug(f"Restarting in {wait} secs...")
                    await asyncio.sleep(wait)
                else:
                    logger.error("Max retries reached, aborting...")

async def startBot(token: str, client: Bot) ->  None:

    max_retry = config.max_retry
    wait = config.retry_CD_s
    await retry(
        token=token,
        max_retry=max_retry,
        wait=wait,
        client=client
    )
    if client.is_closed():
        logger.error("Client disconnected")

def relaunchCurrentProcess(*, scriptPath: str):
    executable = Path(sys.executable)
    target = Path(scriptPath).resolve()
    argv = [str(executable), str(target)]

    try:
        os.chdir(str(target.parent))
        os.execv(str(executable), argv)
    except Exception:
        subprocess.Popen(
            argv,
            cwd=str(target.parent),
            close_fds=True
        )
        os._exit(0)

async def stopAll(botClient: Bot):
    await asyncio.sleep(2.0)
    config.api_shutdown.set()
    config.lurkr_close()
    await botClient.close()

async def queRestart(botClient: Bot):
    await stopAll(botClient)
    working_dir = Path(__file__).parent.parent.resolve()
    script_path = working_dir / "bot.py"
    relaunchCurrentProcess(scriptPath=str(script_path))


