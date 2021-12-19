import os
import requests
import discord
import asyncio
import time
import json
import datetime
import config
import random
import sys
from rpg import RPG, Dungeon, active_dungeons
import economic
from lottery import Lottery, lotteries
import xml.etree.ElementTree as ET
from utils import get_member_by_role, get_role_by_id, get_economic, set_economic, write_log
from admin_commands import mute, unmute
from discord.ext import commands
from discord_slash import SlashCommand, SlashContext, ComponentContext, manage_components, ButtonStyle
from voting import votings, Voting
from roman import toRoman
from music import Music, active_voices

sys.setrecursionlimit(1000000)

print('starting')
write_log('starting')

intents = discord.Intents.default()
intents.members = True
client = commands.Bot(command_prefix=config.prefix, intents=intents)
slash = SlashCommand(client, sync_commands=True)

random_coins = {}
rpg_shops = {}

economics = economic.Economic()


@client.event
async def on_ready():
    print('online')
    write_log('online')

    await client.change_presence(activity=discord.Activity(type=config.default_activity_type,
                                                           name=config.default_activity_text))
    await client.change_presence(status=config.default_status)

    test_channel = discord.utils.get(client.get_guild(config.guild).channels, id=config.test_channel)
    await test_channel.send('Включаюсь')

    await time_checker()


@client.event
async def on_member_join(member):
    economics.add_member(member)


@client.event
async def on_message(msg: discord.Message):
    if len(msg.embeds) > 0:
        write_log(str(msg.id) + '/' + msg.author.display_name + ': ' + msg.embeds[0].title)
    else:
        write_log(str(msg.id) + '/' + msg.author.display_name + ': ' + msg.content)
    if len(msg.attachments) > 0:
        for attachment in msg.attachments:
            write_log(str(msg.id) + '/' + msg.author.display_name + ': ' + attachment.url)


@client.event
async def on_message_delete(msg: discord.Message):
    write_log(str(msg.id) + '/' + msg.author.display_name + ': ' + msg.content + ' - было удалено')


@client.event
async def on_message_edit(old_msg: discord.Message, new_msg: discord.Message):
    write_log(str(old_msg.id) + '/' + old_msg.author.display_name + ': ' + old_msg.content + ' > ' + new_msg.content)


@client.event
async def on_component(ctx: ComponentContext):  # buttons handler
    # voting handler

    if ctx.origin_message_id in rpg_shops.keys():

        id = 0
        for item_id, item in RPG.rpg_shop_list.items():
            if item['name'] == ctx.component['label']:
                id = item_id

        embed = RPG.get_shop(id)

        await ctx.edit_origin(embed=embed)

        rpg_shops[ctx.origin_message.id] = id

    if ctx.origin_message_id in random_coins.keys():
        await ctx.origin_message.channel.send(ctx.author.display_name + ' подобрал ' + str(random_coins[ctx.origin_message_id]) + ' $!')
        await ctx.origin_message.delete()
        economic.give_money(ctx.author, random_coins[ctx.origin_message_id])

    for voting in votings.values():
        labels = []
        for component in voting.components:
            labels.append(component['label'])
        if ctx.component.get('label') in labels:
            await voting.vote(ctx)

    for lottery in lotteries.values():
        labels = []
        for component in lottery.components:
            labels.append(component['label'])
        if ctx.component.get('label') in labels:
            await lottery.take_part(ctx)

    if ctx.origin_message.channel in active_dungeons.keys():
        if ctx.component['label'] == 'Старт!':
            await active_dungeons[ctx.origin_message.channel].start_dungeon()
        if ctx.component['label'] == 'Отмена':
            await active_dungeons[ctx.origin_message.channel].cancel_dungeon()
        if ctx.component['label'] == 'Покинуть данж':
            await active_dungeons[ctx.origin_message.channel].exit_dungeon()
        if ctx.component['label'] == 'Следующий ход':
            await active_dungeons[ctx.origin_message.channel].step()
        for id, potion in active_dungeons[ctx.origin_message.channel].potions.items():
            if potion["count"] > 0:
                if ctx.component['label'] == f'{potion["name"]} ({potion["count"]})':
                    await active_dungeons[ctx.origin_message.channel].apply_potion(id)


async def send_for_three_seconds(ctx: SlashContext, text: str):
    msg = await ctx.reply(text)
    # await asyncio.sleep(3)
    # await msg.delete()


