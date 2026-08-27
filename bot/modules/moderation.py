from multiprocessing.context import BufferTooShort
from typing import Optional

import discord
from discord._types import ClientT
from discord.ui import Button, View
from loguru import logger
from datetime import datetime
from discord import Embed, Member, Color, TextChannel, User, ui, Interaction, Message, ButtonStyle
from discord.ext.commands import Bot

from config import settings
from utils.permissions import _find_permission_integer

class ClaimView(View):
    def __init__(self, jump_url: str):
        super().__init__()
        self.add_item(Button(label="Message", url=jump_url))
        self.claim_button = Button(
            label="Claim",
            style=ButtonStyle.success
        )
        self.claim_button.callback = self.claim_callback
        self.add_item(self.claim_button)

    async def claim_callback(self, interaction: Interaction):
        await interaction.response.defer(ephemeral=True, thinking=True)

        mod = interaction.user
        new_embed = edit_embed(mod, interaction.message.embeds)

        self.claim_button.style = ButtonStyle.danger
        self.claim_button.label = "Claimed"
        self.claim_button.disabled = True

        await interaction.message.edit(
            embed=new_embed,
            view=self
        )
        await interaction.followup.send(
            content="Claimed warning!",
            ephemeral=True
        )

def build_warn_embed(
        member: Member | User,
) -> Embed:
    color = Color.dark_red()
    title = "Possible Warning"

    embed = Embed(
        title=title,
        description="A Possible warning / DQ has been found. Please review as soon as possible.",
        color=color,
        timestamp=datetime.now()
    )
    ava = member.avatar.url if member.avatar else member.default_avatar.url
    embed.set_thumbnail(
        url=ava
    )
    return embed

def edit_embed(
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


async def handle_event_message(botClient: Bot, message: Message):
    try:
        logger.debug("Found message in event channel")
        perm = await _find_permission_integer(message.author)
        logger.debug(f"User Permission tier is: {perm}")
        if perm >= 1:
            return
        channel = message.channel
        logger.debug(f"Channel: {channel.name}")
        count = 0
        async for old_msg in channel.history():
            if old_msg.author == message.author:
                count += 1
        logger.debug(f"Found messages: {count}")
        if count < 2:
            return
        logger.debug("Getting warn logs channel")
        log_channel = botClient.get_channel(settings.warn_logs_channel)
        logger.debug(f"Found warn logs channel: {log_channel.name}")
        if not isinstance(log_channel, TextChannel):
            return
        logger.debug(f"Found text warn logs channel: {log_channel.name}")
        embed = build_warn_embed(
            member=message.author
        )
        view = ClaimView(jump_url=message.jump_url)

        await log_channel.send(
            embed=embed,
            view=view
        )
    except Exception as e:
        logger.warning(f"Failed to process event message due to: {e}")


def build_log_embed(
        moderator: Member | User,
        member: Member,
        reason: str,
        action: str
) -> Embed:
    logger.debug("Creating embed...")
    embed = Embed(
        title="Moderation log",
        color=Color.dark_red(),
        description="Moderation action was taken against a user. Attach any Evidence in the thread bellow. Leaving it empty may result in a strike.",
        timestamp=datetime.now()
    )
    logger.debug("Setting embed thumbnail...")
    embed.set_thumbnail(
        url=member.avatar.url
    )
    logger.debug("Adding embed fields...")
    embed.add_field(
        name="Reason:",
        value=reason,
        inline=True
    )
    embed.add_field(
        name="Action taken:",
        value=action,
        inline=True
    )
    logger.debug("Setting embed author...")
    embed.set_author(
        name=moderator.name,
        icon_url=moderator.avatar.url
    )
    return embed

def build_loa_embed(
    member: Member | User,
    reason: str,
    duration: str
) -> Embed:
    embed = Embed(
        title="LOA notice",
        description="New LOA notice from an event staff or moderator.",
        timestamp=datetime.now(),
        color=Color.dark_magenta()
    )
    embed.set_author(
        name=member.name
    )
    embed.add_field(
        name="Reason:",
        value=reason
    )
    embed.add_field(
        name="Duration:",
        value=duration
    )
    embed.set_thumbnail(
        url=member.avatar.url
    )
    return embed

async def attempt_log(
        moderator: Member | User,
        member: Member,
        reason: str,
        action: str,
        botClient: Bot
) -> Message | None:
    logging_channel_id = settings.logging_channel
    log_channel = botClient.get_channel(logging_channel_id)
    logger.debug(f"Logging in channel: {log_channel.name}")
    log_embed = build_log_embed(
        moderator, member, reason, action
    )
    logger.debug("Created embed, sending message")
    if not isinstance(log_channel, TextChannel):
        logger.debug("Logging Channel not a text channel!")
        return None
    log_msg = await log_channel.send(
        embed=log_embed
    )
    logger.debug("Sent message, creating thread...")
    await log_msg.create_thread(
        name=member.name
    )

    return log_msg

async def attempt_loa_send(
    member: Member | User,
    reason: str,
    duration: str,
    botClient: Bot
):
    embed = build_loa_embed(
        member, reason, duration
    )
    logger.debug(f"Made Loa Embed for user: {member.name}")
    for member_id in settings.bot_administrators:
        admin = botClient.get_user(member_id)
        if not admin:
            return
        await admin.send(
            embed=embed
        )

class LoaModal(ui.Modal, title="Submit new LOA Notice"):
    def __init__(self, *, botClient: Bot):
        super().__init__()
        self.botClient = botClient

    Reason = ui.TextInput(
        label="Reason (This is not shared)",
        required=True,
        style=discord.TextStyle.long,
        placeholder="Your reason here..."
    )
    Duration = ui.TextInput(
        label="Duration (This is not shared)",
        required=True,
        style=discord.TextStyle.short,
        placeholder="I'll be away for one week."
    )

    async def on_submit(self, interaction: Interaction, /) -> None:
        await interaction.followup.send(
            content="Thanks for being honest, your notice has been handed in :3",
            ephemeral=True
        )
        await attempt_loa_send(
            member=interaction.user,
            reason=self.Reason.value,
            duration=self.Duration.value,
            botClient=self.botClient
        )

    async def on_error(self, interaction: Interaction[ClientT], error: Exception, /) -> None:
        await interaction.followup.send(
            content="Sorry, unable to process request.",
            ephemeral=True
        )