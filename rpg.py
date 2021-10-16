import config
import discord


class RPG:
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
            'price': 1000000}}

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
            'price': 1000000}}

    items = {
        0: {
            'name': '',
            'type': '',
            'price': ''
        }
    }

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
            'name': 'Предметы',
            'dict': items,
            'buy_command': 'buy_item'
        }}

    def get_shop(category: int):

        items = RPG.rpg_shop_list[category]['dict']

        text = 'Для покупки введите :\n' \
               '/' + RPG.rpg_shop_list[category]['buy_command'] + ' (Номер предмета в каталоге)\n'

        embed = discord.Embed(title='Магазин игровых предметов:',
                              description=text,
                              color=config.embed_color)

        for id, item in items.items():
            weapon_price = ''
            if item['price'] == 0:
                continue
            elif item['price'] == -1:
                weapon_price = 'Разыгрывается на аукционе'
            else:
                weapon_price = str(item['price'])
            embed.add_field(name='```' + str(id) + '. ' + item['name'] + '```',
                            value='Цена: ' + weapon_price)

        return embed
