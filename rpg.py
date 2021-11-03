import time

import config
import discord
from discord_slash import manage_components, SlashContext, ButtonStyle
from roman import toRoman
from economic import get_economic, give_money, set_economic
import random

active_dungeons = {}

class RPG:
    male_names = 'Григорий, Лев, Андрей, Роман, Арсений, Степан, Владислав, Никита, Глеб, Марк, Давид, Ярослав, Евгений, Матвей, Фёдор, Николай, Алексей, Андрей, Артемий, Виктор, Никита, Даниил, Денис, Егор, Игорь, Лев, Леонид, Павел, Петр, Роман, Руслан, Сергей, Семён, Тимофей, Степан, Владимир, Тимофей, Ярослав, Павел, Егор, Сергей, Владислав, Федор, Константин, Максим, Артём, Никита, Юрий, Платон, Денис, Ярослав, Мирон, Василий, Лев, Степан, Евгений, Савелий, Давид, Григорий, Тимур, Кирилл, Виктор, Фёдор, Богдан, Константин, Адам, Леонид, Роман, Павел, Артемий, Петр, Алексей, Мирон, Владимир, Николай, Руслан, Алексей, Юрий, Ярослав, Семен, Евгений, Олег, Артур, Петр, Степан, Илья, Вячеслав, Сергей, Василий, Степа, Федор, Стас, Вячеслав, Георгий, Антон, Борис, Захар, Арсений, Виктор, Родион, Святослав, Игорь, Гордей, Юрий, Мирослав, Лука, Егор, Игорь, Глеб, Коля, Давид, Леон, Женя, Вася, Мирон, Савелий, Олег, Даниэль, Савва, Денис, Святослав, Рома, Кирилл, Николай, Артём, Костя, Владимир, Степа, Вячеслав, Денис, Паша, Виктор, Михаил, Андрей, Вадим, Анатолий, Илья, Степа, Федор, Георг, Семен, Олег, Лев, Демьян, Антон, Владислав, Артем, Елисей, Радик, Боря, Стас, Марк, Влад, Ян, Паша, Витя, Леонид, Вася, Игнат, Юра, Петр, Анатолий, Валера, Эрик, Марат, Мирон, Витя, Анатолий, Роман, Ника, Платон, Сережа, Тимур, Женя, Семен, Анатолий, Олег, Адам, Игорь, Филя, Артур, Марсель, Валера, Ян, Назар, Леон'.split(', ')
    female_names = 'Александра, Алёна, Алина, Алиса, Алла, Анастасия, Анна, Арина, Валентина, Валерия, Варвара, Вера, Вероника, Виктория, Виталия, Владислава, Галина, Дарья, Диана, Ева, Ева, Евгения, Екатерина, Алёна, Елена, Елизавета, Жанна, Инна, Ирина, Карина, Кристина, Ксения, Лариса, Лера, Лилия, Любовь, Людмила, Маргарита, Марина, Мария, Мила, Милана, Надежда, Наталья, Ника, Нина, Оксана, Олеся, Ольга, Полина, Роза, Руслана, Светлана, Соня, София, Софья, Татьяна, Юлия, Яна, Ярослава'.split(', ')

    dungeons = {
        1: {'name': 'Мусорка',
            'mobs': [
                {
                    'name': 'Бомж {m}',
                    'damage': 1,
                    'health': 5
                },
                {
                    'name': 'Бомж {m}',
                    'damage': 2,
                    'health': 7
                },
                {
                    'name': 'Бомж {m}',
                    'damage': 2,
                    'health': 10
                },
                {
                    'name': 'Бомж {m}',
                    'damage': 5,
                    'health': 20
                }
            ]
            },
        2: {'name': 'Пятёрочка',
            'mobs': [
                {
                    'name': 'Продавщица {f}',
                    'damage': 5,
                    'health': 19
                },
                {
                    'name': 'Продавец {m}',
                    'damage': 6,
                    'health': 23
                },
                {
                    'name': 'Продавщица {f}',
                    'damage': 5,
                    'health': 21
                },
                {
                    'name': 'Администратор {f}',
                    'damage': 10,
                    'health': 50
                }
            ]
            },
        3: {'name': 'Митинг',
            'mobs': [
                {
                    'name': 'Гражданка {f}',
                    'damage': 15,
                    'health': 89
                },
                {
                    'name': 'Гражданин {m}',
                    'damage': 18,
                    'health': 92
                },
                {
                    'name': 'Гражданин {m}',
                    'damage': 17,
                    'health': 98
                },
                {
                    'name': 'ФСБ-шник {m}',
                    'damage': 30,
                    'health': 150
                }
            ]
            },
        4: {'name': 'Mvideo на чёрной пятнице',
            'mobs': [
                {
                    'name': 'Покупатель {m}',
                    'damage': 43,
                    'health': 376
                },
                {
                    'name': 'Покупатель {m}',
                    'damage': 52,
                    'health': 493
                },
                {
                    'name': 'Покупатель {f}',
                    'damage': 59,
                    'health': 542
                },
                {
                    'name': 'Покупатель {m}',
                    'damage': 100,
                    'health': 1000
                }
            ]
            },
        5: {'name': 'Ад',
            'mobs': [
                {
                    'name': 'Демон',
                    'damage': 102,
                    'health': 2242
                },
                {
                    'name': 'Демон',
                    'damage': 110,
                    'health': 2358
                },
                {
                    'name': 'Дъявол',
                    'damage': 300,
                    'health': 5000
                },
                {
                    'name': 'Сатана',
                    'damage': 1000,
                    'health': 10000
                }
            ]
            },
        6: {'name': 'Рай',
            'mobs': [
                {
                    'name': 'Монарх',
                    'damage': 220,
                    'health': 3500
                },
                {
                    'name': 'Ангел',
                    'damage': 440,
                    'health': 4000
                },
                {
                    'name': 'Преспешник Бога',
                    'damage': 800,
                    'health': 8000
                },
                {
                    'name': 'Бог',
                    'damage': 1600,
                    'health': 18000
                }
            ]
            },
        7: {'name': 'Чистилище',
            'mobs': [
                {
                    'name': 'Заквиель',
                    'damage': 440,
                    'health': 9000
                },
                {
                    'name': 'Ники',
                    'damage': 130,
                    'health': 23000
                },
                {
                    'name': 'НеО',
                    'damage': 1600,
                    'health': 15000
                },
                {
                    'name': 'Альцест',
                    'damage': 3000,
                    'health': 36000
                }
            ]
            },
        8: {'name': 'Г.Абобусово',
            'mobs': [
                {
                    'name': 'Абобус',
                    'damage': 600,
                    'health': 12000
                },
                {
                    'name': 'Абобус',
                    'damage': 600,
                    'health': 12000
                },
                {
                    'name': 'Абубуска',
                    'damage': 300,
                    'health': 30000
                },
                {
                    'name': 'Карейка Даша',
                    'damage': 6000,
                    'health': 60000
                }
            ]
            },
        9: {'name': 'Gym',
            'mobs': [
                {
                    'name': 'Fucking slave',
                    'damage': 900,
                    'health': 15000
                },
                {
                    'name': 'Jebrony',
                    'damage': 1500,
                    'health': 30000
                },
                {
                    'name': 'Full master',
                    'damage': 6000,
                    'health': 60000
                },
                {
                    'name': 'Dungeon Master',
                    'damage': 12000,
                    'health': 120000
                }
            ]
            },
        10: {'name': 'Москва Сити',
             'mobs': [
                 {
                     'name': 'Лололошка',
                     'damage': 1500,
                     'health': 30000
                 },
                 {
                     'name': 'Суба',
                     'damage': 2000,
                     'health': 40000
                 },
                 {
                     'name': 'Гардей',
                     'damage': 8000,
                     'health': 70000
                 },
                 {
                     'name': 'Летвин',
                     'damage': 20000,
                     'health': 360000
                 }
             ]
             },
        11: {'name': 'Школьный туалет',
             'mobs': [
                 {
                     'name': 'Малолетка с петардой',
                     'damage': 3000,
                     'health': 60000
                 },
                 {
                     'name': 'Малолетка играющая в бравл',
                     'damage': 4000,
                     'health': 46000
                 },
                 {
                     'name': 'Убрщица',
                     'damage': 16000,
                     'health': 140000
                 },
                 {
                     'name': 'Стареклассник с hqd',
                     'damage': 40000,
                     'health': 720000
                 }
             ]
        }
    }

    weapons = {
        0: {'name': 'Кулаки',
            'damage': 3,
            'price': 0},
        1: {'name': 'Деревянный меч',
            'damage': 10,
            'price': 1000},
        2: {'name': 'Каменный меч',
            'damage': 15,
            'price': 2500},
        3: {'name': 'Железный меч',
            'damage': 25,
            'price': 10000},
        4: {'name': 'Золотой меч',
            'damage': 30,
            'price': 25000},
        5: {'name': 'Алмазный меч',
            'damage': 50,
            'price': 100000},
        6: {'name': 'Адамантитовый меч',
            'damage': 75,
            'price': 200000},
        7: {'name': 'Меч Бога',
            'damage': 150,
            'price': 1000000},
        8: {'name': 'Меч Абобуса',
            'damage': 500,
            'price': 1200000},
        9: {'name': 'Bandage',
            'damage': 2000,
            'price': 1900000},
        10: {'name': 'Заточка Субы',
             'damage': 5000,
             'price': 2200000},
        11: {'name': 'Швабра Уборщицы',
            'damage': 10000,
            'price': 3000000}
    }

    armors = {
    0: {'name': 'Рубашка',
        'defence': 1,
        'price': 0},
    1: {'name': 'Деревянная броня',
        'defence': 10,
        'price': 1000},
    2: {'name': 'Кожанная броня',
        'defence': 15,
        'price': 2500},
    3: {'name': 'Железная броня',
        'defence': 25,
        'price': 10000},
    4: {'name': 'Золотая броня',
        'defence': 30,
        'price': 25000},
    5: {'name': 'Алмазная броня',
        'defence': 50,
        'price': 100000},
    6: {'name': 'Адаманититовая броня',
        'defence': 75,
        'price': 200000},
    7: {'name': 'Броня Бога',
        'defence': 150,
        'price': 1000000},
    8: {'name': 'Броня Абобуса',
        'defence': 500,
        'price': 1200000},
    9: {'name': 'Майка Jebrony',
        'defence': 1500,
        'price': 1900000},
    10: {'name': 'Рубашка Gucci',
         'defence': 5000,
         'price': 2200000},
    11: {'name': 'Накидка Уборщицы',
         'defence': 10000,
         'price': 3000000}
    }

    potions = {
        1: {
            'name': 'Зелье исцеления {}',
            'effect': 'health',
            'price_multiplier': 1
        },
        2: {
            'name': 'Зелье защиты {}',
            'effect': 'defence',
            'price_multiplier': 1
        },
        3: {
            'name': 'Зелье силы {}',
            'effect': 'damage',
            'price_multiplier': 1
        }
    }

    artifacts = {}

    rpg_shop_list = {
        1: {
            'name': 'Оружие',
            'dict': weapons,
            'buy_command': 'buy_weapon'
        },
        2: {
            'name': 'Броня',
            'dict': armors,
            'buy_command': 'buy_armor'
        },
        3: {
            'name': 'Зелья',
            'dict': potions,
            'buy_command': 'buy_potion'
        },
        4: {
            'name': 'Артефакты',
            'dict': artifacts,
            'buy_command': 'buy_artifact'
        }
    }

    def get_shop(category_shop: int):

        items_shop = RPG.rpg_shop_list[category_shop]['dict']

        text = 'Для покупки введите :\n' \
               '/' + RPG.rpg_shop_list[category_shop]['buy_command'] + ' (Номер предмета в каталоге)\n'

        embed = discord.Embed(title='Магазин игровых предметов:',
                              description=text,
                              color=config.embed_color)

        if category_shop == 1:
            for id, weapon in items_shop.items():
                price = ''
                if weapon['price'] == 0:
                    continue
                else:
                    price = str(weapon['price'])
                damage = str(weapon['damage'])
                embed.add_field(name=f'```{str(id)}. {weapon["name"]}```',
                                value=f'Цена: {price} \nУрон: {damage}')
        if category_shop == 2:
            for id, armor in items_shop.items():
                price = ''
                if armor['price'] == 0:
                    continue
                else:
                    price = str(armor['price'])
                embed.add_field(name=f'```{str(id)}. {armor["name"]}```',
                                value=f'Цена: {price} \nЗащита: {armor["defence"]}')
        if category_shop == 3:
            for id, potion in items_shop.items():
                text = ''
                for i in range(9):
                    effect = ((i + 1) ** 2) * 5
                    text = text + f'**{str(id*10+i+1)}. {potion["name"].format(toRoman(i+1))}**\n' \
                                  f'Эффект: {effect}\n' \
                                  f'Цена: {effect*100*potion["price_multiplier"]}\n'
                embed.add_field(name=f'```{potion["name"].format("")}```',
                                value=text)
        if category_shop == 4:
            for id, item in items_shop.items():
                price = ''
                if item['price'] == 0:
                    continue
                else:
                    price = str(item['price'])
                embed.add_field(name='```' + str(id) + '. ' + item['name'] + '```',
                                value='Цена: ' + price)

        return embed