async def time_checker():

    while True:

        file = open(config.economic_file, 'r')
        now_time = int(time.mktime(time.gmtime()))

        eco = json.loads(file.read())

        file.close()
        if now_time - eco['settings']['last_update_day'] > 86400:
            eco['settings']['last_update_day'] = now_time

            for member in eco['members']:
                eco['members'][member]['daily'] = True

            set_economic(eco)

        if now_time - eco['settings']['last_update_random_coins'] > 21600:

            actions = [manage_components.create_button(label='Подобрать!', style=ButtonStyle.green)]
            action_rows = manage_components.create_actionrow(*actions)

            coins = random.randint(100, 160)

            channel = client.get_guild(config.guild).get_channel(config.main_channel)

            msg = await channel.send('Деньги сыпятся с неба!\nУспей подобрать ' + str(coins) + ' $!',
                                     components=[action_rows])

            random_coins[msg.id] = coins

            eco['settings']['last_update_random_coins'] = now_time

            set_economic(eco)

        # news

        if round(now_time) == 1640977199:
            channel = client.get_channel(config.news_channel)
            await channel.send('@here, с Новым годом!')

        # online
        
        
        await asyncio.sleep(1)


#


@slash.slash(name='ping',
             description='Отображает пинг бота',
             guild_ids=[config.guild])
async def ping(ctx: SlashContext):
    await ctx.send('Pong! {0}'.format(round(client.latency, 1)) + ' ms')


@slash.slash(name='say',
             description='Пишет сообщение от лица бота',
             guild_ids=[config.guild])
async def say(ctx: SlashContext, text: str):
    if ctx.author != ctx.guild.owner:
        await send_for_three_seconds(ctx, config.upper_role_error)
        return None
    await ctx.channel.send(text)


@slash.slash(name='say_dm',
             description='Пишет сообщение от лица бота в лс',
             guild_ids=[config.guild])
async def say_dm(ctx: SlashContext, member: discord.Member, text: str):
    if member.bot:
        await send_for_three_seconds(ctx, config.bot_error)
        return None
    if ctx.author != ctx.guild.owner:
        await send_for_three_seconds(ctx, config.upper_role_error)
        return None
    await member.send(text)
    msg = await ctx.reply('Отправил')
    await msg.delete()


#


@slash.slash(name='mute',
             description='Заглушает участника',
             guild_ids=[config.guild])
async def mute_command(ctx: SlashContext, member: discord.Member, time: str = None):
    min_role = await get_role_by_id(ctx, config.mute_perm_role)

    if member.bot:
        await send_for_three_seconds(ctx, config.bot_error)
        return None
    if ctx.author == member:
        await send_for_three_seconds(ctx, config.self_error)
        return None
    if ctx.author.top_role < member.top_role:
        await send_for_three_seconds(ctx, config.upper_role_error)
        return None
    if ctx.author.top_role < await get_role_by_id(ctx, config.mute_perm_role):
        await send_for_three_seconds(ctx, config.role_perm_error.format(min_role.name))
        return None
    
    await mute(ctx, member, ctx.author, time)



@slash.slash(name='unmute',
             description='Размучивает участника.',
             guild_ids=[config.guild])
async def unmute_command(ctx: SlashContext, member: discord.Member):
    min_role = await get_role_by_id(ctx, config.mute_perm_role)
    if not member.bot:
        if ctx.author != member:
            if ctx.author.top_role > member.top_role:
                if ctx.author.top_role >= await get_role_by_id(ctx, config.mute_perm_role):

                    await unmute(ctx, member, ctx.author)

                else:
                    await send_for_three_seconds(ctx, config.role_perm_error.format(min_role.name))
            else:
                await send_for_three_seconds(ctx, config.upper_role_error)
        else:
            await send_for_three_seconds(ctx, config.self_error)
    else:
        await send_for_three_seconds(ctx, config.bot_error)


#


@slash.slash(name='voting',
             description='Позволяет проводить голосования',
             guild_ids=[config.guild])
async def voting(ctx: SlashContext, name: str, text: str, buttons: str):
    min_role = await get_member_by_role(client, config.voting_perm_role)
    buttons_list = buttons.split('; ')
    if ctx.author.top_role >= min_role:
        await Voting(client=client,
                     name=name,
                     description=text,
                     ctx=ctx,
                     buttons=buttons_list).send_voting()
    else:
        await send_for_three_seconds(ctx, config.role_perm_error.format(min_role.name))


@slash.slash(name='complete_voting',
             description='Завершает голосования',
             guild_ids=[config.guild])
async def complete_voting(ctx: SlashContext, name: str):
    min_role = await get_member_by_role(client, config.voting_perm_role)
    voting = votings[name]
    if voting:
        if ctx.author.top_role >= min_role:
            await voting.complete_voting(ctx)
        else:
            await send_for_three_seconds(ctx, config.role_perm_error.format(min_role))
    else:
        await send_for_three_seconds(ctx, config.voting_not_found)


