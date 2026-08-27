from discord import Member, app_commands
from discord.ext import commands
from discord.ext.commands import Bot, Context
from loguru import logger

from config import settings
from utils.commandUtils import chybrid_command
from bot.modules.moderation import LoaModal, attempt_log

class ModerationCog(commands.Cog):

    def __init__(self, botClient: Bot):
        self.bot = botClient

    @chybrid_command(
        name="loa",
        description="Send an LoA notice to the current administrators",
        permission_int=1,
        guilds=[settings.authorized_guild]
    )
    async def loa(self, ctx: Context):
        try:
            if not ctx.interaction:
                await ctx.send(
                    content="Sorry, please use the slash command, this command does not support text commands.",
                    delete_after=5
                )
                return

            logger.debug("Creating modal...")
            modal = LoaModal(
                botClient=self.bot
            )
            logger.debug("Sending modal...")
            await ctx.interaction.response.send_modal(modal)
            await ctx.interaction.followup.send(
                content="LOA Modal Opened.",
                ephemeral=True
            )
        except Exception as e:
            logger.warning(f"Failed to create modal: {e}")

    @chybrid_command(
        name="log",
        description="Creates a new log for a moderation action taken.",
        permission_int=2,
        guilds=[settings.authorized_guild]
    )
    @app_commands.describe(
        member="The person that an action will be taken  against.",
        reason="The reason for the moderation action taken.",
        action="The moderation action taken"
    )
    async def log(self, ctx: Context, member: Member, reason: str, action: str):
        log_msg = await attempt_log(
            moderator=ctx.author,
            member=member,
            reason=reason,
            action=action,
            botClient=self.bot
        )
        if log_msg is not None:
            if ctx.interaction:
                await ctx.interaction.response.send_message(
                    content=log_msg.jump_url,
                    ephemeral=True
                )
            else:
                await ctx.reply(
                    content=log_msg.jump_url,
                    delete_after=5
                )
        else:
            if ctx.interaction:
                await ctx.interaction.response.send_message(
                    content="Failed to create log message.",
                    ephemeral=True
                )
            else:
                await ctx.reply(
                    content="Failed to create log message.",
                    delete_after=5
                )


async def setup(bot: Bot):
    await bot.add_cog(ModerationCog(bot))