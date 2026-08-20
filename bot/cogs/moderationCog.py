from discord.ext import commands
from discord.ext.commands import Bot
from utils.commandUtils import chybrid_command


class moderationCog(commands.Cog):

    def __init__(self, botClient: Bot):
        self.bot = botClient




async def setup(bot: Bot):
    await bot.add_cog(moderationCog(bot))