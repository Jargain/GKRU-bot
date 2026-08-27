from discord import Member, app_commands
from discord.ext import commands
from discord.ext.commands import Bot, Context
from loguru import logger

from config import settings
from utils.commandUtils import chybrid_command, attempt_ephemeral
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
            await attempt_ephemeral(
                ctx, log_msg.jump_url
            )
        else:
            await attempt_ephemeral(
                ctx, "Filed to create log message"
            )


async def setup(bot: Bot):
    await bot.add_cog(ModerationCog(bot))