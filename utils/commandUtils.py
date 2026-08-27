from typing import Optional

import discord
from discord import app_commands, Embed
from discord.utils import MISSING
from discord.ext import commands
from discord.ext.commands import Context

from utils.errors import PermissionCheckError
from utils.permissions import is_bot_admin_ctx, has_permission_integer

async def attempt_ephemeral(ctx: Context, reply: str | MISSING = MISSING, embed: Embed | MISSING = MISSING, delete_after: int | MISSING = 5):
    if ctx.interaction:
        await ctx.interaction.response.send_message(
            content=reply,
            embed=embed,
            ephemeral=True
        )
    else:
        await ctx.reply(
            content=reply,
            embed=embed,
            delete_after=delete_after
        )

def chybrid_command(
    *,
    name: str,
    description: str | None = None,
    guilds: list[int] | None = None,
    default_permissions: discord.Permissions | None = None,
    bot_admin: bool | None = None,
    permission_int: int | None = None,
    **kwargs,
):
    def decorator(func):
        if guilds is not None:
            func = app_commands.guilds(*guilds)(func)

        if default_permissions is not None:
            func = app_commands.default_permissions(default_permissions)(func)

        if bot_admin:
            async def bot_admin_check(ctx):
                if not await is_bot_admin_ctx(ctx):
                    raise PermissionCheckError("Sorry, you need to be a bot administrator to run this command.")
                return True
            func = commands.check(bot_admin_check)(func)

        if permission_int is not None:
            async def perm_check(ctx):
                if not await has_permission_integer(ctx, permission_int):
                    raise PermissionCheckError("Sorry, you need to have a higher permission integer to run this command.")
                return True
            func = commands.check(perm_check)(func)

        cmd_kwargs = {
            "name": name,
            "with_app_command": True,
            **kwargs,
        }

        if description is not None:
            cmd_kwargs["description"] = description

        return commands.hybrid_command(**cmd_kwargs)(func)

    return decorator