@slash.slash(name='cancel_voting',
             description='Отменяет голосования',
             guild_ids=[config.guild])
async def cancel_voting(ctx: SlashContext, name: str):
    min_role = await get_member_by_role(client, config.voting_perm_role)
    voting = votings[name]
    if voting:
        if ctx.author.top_role >= min_role:
            await voting.cancel_voting(ctx)
        else:
            await send_for_three_seconds(ctx, config.role_perm_error.format(min_role))
    else:
        await send_for_three_seconds(ctx, config.voting_not_found)


@slash.slash(name='votings_list',
             description='Выводит список всех голований, проводимых в данное время.',
             guild_ids=[config.guild])
async def votings_list(ctx: SlashContext):
    min_role = await get_member_by_role(client, config.voting_perm_role)
    if ctx.author.top_role >= min_role:
        text = ''
        if len(votings.items()) > 0:
            for name, voting in votings.items():
                text = text + name + '\n'
        else:
            text = 'В данный момент голосования не проводятся.'
        embed = discord.Embed(title='Голования, проводимые в данный момент:',
                              description=text,
                              color=config.embed_color)
        await ctx.reply(embed=embed)
    else:
        await send_for_three_seconds(ctx, config.role_perm_error.format(min_role))


@slash.slash(name='lottery',
             description='Позволяет проводить лотереи',
             guild_ids=[config.guild])
async def lottery(ctx: SlashContext, name: str, money: int):
    if ctx.author == ctx.guild.owner:
        await Lottery(client=client,
                      name=name,
                      money=money,
                      ctx=ctx).send_lottery()
    else:
        await send_for_three_seconds(ctx, config.owner_perm_error)


@slash.slash(name='complete_lottery',
             description='Завершает лотереи',
             guild_ids=[config.guild])
async def complete_lottery(ctx: SlashContext, name: str):
    lottery = lotteries[name]
    if lottery:
        if ctx.author == ctx.guild.owner:
            await lottery.complete_lottery(ctx)
        else:
            await send_for_three_seconds(ctx, config.owner_perm_error)
    else:
        await send_for_three_seconds(ctx, config.lottery_not_found)


@slash.slash(name='cancel_lottery',
             description='Отменяет лотереи',
             guild_ids=[config.guild])
async def cancel_lottery(ctx: SlashContext, name: str):
    lottery = lotteries[name]
    if lottery:
        if ctx.author == ctx.guild.owner:
            await lottery.cancel_lottery(ctx)
        else:
            await send_for_three_seconds(ctx, config.owner_perm_error)
    else:
        await send_for_three_seconds(ctx, config.voting_not_found)


@slash.slash(name='lotteries_list',
             description='Выводит список всех лотерей, проводимых в данное время.',
             guild_ids=[config.guild])
async def lotteries_list(ctx: SlashContext):
    if ctx.author == ctx.guild.owner:
        text = ''
        if len(lotteries.items()) > 0:
            for name, lottery in lotteries.items():
                text = text + name + '\n'
        else:
            text = 'В данный момент лотереи не проводятся.'
        embed = discord.Embed(title='Лотереи, проводимые в данный момент:',
                              description=text,
                              color=config.embed_color)
        await ctx.reply(embed=embed)
    else:
        await send_for_three_seconds(ctx, config.owner_perm_error)


#


@slash.slash(name='hentai',
             description='Отправляет хентай.',
             guild_ids=[config.guild])
async def hentai(ctx: SlashContext, num: int = 1, tags: str = ''):
    if ctx.channel.id in [config.nsfw_channel, config.test_channel, config.beta_test_channel]:
        if num < 31:
            if num > 0:
                e = requests.get(f'https://rule34.xxx/index.php?page=dapi&s=post&q=index&tags={tags}')
                root = ET.fromstring(e.text)
                count = int(root.get('count'))

                r = requests.get(f'https://rule34.xxx/index.php?page=dapi&s=post&q=index&'
                                 f'limit={num}&tags={tags}&pid={random.randint(0,(count//num)-1)}')
                root = ET.fromstring(r.text)
                for post in root.findall('post'):
                    await ctx.send(post.get('file_url'))
            else:
                await send_for_three_seconds(ctx, config.lower_zero_time_error)
        else:
            await send_for_three_seconds(ctx, 'Максимальное количество - 30')
    else:
        await send_for_three_seconds(ctx, config.channel_error)


#


@slash.slash(name='call',
             description='Зовет человека на сервер в лс.',
             guild_ids=[config.guild])
