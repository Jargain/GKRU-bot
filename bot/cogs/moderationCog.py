from operator import add
from uuid import UUID

from discord import Member, app_commands, Embed, Color, User
from discord.ext import commands
from discord.ext.commands import Bot, Context
from discord.utils import MISSING
from loguru import logger

from config import settings
from server.db.access import get_user_id_from_code
from utils.commandUtils import chybrid_command, attempt_ephemeral
from bot.modules.moderation import LoaModal, attempt_log

def build_member_embed(
        code: str,
        member: Member | User
) -> Embed:
    embed = Embed(
        color=Color.green(),
        title=f"{member.display_name} ( {member.name} | {member.id} )",
        description=f" **Code**: {code} \n \n **Member**: {member.mention}"
    )
    embed.set_thumbnail(url=member.avatar.url if member.avatar is not None else member.default_avatar.url)
    return embed


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
    async def log(self, ctx: Context, member: Member | User, reason: str, action: str):
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

    @chybrid_command(
        name="getlink",
        description="Get the discord user from their generated uuid.",
        guilds=[settings.authorized_guild],
        permission_int=3
    )
    @app_commands.describe(
        code="The code given from the user."
    )
    async def get_link(self, ctx: Context, code: str):
        user_id = await get_user_id_from_code(
            code=code
        )
        if not user_id:
            await attempt_ephemeral(
                ctx, "I couldn't find a user associated with that code."
            )
            return
        user = await self.bot.fetch_user(user_id)
        if not user:
            await attempt_ephemeral(
                ctx, f"I couldn't fetch member: {user_id}"
            )
            return
        embed = build_member_embed(
            code, user
        )
        await attempt_ephemeral(
            ctx, embed=embed, delete_after=MISSING
        )


async def setup(bot: Bot):
    await bot.add_cog(ModerationCog(bot))