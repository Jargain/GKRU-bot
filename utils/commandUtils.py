import discord
from discord import app_commands
from discord.ext import commands
from utils.permissions import is_bot_admin_ctx

def chybrid_command(
    *,
    name: str,
    description: str | None = None,
    guilds: list[int] | None = None,
    default_permissions: discord.Permissions | None = None,
    bot_admin: bool | None = None,
    **kwargs,
):
    def decorator(func):
        if guilds is not None:
            func = app_commands.guilds(*guilds)(func)

        if default_permissions is not None:
            func = app_commands.default_permissions(default_permissions)(func)

        if bot_admin:
            func = commands.check(is_bot_admin_ctx)(func)

        cmd_kwargs = {
            "name": name,
            "with_app_command": True,
            **kwargs,
        }

        if description is not None:
            cmd_kwargs["description"] = description

        return commands.hybrid_command(**cmd_kwargs)(func)

    return decorator