async def call(ctx: SlashContext, member: discord.Member):
    min_role = await get_member_by_role(client, config.call_perm_role)
    if ctx.author.top_role >= min_role:
        if not member.bot:
            if ctx.author != member:
                await member.send(member.mention + ' вас зовет ' + ctx.author.display_name +
                                  ' на ' + ctx.guild.name + '.')
                await send_for_three_seconds(ctx, 'Сообщения отправлены')
            else:
                await send_for_three_seconds(ctx, config.self_error)
        else:
            await send_for_three_seconds(ctx, config.bot_error)
    else:
        await send_for_three_seconds(ctx, config.role_perm_error.format(min_role))


@slash.slash(name='flip_coin',
             description='Подбрасывает монетку.',
             guild_ids=[config.guild])
async def flip_coin(ctx: SlashContext):
    embed = discord.Embed(title='Бог рандома вас услышал!',
                          description=random.choice(['Орёл (Да)', 'Решка (Нет)']),
                          color=config.embed_color)
    await ctx.reply(embed=embed)


@slash.slash(name='rip',
             description='Press F to pay respect.',
             guild_ids=[config.guild])
async def rip(ctx: SlashContext):
    embed = discord.Embed(title=ctx.author.display_name + ' сдох.', color=config.embed_color)
    embed.set_image(url=config.rip_image)
    await ctx.reply(embed=embed)


@slash.slash(name='user_info',
             description='Показывает информацию о пользователе.',
             guild_ids=[config.guild])
async def user_info(ctx: SlashContext, member: discord.Member = None):
    min_role = await get_role_by_id(ctx, config.user_info_perm_role)

    if not member:
        member = ctx.author

    if ctx.author.top_role >= min_role:
        info = ''
        info = info + 'Имя в дискорде: ' + member.name + '\n'
        info = info + 'Имя на сервере: ' + member.display_name + '\n'
        info = info + 'Аккаунт создан: ' + member.created_at.strftime("%d %b %Y ") + '\n'
        info = info + 'ID: ' + str(member.id) + '\n'
        info = info + 'Высшая роль: ' + member.top_role.name + '\n'
        info = info + 'Ссылка на аву: ' + str(member.avatar_url) + '\n'
        if member.activity:
            info = info + 'Активность: ' + member.activity.name + '\n'
        embed = discord.Embed(title='Информация о ' + member.display_name,
                              description=info,
                              color=config.embed_color)
        await ctx.reply(embed=embed)
    else:
        await ctx.reply(config.role_perm_error.format(min_role))


@slash.slash(name='id',
             description='Показывает ID пользователя.',
             guild_ids=[config.guild])
async def id(ctx: SlashContext, member: discord.Member = None):
    if not member:
        member = ctx.author

    await ctx.reply('ID пользователя ' + member.display_name + ':\n' + str(member.id))


#


@slash.slash(name='reset_economic',
             description='[DANGER] Сбрасывает экономику [DANGER]',
             guild_ids=[config.guild])
async def reset_economic(ctx: SlashContext, password: str):
    global economics

    if ctx.author == ctx.guild.owner:
        if password == config.password:
            economics.reset_economic(ctx)
            await send_for_three_seconds(ctx, 'Экономика была сброшена!')
        else:
            await send_for_three_seconds(ctx, config.password_error)
    else:
        await send_for_three_seconds(ctx, config.owner_perm_error)


#


@slash.slash(name='money',
             description='Позволяет посмотреть баланс',
             guild_ids=[config.guild])
async def money(ctx: SlashContext, member: discord.Member = None):
    if not member:
        member = ctx.author

    if not member.bot:
        await ctx.reply('Баланс ' + member.display_name + ': ' + str(economic.get_money(member)) + ' $')
    else:
        await ctx.reply(config.bot_error)


@slash.slash(name='give_money',
             description='Выдает деньги человеку',
             guild_ids=[config.guild])
async def give_money(ctx: SlashContext, member: discord.Member, money: float):
    if ctx.author == ctx.guild.owner:
        economic.give_money(member, money)
        await ctx.reply(ctx.author.display_name + ' дал ' + member.display_name + ' ' + str(money) + ' $')
    else:
        await send_for_three_seconds(ctx, config.owner_perm_error)


@slash.slash(name='take_money',
             description='Забирает деньги у человека',
             guild_ids=[config.guild])
async def take_money(ctx: SlashContext, member: discord.Member, money: float):
    if ctx.author == ctx.guild.owner:
        economic.take_money(member, money)
        await ctx.reply(ctx.author.display_name + ' отнял у ' + member.display_name + ' ' + str(money) + ' $')
    else:
        await send_for_three_seconds(ctx, config.owner_perm_error)


@slash.slash(name='set_money',
             description='Устанавливает деньги у человека',
             guild_ids=[config.guild])
