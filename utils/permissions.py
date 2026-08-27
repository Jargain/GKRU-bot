import discord
from _testcapi import awaitType
from discord import Member
from discord.ext.commands import Context

from config import settings, apiClient

async def has_ban_permission(user: discord.Member) -> bool:
    """
    Check if a member has the ban permission
    :param user: The discord guild member to be checked
    """
    if not apiClient:
        return False
    real_user = apiClient.get_guild(settings.authorized_guild).get_member(user.id)
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
    real_user = apiClient.get_guild(settings.authorized_guild).get_member(user.id)
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
    return int(user.id) in settings.bot_administrators

async def is_bot_admin_ctx(ctx: Context) -> bool:
    """
    Checks is the given context author is a bot administrator.
    :param ctx: The Context
    """
    if not isinstance(ctx.author, discord.Member):
        return False
    return await is_bot_admin(ctx.author)

async def _find_permission_integer(member: Member):
    highest = 0
    for role in member.roles:
        if (str(role.id) in settings.permission_integer_roles) and settings.permission_integer_roles.get(str(role.id)) > highest:
            highest = settings.permission_integer_roles.get(str(role.id))
    return 8 if await is_bot_admin(member) else highest

async def has_permission_integer(ctx: Context, permission_integer: int):
    """
    Check is the given users role has the needed permission integer.
    1 - Event Staff
    2 - Trial Staff
    3 - Normal Staff
    4 - Senior Staff
    5 - Management

    :param ctx:
    :param permission_integer:
    :return:
    """
    if not isinstance(ctx.author, Member):
        return False
    obtained_int = await _find_permission_integer(ctx.author)
    return (obtained_int >= permission_integer) or await is_bot_admin(ctx.author)