import discord
import config
from utils import get_economic, set_economic, write_log
from discord_slash import SlashContext


def get_money(member: discord.Member):
    eco = get_economic()
    return eco['members'][str(member.id)]['money']


def set_money(member: discord.Member, money: float):
    eco = get_economic()
    eco['members'][str(member.id)]['money'] = money
    set_economic(eco)
    write_log(member.display_name + ' установлено ' + str(money) + ' $')


def take_money(member: discord.Member, money: float):
    eco = get_economic()
    set_money(member, eco['members'][str(member.id)]['money'] - money)
    write_log(member.display_name + ' забрано ' + str(money) + ' $')


def give_money(member: discord.Member, money: float):
    eco = get_economic()
    set_money(member, eco['members'][str(member.id)]['money'] + money)
    write_log(member.display_name + ' выдано ' + str(money) + ' $')


class Economic:

    def __init__(self):

        self.filename = config.economic_file

    roles_shop = {
        1:
            {"id": config.vip_role,
             "price": 10000,
             "coin_multiplier": 1.25},
        2:
            {"id": config.deluxe_role,
             "price": 25000,
             "coin_multiplier": 1.5},
        3:
            {"id": config.emperor_role,
             "price": 50000,
             "coin_multiplier": 1.75},
        4:
            {"id": config.helper_role,
             "price": 100000,
             "coin_multiplier": 2}
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
            'timeout': 60,
            'price': 0
        },
        2: {
            'name': 'Продавец-кассир',
            'salary': 100,
            'timeout': 120,
            'price': 500
        },
        3: {
            'name': 'Консультант DNS',
            'salary': 200,
            'timeout': 120,
            'price': 2000
        },
        4: {
            'name': 'Менеджер',
            'salary': 400,
            'timeout': 120,
            'price': 30000
        },
        5: {
            'name': 'Хирург',
            'salary': 600,
            'timeout': 180,
            'price': 55000
        },
        6: {
            'name': 'Программист',
            'salary': 1000,
            'timeout': 120,
            'price': 77000
        },
        7: {
            'name': 'Хакер',
            'salary': 5000,
            'timeout': 180,
            'price': 250000
        },
        8: {
            'name': 'Гендиректор Google',
            'salary': 10000,
            'timeout': 180,
            'price': 700000
        },
    }

    def reset_economic(self, ctx: SlashContext):

        try:
            eco = get_economic()
        except:
            eco = {}

        eco['members'] = {}

        try:
            _ = eco['settings']
        except:
            eco['settings'] = {'last_update_day': 0,
                               'last_update_random_coins': 0}
        set_economic(eco)

        for member in ctx.guild.members:
            if not member.bot:
                self.add_member(member)

    def add_member(self, member: discord.Member):
        eco = get_economic()
        eco['members'][str(member.id)] = {'money': 0.0,
                                          'inventory': {'weapon': 0,
                                                        'armor': 0,
                                                        'potions': {},
                                                        'artifacts': []},
                                          'daily': True,
                                          'work': 0,
                                          'work_timeout': 0,
                                          'health': 20,
                                          'dungeon_timeout': 0}
        from rpg import RPG
        for id, potion in RPG.potions.items():
            eco['members'][str(member.id)]['inventory']['potions'][str(id)] = {'strength': 0,
                                                                               'name': '',
                                                                               'count': 0}

        set_economic(eco)
