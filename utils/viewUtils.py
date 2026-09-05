import asyncio
from datetime import datetime

from discord import Interaction, ButtonStyle, Member, User, Embed, Color, TextChannel
from discord.ext.commands import Bot
from discord.ui import Button, View
from loguru import logger

import config
from server.db.access import log_event
from utils import permissions
from utils.adminUtils import remove_access
from utils.enums import eventAccess
from utils.errors import InteractionMessageNone



def edit_embed_warn(
        moderator: Member | User,
        old: list[Embed]
) -> Embed:
    new_embed = Embed(
        title=f"Possible Warning: Claimed by {moderator.name}",
        description="A Possible warning / DQ has been found. Please review as soon as possible.",
        color=Color.green()
    )
    old_embed = old[0]
    new_embed.set_thumbnail(
        url=old_embed.thumbnail.url
    )
    return new_embed

async def setClaimButtonError(claim_button: Button):
    claim_button.style = ButtonStyle.danger
    claim_button.disabled = True
    claim_button.label = "Error"
    await asyncio.sleep(5)
    claim_button.disabled = False
    claim_button.label = "Claim"
    claim_button.style = ButtonStyle.success

class ClaimView(View):
    def __init__(self, jump_url: str, botClient: Bot):
        super().__init__()
        self.add_item(Button(label="Message", url=jump_url))
        self.claim_button = Button(
            label="Claim",
            style=ButtonStyle.success
        )
        self.claim_button.callback = self.claim_callback
        self.add_item(self.claim_button)
        self.botClient = botClient

    async def claim_callback(self, interaction: Interaction):
        logger.info(f"New warn claim attempt from: {interaction.user.name}")
        await interaction.response.defer(ephemeral=True, thinking=True)
        logger.info(f"Moving forward with the claim...")

        if not interaction.message:
            await interaction.followup.send(
                content="There was an error processing this request, an error log has been forwarded to all admins.",
                ephemeral=True
            )
            asyncio.create_task(setClaimButtonError(claim_button=self.claim_button))
            raise InteractionMessageNone("Failed to get interaction message for a possible warning.")

        mod = interaction.user
        logger.debug(f"Moving forward with the claim 2")
        new_embed = edit_embed_warn(mod, interaction.message.embeds)
        logger.debug(f"Moving forward with the claim 3")

        self.claim_button.style = ButtonStyle.danger
        self.claim_button.label = "Claimed"
        self.claim_button.disabled = True
        logger.debug(f"Moving forward with the claim 4")

        await interaction.followup.send(
            content="Claimed warning!",
            ephemeral=True
        )

        await interaction.message.edit(
            embed=new_embed,
            view=self
        )

class ClassView(View):
    def __init__(self, owner: Member, channel: TextChannel):
        super().__init__()
        self.owner = owner
        self.channel = channel
        self.end_button = Button(
            label="End",
            style=ButtonStyle.danger
        )
        self.cancel_button = Button(
            label="Cancel",
            style=ButtonStyle.blurple
        )
        self.cancel_button.callback = self.cancel_event_callback
        self.end_button.callback = self.end_event_callback
        self.add_item(
            self.end_button
        )
        self.add_item(
            self.cancel_button
        )

    async def end_handle_message(self,interaction: Interaction, Content: str):
        new_embed = Embed(
            title=f"Class {Content}!",
            color=Color.brand_red(),
            timestamp=datetime.now(),
            description=f"The class hosting from {self.owner.display_name} ({self.owner.id}) has ended. \n Your class event has been logged or voided."
        )
        new_embed.set_thumbnail(
            url=self.owner.avatar.url if self.owner.avatar else self.owner.default_avatar.url
        )
        self.cancel_button.disabled = True
        self.end_button.disabled = True
        await interaction.message.edit(
            embed=new_embed,
            view=self
        )
        config.class_count -= 1
        await interaction.followup.send(
            ephemeral=True,
            content=f"Class {Content}!"
        )

    async def check_perms(self, member: Member):
        return (member.id == self.owner.id) or (await permissions._find_permission_integer(member) >= 4)

    async def end_event_callback(self, interaction: Interaction):
        await interaction.response.defer(
            ephemeral=True,
            thinking=True
        )
        if not isinstance(interaction.user, Member):
            await interaction.followup.send(
                ephemeral=True,
                content="Sorry, this can only be used in an authorized guild. Contact @koulmoir for more information."
            )
            return

        # Prime example of stupidity:
        if not (await self.check_perms(interaction.user)):
            await interaction.followup.send(
                ephemeral=True,
                content="Sorry, only Senior Staff+ or the original owner can manager this."
            )
            return

        await log_event(interaction.user, eventAccess.End)
        await remove_access(self.owner, self.channel)
        await self.end_handle_message(interaction, "ended")

    async def cancel_event_callback(self, interaction: Interaction):
        await interaction.response.defer(
            ephemeral=True,
            thinking=True
        )
        if not isinstance(interaction.user, Member):
            await interaction.followup.send(
                ephemeral=True,
                content="Sorry, this can only be used in an authorized guild. Contact @koulmoir for more information."
            )
            return

        # Prime example of stupidity:
        if not (await self.check_perms(interaction.user)):
            await interaction.followup.send(
                ephemeral=True,
                content="Sorry, only Senior Staff+ or the original owner can manager this."
            )
            return

        await log_event(interaction.user, eventAccess.Cancel)
        await remove_access(self.owner, self.channel)
        await self.end_handle_message(interaction, "cancelled")