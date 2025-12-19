"""Utility functions for the bot."""

from __future__ import annotations

import discord
from cs2_battle_bot_api_client.api.guilds import guilds_retrieve
from cs2_battle_bot_api_client.api.servers import servers_list
from cs2_battle_bot_api_client.models import Match
from cs2_battle_bot_api_client.models.guild import Guild
from cs2_battle_bot_api_client.models.paginated_server_list import PaginatedServerList
from cs2_battle_bot_api_client.types import Response

from bot.i18n import _
from bot.settings import api_client, settings


def get_connect_account_link() -> str:
    """
    Get connect account link.

    Returns
    -------
        str: Connect account link.

    """
    return (
        "http://localhost:8002/accounts/discord/"
        if settings.DEBUG
        else f"{settings.API_URL}/accounts/discord/"
    )


def create_match_embed(match: Match) -> discord.Embed:
    """
    Create match embed.

    Args:
    ----
        match (Match): Match object.

    Returns:
    -------
        discord.Embed: Embed with match information.

    """
    embed = discord.Embed(
        title=_("embed_match_title"),
        description=_("embed_match_desc", match.id, match.type),
        color=discord.Colour.blurple(),
    )

    teams = [match.team1, match.team2]
    for team in teams:
        mentioned_leader = f"<@{team.leader.discord_user.user_id}>"
        mentioned_players = [
            f"<@{player.discord_user.user_id}>" for player in team.players
        ]
        embed.add_field(
            name=team.name,
            value=", ".join(mentioned_players),
            inline=False,
        )
        embed.add_field(
            name=_("leader"),
            value=mentioned_leader,
            inline=False,
        )
    embed.add_field(
        name=_("maps"),
        value=", ".join(match.maplist),
        inline=False,
    )
    return embed


def can_manage_matches(member: discord.Member, guild_owner_id: int) -> bool:
    """
    Check if a member can manage matches.

    A member can manage matches if they are:
    - The guild owner
    - Have a role matching MATCH_MANAGER_ROLE setting

    Args:
    ----
        member (discord.Member): The member to check.
        guild_owner_id (int): The guild owner's ID.

    Returns:
    -------
        bool: True if the member can manage matches, False otherwise.

    """
    # Guild owner can always manage matches
    if member.id == guild_owner_id:
        return True

    # Check if member has the match manager role
    role_names = [role.name.lower() for role in member.roles]
    return settings.MATCH_MANAGER_ROLE.lower() in role_names


async def get_servers_list(ctx: discord.AutocompleteContext) -> list[str]:
    """
    Get servers list.

    Args:
    ----
        ctx (discord.AutocompleteContext): Autocomplete context.

    Returns:
    -------
        list[str]: List of servers.

    """
    guild: Guild = await guilds_retrieve.asyncio(
        client=api_client, guild_id=str(ctx.interaction.guild_id)
    )
    response: Response[PaginatedServerList] = await servers_list.asyncio_detailed(
        client=api_client, guild_or_public=guild.id
    )

    paginated_servers = response.parsed
    return [f"{server.name}:{server.id}" for server in paginated_servers.results]
