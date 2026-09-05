from datetime import datetime

from discord import Member, Embed, Color
from discord.ext.commands import Cog, Bot, Context

import config
from config import settings
from server.db.access import log_event
from utils.adminUtils import give_access
from utils.commandUtils import attempt_ephemeral, chybrid_command
from utils.enums import eventAccess
from utils.viewUtils import ClassView


def build_class_embed(user: Member):
    embed = Embed(
        title="Class started!",
        description=f"Class currently being hosted by {user.display_name} ({user.id})",
        color=Color.brand_green(),
        timestamp=datetime.now()
    )
    embed.set_thumbnail(
        url=user.avatar.url if user.avatar else user.default_avatar.url
    )
    return embed

class EventCog(Cog):

    def __init__(self, botClient: Bot):
        self.botClient = botClient

    @chybrid_command(
        name="startclass",
        description="This commands starts a class.",
        permission_int=1,
        guilds=[settings.authorized_guild]
    )
    async def start_class(self, ctx: Context):
        if not (config.class_count < 1):
            await attempt_ephemeral(
                ctx, "Sorry, a class is currently being hosted."
            )
            return

        if not isinstance(ctx.author, Member):
            await attempt_ephemeral(
                ctx, "Sorry, you need to be in a server for this command to work."
            )
            return
        await attempt_ephemeral(
            ctx, "Class started!"
        )

        await log_event(
            ctx.author, eventAccess.Start
        )
        class_channel = await self.botClient.fetch_channel(settings.class_channel)
        await ctx.channel.send(
            embed=build_class_embed(ctx.author),
            view=ClassView(owner=ctx.author, channel=class_channel)
        )

        await give_access(ctx.author, class_channel)
        config.class_count += 1


async def setup(botClient: Bot):
    await botClient.add_cog(EventCog(botClient))