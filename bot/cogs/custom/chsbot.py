import discord

from bot.helpers import tools


def create_persistent_role_selector(
    guild: discord.Guild,
) -> tools.PersistentRoleSelector:
    return tools.PersistentRoleSelector(
        guild,
        [
            705065841737072740,
            713502413335822336,
            710957162167402558,
        ],
        "Role Selector",
        custom_id_prefix="roleselector",
        mutually_exclusive=False,
    )