async def set_money(ctx: SlashContext, member: discord.Member, money: float):
    if ctx.author == ctx.guild.owner:
        economic.set_money(member, money)
        await ctx.reply(ctx.author.display_name + ' установил у ' + member.display_name + ' ' + str(money) + ' $')
    else:
        await send_for_three_seconds(ctx, config.owner_perm_error)


@slash.slash(name='pay',
             description='Передает деньги',
             guild_ids=[config.guild])
async def pay(ctx: SlashContext, member: discord.Member, money: float):
    if not member.bot:
        if ctx.author != member:
            if economic.get_money(ctx.author) >= money:
                economic.give_money(member, money)
                economic.take_money(ctx.author, money)
                if money == 300:
                    await ctx.reply(ctx.author.display_name + ' передал ' + member.display_name + ' three hundred bucks')
                else:
                    await ctx.reply(ctx.author.display_name + ' передал ' + member.display_name + ' ' + str(money) + ' $')
            else:
                await send_for_three_seconds(ctx, config.not_enough_money_error)
        else:
            await send_for_three_seconds(ctx, config.self_error)
    else:
        await send_for_three_seconds(ctx, config.bot_error)


@slash.slash(name='bet',
             description='Позваляет сделать ставку',
             guild_ids=[config.guild])
async def bet(ctx: SlashContext, money: int):
    if money > 0:
        if economic.get_money(ctx.author) >= money:
            if random.choice([True, False]):
                await ctx.reply(ctx.author.mention + ' выиграл ' + str(money) + ' $')
                economic.give_money(ctx.author, money)
            else:
                await ctx.reply(ctx.author.mention + ' проиграл ' + str(money) + ' $')
                economic.take_money(ctx.author, money)
        else:
            await send_for_three_seconds(ctx, config.not_enough_money_error)
    else:
        await send_for_three_seconds(ctx, config.lower_zero_time_error)



@slash.slash(name='leaderboard',
             description='Отображает таблицу лидеров',
             guild_ids=[config.guild])
async def leaderboard(ctx: SlashContext):
    eco = get_economic()
    members = {}
    leaderboard = {}

    for id, member in eco['members'].items():
        if member['money'] > 0:
            members[id] = member['money']

    for k in sorted(members, key=members.get):
        leaderboard[k] = members[k]

    count = len(leaderboard)
    text = ''
    for member_id, money in leaderboard.items():
        if money == 0:
            continue
        member = discord.utils.get(client.get_all_members(), id=int(member_id))
        text = str(count) + '. ' + member.display_name + '   -   ' + str(round(money)) + ' $\n' + text

        count = count - 1

    embed = discord.Embed(title='Таблица лидеров:',
                          description=text,
                          color=config.embed_color)
    await ctx.reply(embed=embed)
    print(leaderboard)


@slash.slash(name='daily',
             description='Позволяет собрать {} $ раз в день.'.format(config.daily_coins),
             guild_ids=[config.guild])
async def daily(ctx: SlashContext):
    eco = get_economic()

    if eco['members'][str(ctx.author.id)]['daily']:
        eco['members'][str(ctx.author.id)]['daily'] = False
        economic.give_money(ctx.author, float(config.daily_coins))
        
        coin_multiplier = 1
        
        role_ids = []
        
        for role in ctx.author.roles:
            role_ids.append(role.id)
        
        for id, role in economics.roles_shop.items():
            if role['id'] in role_ids:
                coin_multiplier = economics.roles_shop[id]['coin_multiplier']
            
        coins = float(config.daily_coins * coin_multiplier)

        eco['members'][str(ctx.author.id)]['money'] = eco['members'][str(ctx.author.id)]['money'] + coins
        set_economic(eco)
        await send_for_three_seconds(ctx, config.daily_success.format(coins))
    else:
        await send_for_three_seconds(ctx, config.daily_error)


@slash.slash(name='roles_shop',
             description='Открывает магазин ролей',
             guild_ids=[config.guild])
async def roles_shop(ctx: SlashContext):

    text = 'Для покупки введите :\n' \
           '/buy_role (Номер роли в каталоге)\n'

    embed = discord.Embed(title='Магазин ролей:',
                          description=text,
                          color=config.embed_color)

    for num, role_dict in economics.roles_shop.items():

        role = await get_role_by_id(ctx, role_dict['id'])
        embed.add_field(name='```' + str(num) + '. ' + role.name + '```',
                        value='Цена: ' + str(role_dict['price']) + ' $\n')

    await ctx.reply(embed=embed)


@slash.slash(name='buy_role',
             description='Позволяет купить роль',
             guild_ids=[config.guild])
