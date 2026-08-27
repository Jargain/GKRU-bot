from discord import Role, app_commands
from discord.ext import commands
from discord.ext.commands import Bot, Context
from loguru import logger

from config import settings
from utils.commandUtils import chybrid_command, attempt_ephemeral


class AdministrationCog(commands.Cog):

    def __init__(self, botClient: Bot):
        self.bot = botClient

    @chybrid_command(
        name="setperm",
        description="Sets the permission integer of the given role.",
        bot_admin=True,
        guilds=[settings.authorized_guild],
    )
    @app_commands.describe(
        role="The role to be linked",
        permission="The permission level that role should be given"
    )
    async def set_perm(self, ctx: Context, role: Role, permission: int):
        try:
            logger.debug("Setting role link...")
            roles = settings.permission_integer_roles
            roles[str(role.id)] = permission
            settings.permission_integer_roles = roles
            logger.debug("Set role link...")
            if settings.permission_integer_roles:
                await attempt_ephemeral(
                    ctx,
                    f"Successfully linked role {role.name} to permission integer {permission}"
                )
            else:
                await attempt_ephemeral(
                    ctx,
                    f"Failed to link {role.name} to permission integer {permission}"
                )
            logger.debug(f"Current role links: {settings.permission_integer_roles}")
        except Exception as e:
            logger.warning(f"Unable to link roles: {e}")

    @chybrid_command(
        name="setevent",
        description="Sets the permission integer of the given role.",
        bot_admin=True,
        guilds=[settings.authorized_guild],
    )
    async def set_event_channel(self, ctx: Context):
        try:
            channels = list(settings.event_channels)
            channels.append(ctx.channel.id)
            settings.event_channels = channels

            if settings.event_channels[-1] == ctx.channel.id:
                logger.debug("Set event channel successfully")
                await attempt_ephemeral(
                    ctx,
                    f"Successfully set channel {ctx.channel.name} as event channel."
                )
            else:
                logger.warning("Did not set event channel successfully")
                await attempt_ephemeral(
                    ctx,
                    "Failed to set event channel."
                )
        except Exception as e:
            logger.warning(f"Failed to set event channel because: {e}")

    @chybrid_command(
        name="setwarn",
        description="Sets the current channel as the warning log channel",
        bot_admin=True,
        guilds=[settings.authorized_guild],
    )
    async def set_warn_channel(self, ctx: Context):
        settings.warn_logs_channel = ctx.channel.id

        if settings.warn_logs_channel == ctx.channel.id:
            await attempt_ephemeral(
                ctx,
                f"Successfully set channel {ctx.channel.name} as warning channel."
            )
        else:
            await attempt_ephemeral(
                ctx,
                "Failed to set warning channel."
            )

    @chybrid_command(
        name="setlog",
        description="Sets the current channel as the logging channel",
        bot_admin=True,
        guilds=[settings.authorized_guild],
    )
    async def set_log_channel(self, ctx: Context):
        settings.logging_channel = ctx.channel.id

        if settings.logging_channel == ctx.channel.id:
            await attempt_ephemeral(
                ctx,
                f"Successfully set channel {ctx.channel.name} as logging channel."
            )
        else:
            await attempt_ephemeral(
                ctx,
                "Failed to set logging channel."
            )



async def setup(bot: Bot):
    await bot.add_cog(AdministrationCog(bot))