import discord
import config
import json
from discord.utils import get


async def get_member_by_role(client: discord.Client, role: discord.Role):
    return get(client.get_guild(config.guild).roles, id=role)


async def get_role_by_id(ctx, id: int):
    return ctx.guild.get_role(role_id=id)


def get_economic():
    file = open(config.economic_file, 'r+')
    return json.loads(file.read())


def set_economic(eco: dict):
    file = open(config.economic_file, 'w')
    file.write(json.dumps(eco, indent=4, sort_keys=True))