async def buy_role(ctx: SlashContext, id: int):

    if id <= len(economics.roles_shop.keys()):
        role = await get_role_by_id(ctx, economics.roles_shop[id]['id'])
        if not role in ctx.author.roles:
            if economic.get_money(ctx.author) >= economics.roles_shop[id]['price']:
                economic.take_money(ctx.author, economics.roles_shop[id]['price'])
                await ctx.author.add_roles(role)
                await ctx.reply('Поздравляем с покупкой роли **' + role.name + '**!')
            else:
                await send_for_three_seconds(ctx, config.not_enough_money_error)
        else:
            await send_for_three_seconds(ctx, config.has_role_error)
    else:
        await send_for_three_seconds(ctx, config.role_number_error)


@slash.slash(name='works',
             description='Показывает доступные работы',
             guild_ids=[config.guild])
async def works(ctx: SlashContext):

    text = 'Для покупки введите :\n' \
           '/buy_work (Номер работы)\n'

    embed = discord.Embed(title='Список работ:',
                          description=text,
                          color=config.embed_color)
    text = ''

    for id, work in economics.works.items():
        if id == 0:
            continue
        text = text + 'Зарплата: ' + str(work['salary']) + ' $\n'
        text = text + 'Смена: ' + str(round(work['timeout'] / 60)) + ' часов\n'
        text = text + 'Цена: ' + str(work['price']) + ' $\n'
        embed.add_field(name='```' + str(id) + '. ' + work['name'] + '```',
                        value=text)
        text = ''

    await ctx.reply(embed=embed)


@slash.slash(name='buy_work',
             description='Позволяет устроиться на работу',
             guild_ids=[config.guild])
async def buy_work(ctx: SlashContext, id: int):
    eco = get_economic()
    whitelisted_ids = []
    for item_id, item in economics.works.items():
        if item['price'] >= 0:
            whitelisted_ids.append(item_id)
    if id in whitelisted_ids:
        if eco['members'][str(ctx.author.id)]['work'] < id:
            if economic.get_money(ctx.author) >= economics.works[id]['price']:
                eco['members'][str(ctx.author.id)]['work'] = id
                set_economic(eco)
                economic.take_money(ctx.author, economics.works[id]['price'])
                await ctx.reply('Вас приняли на работу ' + economics.works[id]['name'] + '!')
            else:
                await send_for_three_seconds(ctx, config.not_enough_money_error)
        else:
            await send_for_three_seconds(ctx, config.has_item_error)
    else:
        await send_for_three_seconds(ctx, config.id_error)


@slash.slash(name='work',
             description='Выйти на работу',
             guild_ids=[config.guild])
async def work(ctx: SlashContext):

    eco = get_economic()

    member = eco['members'][str(ctx.author.id)]

    if time.time() - member['work_timeout'] > economics.works[member['work']]['timeout'] * 60:

        text = 'Вы успешно вышли на работу ' + economics.works[member['work']]['name'] + '!\n'
        text = text + 'Вы заработали: ' + str(economics.works[member['work']]['salary']) + ' $'

        eco['members'][str(ctx.author.id)]['money'] = eco['members'][str(ctx.author.id)]['money'] + economics.works[member['work']]['salary']
        eco['members'][str(ctx.author.id)]['work_timeout'] = time.time()

        await send_for_three_seconds(ctx, text)

        set_economic(eco)

    else:

        await send_for_three_seconds(ctx, 'До конца вашей смены: **' + str(datetime.timedelta(seconds=round(-(time.time() - member['work_timeout'] - economics.works[member['work']]['timeout'] * 60)))) + '**')


#


@slash.slash(name='rpg_shop',
             description='Открывает магазин',
             guild_ids=[config.guild])
async def rpg_shop(ctx: SlashContext):

    actions = []

    for id, item in RPG.rpg_shop_list.items():
        actions.append(manage_components.create_button(label=item['name'], style=ButtonStyle.gray))
    action_rows = manage_components.create_actionrow(*actions)

    embed = RPG.get_shop(1)

    msg = await ctx.reply(embed=embed,
                          components=[action_rows])

    rpg_shops[msg.id] = 1


@slash.slash(name='buy_weapon',
             description='Позволяет купить оружие',
             guild_ids=[config.guild])
