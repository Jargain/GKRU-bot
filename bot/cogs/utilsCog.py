import asyncio
import datetime
from time import time
from typing import Optional

from discord import app_commands, Embed, Color, permissions, Member
from discord.ext import commands
from discord.ext.commands import Bot, hybrid_command, Context
from loguru import logger

from config import authorized_guild
from server.db.access import get_restart, clear_restart, log_restart
from utils.permissions import is_bot_admin
from utils.runtimeUtils import queRestart, stopAll

#please work yo pleeeaasseee
async def get_difference(time_in_s: int):
    diff = int(time()) - time_in_s
    return diff

async def build_restart_embed(restart_complete: bool, time_in_s: Optional[int]) -> Embed:
    red_color = Color.dark_red()
    green_color = Color.green()
    color = green_color if restart_complete else red_color
    completed_text = "Restart completed!"
    scheduled_text = "Restart has started, this message will be updated once complete."
    embed = Embed(
        color=color,
        title="Restart Notification"
    )
    if time_in_s:
        diff = await get_difference(time_in_s)
        embed.add_field(name="Restart duration", value=f"{diff} seconds")
    embed.description = completed_text if restart_complete else scheduled_text
    return embed

async def _build_shutdown_embed() -> Embed:
    color = Color.green()
    embed = Embed(
        color=color,
        timestamp=datetime.datetime.now(),
        title="Shutdown Notification",
        description="Shutting down in 10 seconds. This message will be deleted automatically."
    )
    return embed

async def try_update_restart_message(botClient: Bot):

    entry = await get_restart()
    if not entry:
        return
    time_in_s = entry[0]
    message_id = entry[2]
    channel_id = entry[3]
    embed = await build_restart_embed(True, time_in_s)

    try:
        channel= botClient.get_channel(channel_id)
        message = channel.get_partial_message(message_id)
        await message.edit(
            embed=embed
        )
    except Exception as e:
        logger.error(f"Unable to update message: {e}")
    finally:
        await clear_restart()

class utils(commands.Cog):
    def __init__(self, bot: Bot):
        self.bot = bot
        self.build_restart_embed = build_restart_embed

    @hybrid_command(name="ping", with_app_command=True, description="Replies with the ping to discord servers.")
    async def ping(self, ctx: Context):
        latency = self.bot.latency
        await ctx.reply(str(latency))

    @hybrid_command(name="say", with_app_command=True)
    @app_commands.guilds(authorized_guild)
    async def say(self, ctx: Context, text: str):
        await ctx.send(text)

    @hybrid_command(
        name="restart",
        with_app_command=True,
        description="A classic, you need to be a bot admin for this one to work.",
    )
    @app_commands.default_permissions(
        permissions.Permissions.elevated()
    )
    @app_commands.guilds(authorized_guild)
    async def restart(self, ctx: Context):
        member : Member = ctx.author

        if not Member:
            return

        if not await is_bot_admin(member):
            await ctx.reply(
                content="You need to be a bot administrator to do this."
            )
            return

        arguments = ""
        embed = await self.build_restart_embed(False, None)
        msg = await ctx.reply(
            embed=embed
        )
        logger.debug("Logging restart entry...")
        await log_restart(
            user=ctx.author.id,
            channel=ctx.channel.id,
            message=msg.id,
            arguments=arguments
        )
        asyncio.create_task(
            queRestart(botClient=self.bot)
        )

    @hybrid_command(
        name="shutdown",
        with_app_command=True,
        description="Another classic, you need to be a bot admin for this one to work.",
    )
    @app_commands.default_permissions(
        permissions.Permissions.elevated()
    )
    @app_commands.guilds(authorized_guild)
    async def shut_down(self, ctx: Context):
        member : Member = ctx.author

        if not Member:
            return

        if not await is_bot_admin(member):
            await ctx.reply(
                content="You need to be a bot administrator to do this."
            )
            return
        logger.info(f"Shutting down from command ran by {member.display_name} ( {member.name} | {member.id})")

        message = await ctx.reply(
            embed=await _build_shutdown_embed()
        )
        await asyncio.sleep(10.0)
        await message.delete()
        await stopAll(self.bot)


async def setup(bot: Bot):
    await bot.add_cog(utils(bot))