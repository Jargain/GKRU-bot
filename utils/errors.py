from discord.ext.commands import CommandError, Context


class PermissionCheckError(CommandError):
    """Raised when a user does not have the needed permissions."""
    pass

async def onCommandError(ctx: Context, error: CommandError):

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