async def buy_weapon(ctx: SlashContext, id: int):
    eco = get_economic()
    whitelisted_ids = []
    for item_id, item in RPG.weapons.items():
        if item['price'] > 0:
            whitelisted_ids.append(item_id)
    if id in whitelisted_ids:
        if eco['members'][str(ctx.author.id)]['inventory']['weapon'] < id:
            if economic.get_money(ctx.author) >= RPG.weapons[id]['price']:
                eco['members'][str(ctx.author.id)]['inventory']['weapon'] = id
                set_economic(eco)
                economic.take_money(ctx.author, RPG.weapons[id]['price'])
                await ctx.reply('Поздравляем с покупкой **' + RPG.weapons[id]['name'] + '**!')
            else:
                await send_for_three_seconds(ctx, config.not_enough_money_error)
        else:
            await send_for_three_seconds(ctx, config.has_item_error)
    else:
        await send_for_three_seconds(ctx, config.id_error)


@slash.slash(name='buy_armor',
             description='Позволяет купить броню',
             guild_ids=[config.guild])
async def buy_armor(ctx: SlashContext, id: int):
    eco = get_economic()
    whitelisted_ids = []
    for item_id, item in RPG.armors.items():
        if item['price'] > 0:
            whitelisted_ids.append(item_id)
    if id in whitelisted_ids:
        if eco['members'][str(ctx.author.id)]['inventory']['armor'] < id:
            if economic.get_money(ctx.author) >= RPG.armors[id]['price']:
                eco['members'][str(ctx.author.id)]['inventory']['armor'] = id
                set_economic(eco)
                economic.take_money(ctx.author, RPG.armors[id]['price'])
                await ctx.reply('Поздравляем с покупкой **' + RPG.armors[id]['name'] + '**!')
            else:
                await send_for_three_seconds(ctx, config.not_enough_money_error)
        else:
            await send_for_three_seconds(ctx, config.has_item_error)
    else:
        await send_for_three_seconds(ctx, config.id_error)


@slash.slash(name='inventory',
             description='Отображает ваш инвентарь',
             guild_ids=[config.guild])
async def inventory(ctx: SlashContext):

    inventory_dict = get_economic()['members'][str(ctx.author.id)]['inventory']
    weapon = RPG.weapons[inventory_dict['weapon']]
    armor = RPG.armors[inventory_dict['armor']]

    embed = discord.Embed(title='Инвентарь ' + ctx.author.display_name + ':',
                          description='',
                          color=config.embed_color)

    embed.add_field(name=f'```Оружие:```',
                    value=weapon['name'] + ' (' + str(weapon['damage']) + ' урона)', inline=False)
    embed.add_field(name=f'```Броня:```',
                    value=armor['name'] + ' (' + str(armor['defence']) + ' защиты)', inline=False)
    text = ''
    for potion_id, potion in inventory_dict['potions'].items():
        if potion['count'] > 0:
            text += f'{potion["name"]} ({potion["count"]})\n'
    if text == '':
        text = 'У вас нет зелий'
    embed.add_field(name=f'```Зелья:```',
                    value=text, inline=False)
    text = ''
    if len(inventory_dict['artifacts']) > 0:
        for item in inventory_dict['artifacts']:
            text = text + item['name'] + '\n'
    else:
        text = 'У вас нет артефактов'
    embed.add_field(name=f'```Артефакты:```',
                    value=text, inline=False)

    await ctx.reply(embed=embed)


@slash.slash(name='hp',
             description='Отображает ваше здоровье',
             guild_ids=[config.guild])
async def hp(ctx: SlashContext):
    eco = get_economic()

    health = eco['members'][str(ctx.author.id)]['health']

    await send_for_three_seconds(ctx, f'Ваше hp состовляет: {health}')


@slash.slash(name='buy_potion',
             description='Позволяет купить зелье',
             guild_ids=[config.guild])
async def buy_potion(ctx: SlashContext, id: int):
    eco = get_economic()
    strength = id % 10
    potion_id = id // 10

    if potion_id in RPG.potions.keys():
        effect = (strength ** 2) * 5
        price = effect * 10 * RPG.potions[potion_id]['price_multiplier']
        name = RPG.potions[potion_id]['name'].format(toRoman(strength))

        if economic.get_money(ctx.author) >= price:
            count = eco['members'][str(ctx.author.id)]['inventory']['potions'][str(potion_id)]['count'] + 1
            
            eco['members'][str(ctx.author.id)]['inventory']['potions'].pop(str(potion_id))
            eco['members'][str(ctx.author.id)]['inventory']['potions'][str(potion_id)] = {'strength': strength,
                                                                                          'name': name,
                                                                                          'count': count}
            set_economic(eco)
            economic.take_money(ctx.author, price)
            await ctx.reply(f'Поздравляем с покупкой **{name}**!')
        else:
            await send_for_three_seconds(ctx, config.not_enough_money_error)
    else:
        await send_for_three_seconds(ctx, config.id_error)


@slash.slash(name='dungeons',
             description='Отображает список данжей',
             guild_ids=[config.guild])
