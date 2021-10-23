import discord
import config
from utils import get_economic, set_economic
from discord_slash import SlashContext


def get_money(member: discord.Member):
    eco = get_economic()
    return eco['members'][str(member.id)]['money']


def set_money(member: discord.Member, money: float):
    eco = get_economic()
    eco['members'][str(member.id)]['money'] = money
    set_economic(eco)


def take_money(member: discord.Member, money: float):
    eco = get_economic()
    set_money(member, eco['members'][str(member.id)]['money'] - money)


def give_money(member: discord.Member, money: float):
    eco = get_economic()
    set_money(member, eco['members'][str(member.id)]['money'] + money)


class Economic:

    def __init__(self):

        self.filename = config.economic_file

    roles_shop = {
        1:
            {"id": config.vip_role,
             "price": 1000},
        2:
            {"id": config.deluxe_role,
             "price": 2500},
        3:
            {"id": config.emperor_role,
             "price": 5000},
        4:
            {"id": config.helper_role,
             "price": 10000}
    }

    works = {
        0: {
            'name': 'Безработный',
            'salary': 0,
            'timeout': 0,
            'price': 0
        },
        1: {
            'name': 'Дворник',
            'salary': 50,
            'timeout': 120,
            'price': 0
        },
        2: {
            'name': 'Продавец-кассир',
            'salary': 100,
            'timeout': 180,
            'price': 1000
        },
        3: {
            'name': 'Консультант DNS',
            'salary': 200,
            'timeout': 240,
            'price': 5000
        },
        4: {
            'name': 'Менеджер',
            'salary': 400,
            'timeout': 360,
            'price': 20000
        },
        5: {
            'name': 'Хирург',
            'salary': 600,
            'timeout': 720,
            'price': 20000
        },
        6: {
            'name': 'Программист',
            'salary': 1000,
            'timeout': 360,
            'price': 100000
        },
        7: {
            'name': 'Хакер',
            'salary': 5000,
            'timeout': 720,
            'price': 500000
        },
        8: {
            'name': 'Гендиректор Google',
            'salary': 10000,
            'timeout': 60,
            'price': 2500000
        },
    }

    def reset_economic(self, ctx: SlashContext):

        eco = {'settings': {'last_update_day': 0,
                            'last_update_random_coins': 0},
               'members': {}}

        set_economic(eco)

        for member in ctx.guild.members:
            if not member.bot:
                self.add_member(member)

    def add_member(self, member: discord.Member):
        eco = get_economic()
        eco['members'][str(member.id)] = {'money': 0.0,
                                          'inventory': {'weapon': 0,
                                                        'armor': 0,
                                                        'items': []},
                                          'daily': True,
                                          'work': 0,
                                          'work_timeout': 0}
        set_economic(eco)
