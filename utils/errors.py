from discord import Embed, Color
from discord.ext.commands import CommandError, Context, Bot

from config import settings


def build_error_embed(
        error: CommandError,
) -> Embed:
    file = error.__traceback__.tb_frame.f_code.co_filename
    line = error.__traceback__.tb_lineno
    reason = str(error)
    embed = Embed(
        color=Color.brand_red(),
        title="Error Occurred!",
        description=f"New exception: {reason} \n Line number: {line} \n File: {file}"
    )
    return embed

class PermissionCheckError(CommandError):
    """Raised when a user does not have the needed permissions."""
    pass

class InteractionMessageNone(CommandError):
    """Raised when an interaction.message is None or another error has occurred."""
    pass

async def onCommandError(ctx: Context, error: CommandError, botClient: Bot):

    if isinstance(error, PermissionCheckError):

        message = str(error)

        if ctx.interaction:
            await ctx.interaction.response.send_message(
                content=message,
                ephemeral=True,
                delete_after=10
            )
        else:
            await ctx.send(
                content=message,
                delete_after=5
            )
        return

    embed = build_error_embed(error)
    for admin_id in settings.bot_administrators:
        admin = botClient.get_user(admin_id)
        if admin:
            await admin.send(
                embed=embed
            )