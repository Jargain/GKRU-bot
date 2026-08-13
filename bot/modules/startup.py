import mimetypes

from discord import Client, Intents, Status, CustomActivity, PartialEmoji
from discord.ext.commands import Bot, Cog
from loguru import logger

from config import bot_token, cogs_dir, setApiClient, authorized_guild
from utils.runtimeUtils import startBot
from bot.cogs.utilsCog import try_update_restart_message
import os



async def register_cogs(client: Bot):
    cogs = os.listdir(cogs_dir)
    for cog in cogs:
        if "python" not in str(mimetypes.guess_type(cog)[0]):
            continue
        cog_path = f"bot.cogs.{cog[:-3]}"
        logger.debug(f"Registering: {cog_path}")
        try:
            await client.load_extension(cog_path)
        except Exception as e:
            logger.error(f"Failed to register cog ({cog}): {e}")
    ping = client.tree.get_command("ping")
    if not ping:
        logger.warning("Ping command not registered!")
    else:
        logger.debug("Ping command registered.")
    logger.info("Registered all extensions")

async def sync_cmds(client: Bot, guild_id: int):
    guild = client.get_guild(guild_id)
    if not guild:
        logger.error(f"Unable to get guild for sync: {guild_id}")
        return
    try:
        logger.info(f"Attempting sync with guild: {guild.name} ({guild.id})")
        client.tree.copy_global_to(guild=guild)
        await client.tree.sync(guild=guild)
        logger.info("Synced successfully!")
    except Exception as e:
        logger.error(f"Encountered exception while attempting to sync: {e}")
        return
    cmds_from_guild = [cmd.name for cmd in await client.tree.fetch_commands(guild=guild)]
    logger.debug(f"Commands registered on the guild: {cmds_from_guild}")

async def onReady(botClient: Bot):
    logger.debug("Starting onReady")
    try:
        setApiClient(botClient)
        emoji = PartialEmoji.from_str("<a:E_sorry_bow:1209162206172938350>", client=botClient)
        activity = CustomActivity(
            name=f"Running on bad sleep",
            emoji=emoji
        )
        await botClient.change_presence(
            activity=activity,
            status=Status.idle  # idle bcz testing yk
        )
        await sync_cmds(botClient, authorized_guild)
        cmds = [cmd.name for cmd in botClient.tree.get_commands()]
        logger.debug(f"Global commands: {cmds}")
        await try_update_restart_message(botClient)
        logger.info("OnReady finished")
    except Exception as e:
        logger.error(f"Failed to run onReady: {e}")
        import traceback
        traceback.print_exc()

async def setup_hook(botClient: Bot):
    await register_cogs(client=botClient)

async def startup():
    token = bot_token
    logger.debug(f"Token is: {token[10:]}")
    logger.debug(f"Bot Token is {bot_token[10:]}")
    if not token:
        raise ValueError("BOT TOKEN IS NONE OH SHITTINGS")
    logger.info("Registering bot...")
    logger.debug("getting intents")
    intents = Intents.all()
    logger.debug("Creating client")
    client = Bot(
        intents=intents,
        command_prefix="./"
    )

    async def _setup_hook():
        await setup_hook(botClient=client)

    client.setup_hook = _setup_hook

    @client.event
    async def on_ready():
        await onReady(client)

    await startBot(token, client)


