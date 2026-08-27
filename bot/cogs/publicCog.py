from uuid import UUID, uuid4

from discord import Member, User
from discord.ext.commands import Cog, Bot, Context

from config import settings
from server.db.access import get_code_from_user_id, create_link
from utils.commandUtils import chybrid_command, attempt_ephemeral


async def get_safe_code(user: Member | User) -> UUID:
    code = await get_code_from_user_id(
        user.id
    )
    if code is not None:
        return code

    code = uuid4()
    await create_link(
        member=user,
        code_uuid=code
    )
    return code


class PublicCog(Cog):

    def __init__(self, botClient: Bot):
        self.botClient = botClient

    @chybrid_command(
        name="appcode",
        description="Link your discord account to a unique code.",
        guilds=[settings.authorized_guild]
    )
    async def app_code(self, ctx: Context):
        code = await get_safe_code(ctx.author)
        if ctx.interaction:
            await attempt_ephemeral(
                ctx=ctx,
                reply=f"Your code is: \n ```{code.hex}```"
            )
        else:
            await ctx.author.send(
                content=f"Your code is: \n ```{code.hex}```"
            )


async def setup(botClient: Bot):
    await botClient.add_cog(PublicCog(botClient=botClient))