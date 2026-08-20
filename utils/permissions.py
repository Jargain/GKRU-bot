import discord
from discord.ext.commands import Context

from config import bot_administrators, authorized_guild, apiClient

async def has_ban_permission(user: discord.Member) -> bool:
    """
    Check if a member has the ban permission
    :param user: The discord guild member to be checked
    """
    if not apiClient:
        return False
    real_user = apiClient.get_guild(authorized_guild).get_member(user.id)
    if not real_user:
        return False
    perms = real_user.guild_permissions.ban_members or real_user.guild_permissions.administrator
    if perms:
        return True
    return False or await is_bot_admin(real_user)

async def is_admin(user: discord.Member, trueAdmin: bool) -> bool:
    """
    Checks if a user is an administrator (Has Manage server)
    :param user: A guild member to be checked
    :param trueAdmin: Ask for the actual admin position rather than manager server
    """
    if not apiClient:
        return False
    real_user = apiClient.get_guild(authorized_guild).get_member(user.id)
    if not real_user:
        return False
    perms = real_user.guild_permissions.administrator if trueAdmin else real_user.guild_permissions.manage_guild
    if perms:
        return True
    return False or await is_bot_admin(real_user)

async def is_bot_admin(user: discord.Member) -> bool:
    """
    Checks is the given user is a bot administrator.
    :param user: The user to check
    """
    return int(user.id) in bot_administrators

async def is_bot_admin_ctx(ctx: Context) -> bool:
    """
    Checks is the given context author is a bot administrator.
    :param ctx: The Context
    """
    if not isinstance(ctx.author, discord.Member):
        return False
    return await is_bot_admin(ctx.author)