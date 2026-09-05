from discord import TextChannel, Member, User


async def give_access(user: Member, channel: TextChannel):
    await channel.set_permissions(
        target=user,
        reason="Class start",
        send_messages=True,
        embed_links=True,
        mention_everyone=True,
        attach_files=True,
        add_reactions=True
    )

async def remove_access(user: Member, channel: TextChannel):
    await channel.set_permissions(
        target=user,
        reason="Class emd",
        overwrite=None
    )