class Dungeon:

    def __init__(self, ctx: SlashContext, dungeon_id: int):

        embed = discord.Embed(title='Вы готовитесь идти в данж!',
                              description='Когда будете готовы, нажмите кнопку',
                              color=config.embed_color)

        self.member = ctx.author
        self.embed = embed
        self.ctx = ctx
        eco = get_economic()
        self.health = eco['members'][str(ctx.author.id)]['health']
        self.damage = RPG.weapons[eco['members'][str(ctx.author.id)]['inventory']['weapon']]['damage']
        self.defence = RPG.armors[eco['members'][str(ctx.author.id)]['inventory']['armor']]['defence']
        self.dungeon_id = dungeon_id
        self.mob_num = 0

    async def create_dungeon(self):

        text = ''

        for mob in RPG.dungeons[self.dungeon_id]['mobs'].copy():
            name = mob['name']
            name = name.replace("{m}", "").replace("{f}", "")
            text = text + f'_ _ {name} ({mob["health"]} hp, {mob["damage"]} атаки) \n'
        self.embed.add_field(name=f'``` {RPG.dungeons[self.dungeon_id]["name"]} ```',
                             value=text, inline=False)

        inventory_dict = get_economic()['members'][str(self.ctx.author.id)]['inventory']
        weapon = RPG.weapons[inventory_dict['weapon']]
        armor = RPG.armors[inventory_dict['armor']]

        self.embed.add_field(name='```Ваше снаряжение:```',
                             value='Если вы забыли подготовить снаряжение, то можете отменить поход в данж')
        self.embed.add_field(name=f'Оружие:',
                             value=weapon['name'] + ' (' + str(weapon['damage']) + ' урона)', inline=False)
        self.embed.add_field(name=f'Броня:',
                             value=armor['name'] + ' (' + str(armor['defence']) + ' защиты)', inline=False)
        text = ''
        for potion_id, potion in inventory_dict['potions'].items():
            if potion['count'] > 0:
                text = text + f'{potion["name"]} ({potion["count"]})'
            else:
                text = 'У вас нет зелий'
        self.embed.add_field(name=f'Зелья:',
                             value=text, inline=False)

        text = ''
        if len(inventory_dict['artifacts']) > 0:
            for item in inventory_dict['artifacts']:
                text = text + item['name'] + '\n'
        else:
            text = 'У вас нет артефактов'
        self.embed.add_field(name=f'Артефакты:',
                             value=text, inline=False)

        overwrites = {
            self.ctx.guild.default_role: discord.PermissionOverwrite(view_channel=False),
            self.ctx.author: discord.PermissionOverwrite(read_messages=True)
        }
        self.channel = await self.ctx.guild.create_text_channel(f'{RPG.dungeons[self.dungeon_id]["name"]} (для {self.ctx.author.display_name})',
                                                                overwrites=overwrites)

        original_msg = await self.ctx.reply(f'Перейдите в канал {self.channel.mention} для продолжения')

        self.original_channel = original_msg.channel

        actions = [manage_components.create_button(label='Старт!', style=ButtonStyle.green),
                   manage_components.create_button(label='Отмена', style=ButtonStyle.secondary)]
        action_rows = manage_components.create_actionrow(*actions)
        self.start_message = await self.channel.send(embed=self.embed, components=[action_rows])

        active_dungeons[self.channel] = self

    async def start_dungeon(self):
        await self.start_message.delete()
        self.enemy = RPG.dungeons[self.dungeon_id]['mobs'][self.mob_num].copy()
        self.enemy['name'] = self.enemy['name'].format(m=random.choice(RPG.male_names),
                                                       f=random.choice(RPG.female_names))

        eco = get_economic()
        self.potions = eco['members'][str(self.member.id)]['inventory']['potions']

        await self.battle_enemy(RPG.dungeons[self.dungeon_id]['mobs'][self.mob_num].copy())

    async def battle_enemy(self, enemy: dict):
        try:
            await self.message.delete()
        except:
            pass
        self.embed = discord.Embed(title='Вы наткнулись на врага!',
                                   description='',
                                   color=config.embed_color)
        self.embed.add_field(name=f'```Ваш враг - {enemy["name"]}```',
                             value=f'Здоровье - {enemy["health"]}\n'
                                   f'Урон - {enemy["damage"]}',
                             inline=False)
        self.embed.add_field(name='**VS**',
                             value='_ _',
                             inline=False)
        self.embed.add_field(name='```Вы```',
                             value=f'Здоровье - {self.health}\n'
                                   f'Урон - {self.damage}\n'
                                   f'Защита - {self.defence}',
                             inline=False)
        actions = []
        for id, potion in self.potions.items():
            if potion['count'] > 0:
                actions.append(manage_components.create_button(label=f'{potion["name"]} ({potion["count"]})', style=ButtonStyle.green))
        actions.append(manage_components.create_button(label='Следующий ход', style=ButtonStyle.green))
        actions.append(manage_components.create_button(label='Покинуть данж', style=ButtonStyle.danger))
        action_rows = manage_components.create_actionrow(*actions)

        self.message = await self.channel.send(embed=self.embed, components=[action_rows])

    async def apply_potion(self, potion_id: int):
        for id, potion in self.potions.items():
            if id == potion_id:
                print(RPG.potions[int(potion_id)])
                print(RPG.potions[int(potion_id)]['effect'])
                potion['count'] = potion['count'] - 1
                if RPG.potions[int(potion_id)]['effect'] == 'health':
                    self.health = self.health + ((potion['strength'] + 1) ** 2) * 5
                if RPG.potions[int(potion_id)]['effect'] == 'damage':
                    self.damage = self.health + ((potion['strength'] + 1) ** 2) * 5
                if RPG.potions[int(potion_id)]['effect'] == 'defence':
                    self.defence = self.health + ((potion['strength'] + 1) ** 2) * 5
                await self.battle_enemy(self.enemy)


    async def step(self):
        self.enemy['health'] = self.process_hit(self.enemy['health'], self.damage, 0)

        if self.enemy['health'] <= 0:
            self.mob_num = self.mob_num + 1
            if self.mob_num >= len(RPG.dungeons[self.dungeon_id]['mobs']):
                await self.complete_dungeon()
                return None
            self.enemy = RPG.dungeons[self.dungeon_id]['mobs'][self.mob_num].copy()
            self.enemy['name'] = self.enemy['name'].format(m=random.choice(RPG.male_names),
                                                           f=random.choice(RPG.female_names))
            await self.battle_enemy(self.enemy)
            return None

        self.health = self.process_hit(self.health, self.enemy['damage'], self.defence)

        if self.health <= 0:
            await self.defeat_dungeon()

        await self.battle_enemy(self.enemy)


    def process_hit(self, health: int, damage: int, armor: int):
        new_health = health - (damage + (damage * (random.random() - 0.5) // 2)) + (armor // 2)
        if new_health > health:
            return health
        else:
            return int(new_health)

    async def cancel_dungeon(self):
        await self.channel.delete()
        active_dungeons.pop(self.channel)
        del self

    async def defeat_dungeon(self):
        await self.channel.delete()
        active_dungeons.pop(self.channel)
        embed = discord.Embed(title=self.member.display_name + ' сдох.', color=config.embed_color)
        embed.set_image(url=config.rip_image)
        await self.original_channel.send(embed=embed)
        eco = get_economic()
        eco['members'][str(self.member.id)]['dungeon_timeout'] = time.time() + 3600
        set_economic(eco)
        del self

    async def exit_dungeon(self):
        await self.channel.delete()
        active_dungeons.pop(self.channel)
        await self.original_channel.send(f'{self.member.mention}, вы покинули данж')
        eco = get_economic()
        eco['members'][str(self.member.id)]['dungeon_timeout'] = time.time() + 3600
        set_economic(eco)
        del self

    async def complete_dungeon(self):
        await self.channel.delete()
        active_dungeons.pop(self.channel)
        eco = get_economic()
        eco['members'][str(self.member.id)]['dungeon_timeout'] = time.time() + 36000
        set_economic(eco)
        money = 0
        for mob in RPG.dungeons[self.dungeon_id]['mobs']:
            money = money + (mob['health'] + mob['damage'])
        money = money // 2
        give_money(self.member, money)
        await self.original_channel.send(f'{self.member.mention}, Вы прошли данж {RPG.dungeons[self.dungeon_id]["name"]}!\n'
                                         f'Вам начислено {money} $')
        del self