async def dungeons(ctx: SlashContext):
    text = 'Для похода в данж введите: \n' \
           '/dungeon (Номер данжа)\n'

    embed = discord.Embed(title='Список данжей:',
                          description=text,
                          color=config.embed_color)

    text = ''

    for id, dungeon in RPG.dungeons.items():
        text = text + 'Враги:  \n'
        for mob in dungeon['mobs']:
            text = text + f'_ _ {mob["name"].replace("{m}", "").replace("{f}", "")} ({mob["health"]} hp, {mob["damage"]} атаки) \n'
        embed.add_field(name=f'```{id}. {dungeon["name"]}```',
                        value=text, inline=False)
        text = ''

    await ctx.reply(embed=embed)


@slash.slash(name='dungeon',
             description='Позволяет пойти в данж',
             guild_ids=[config.guild])
async def dungeon(ctx: SlashContext, id: int):
    eco = get_economic()

    if eco['members'][str(ctx.author.id)]['dungeon_timeout'] < time.time():
        if id in RPG.dungeons.keys():
            for active_dungeon in active_dungeons.values():
                if active_dungeon.member == ctx.author:
                    await ctx.reply('Ты аферист?')
                    return None
            dungeon = Dungeon(ctx, dungeon_id=id)
            await dungeon.create_dungeon()
        else:
            await send_for_three_seconds(ctx, config.id_error)
    else:
        await send_for_three_seconds(ctx, 'Вы слишком устали, чтобы идти в данж.\n'
                                          'Вы сможете пойти в данж только через **' + str(datetime.timedelta(seconds=round(eco['members'][str(ctx.author.id)]['dungeon_timeout'] - time.time()))) + '**')


#


@slash.slash(name='join',
             description='Подключает бота к голосовому каналу',
             guild_ids=[config.guild])
async def join(ctx: SlashContext):
    if ctx.author.voice.channel:
        if ctx.author.voice.channel in active_voices.keys():
            await ctx.reply('Бот и так подключен к вашему голосовому каналу')
        else:
            for channel in active_voices.keys():
                if channel.guild == ctx.guild:
                    await active_voices[channel].delete()
                    print('канал удален')
                    break
            await Music(client, ctx.author.voice.channel).connect()
            await ctx.reply('Подключился')
    else:
        await ctx.reply(config.voice_channel_error)


@slash.slash(name='play',
             description='Включает музыку',
             guild_ids=[config.guild])
async def play(ctx: SlashContext, music: str):
    if ctx.author.voice.channel:
        if ctx.author.voice.channel in active_voices.keys():
            await active_voices[ctx.author.voice.channel].play(ctx, music)
        else:
            for channel in active_voices.keys():
                if channel.guild == ctx.guild:
                    await active_voices[channel].delete()
                    break
            _music = Music(client, ctx.author.voice.channel)
            await _music.connect()
            await _music.play(ctx, music)
    else:
        await ctx.reply(config.voice_channel_error)
        

@slash.slash(name='leave',
             description='Покидает голосовой канал',
             guild_ids=[config.guild])
async def leave(ctx: SlashContext):
    is_leave = False
    
    for channel in active_voices.keys():
        if channel.guild == ctx.guild:
            await active_voices[channel].delete()
            await ctx.reply('Ок👌')
            is_leave = True
            break
    
    if not is_leave:
        await ctx.reply('Бот и так не подключен')


@slash.slash(name='aboba',
             description='Покидает голосовой канал',
             guild_ids=[config.guild])
async def aboba(ctx: SlashContext):
    voice: discord.VoiceClient = await ctx.author.voice.channel.connect()
    
    await voice.play(discord.FFmpegPCMAudio(executable="ffmpeg.exe", source='slava-marlow-snova-ya-napivayus-mp3.mp3'))

#


@slash.slash(name='restart',
             description='Перезагружает бота',
             guild_ids=[config.guild])
async def restart(ctx: SlashContext):
    if ctx.author == ctx.guild.owner:
        write_log('restarting')
        await ctx.reply('Перезагружаюсь')
        os.system('python3 ' + str(os.getcwd() + '\\bot.py') + '')
        print('restarting')
        exit()
    else:
        await send_for_three_seconds(ctx, config.owner_perm_error)


@slash.slash(name='off',
             description='Выключает бота',
             guild_ids=[config.guild])
async def off(ctx: SlashContext):
    if ctx.author == ctx.guild.owner:
        write_log('exiting')
        await ctx.reply('Выключаюсь')
        print('exiting')
        exit()
    else:
        await send_for_three_seconds(ctx, config.owner_perm_error)


client.run(config.token)
