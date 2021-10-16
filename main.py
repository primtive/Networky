import discord, os, re, json, hmtai, random, requests, datetime, asyncio
from datetime import datetime
from datetime import date
from exchanges.bitfinex import Bitfinex
import config
from config import console
from random import randint
from random import uniform
from random import choice
from discord.ext import commands
from discord.utils import get
from collections import OrderedDict

intents = discord.Intents.default()
intents.members = True

help_msgs = []
mine_msgs = {}
color_msgs = []
comp_msgs = {}
count = 1
day_month = {1: 31, 2: 28, 3: 31, 4: 30, 5: 31, 6: 30, 7: 31, 8: 31, 9: 30, 10: 31, 11: 30, 12: 31}

year = date.today().year
if not os.path.exists(os.path.join(os.getcwd(), 'dz', str(year))):
    os.mkdir(os.path.join(os.getcwd(), 'dz', str(year)))
    for month in range(12):
        os.mkdir(os.path.join(os.getcwd(), 'dz', str(year), str(month+1)))
        for day in range(day_month.get(month+1)):
            os.mkdir(os.path.join(os.getcwd(), 'dz', str(year), str(month+1), str(day+1)))

client = commands.Bot(command_prefix=config.prefix, intents=intents)
banhammer_urls = ('777867435754782720/1.png','777867438741258240/3.png','777867439550890024/2.png','777867440699998228/4.png','777867442436964372/5.png','777867443238207488/6.png','777867446483943444/8.png','777867448119853066/9.png','777867449134481418/10.png','777867445700001792/7.png','777867521574830110/16.png','777867524774952971/8.png','777867528386641930/9.png','777867532417630238/10.png','777867536775381012/11.png','777867541006647356/12.png','777867544421728256/13.png','777867549474947072/14.png','777867554570895370/15.png')

@client.event
async def on_ready():
    comp_msgs = await read_file('comps.txt')
    print('online')
    print('console: '+str(console))
    await client.change_presence(activity=discord.Activity(type=config.default_activity_type, name=config.default_activity_text))

@client.event
async def on_message(msg):
    if type(msg.channel) == discord.channel.DMChannel:
        if msg.channel.recipient in client.get_guild(config.server_id).members and not msg.author.bot:
            if msg.content.startswith('#'):
                if re.findall('#disconnect \d{18}', msg.content):
                    member_id = int(msg.content.split(' ')[1])
                    print(member_id)
                    if await check_money(msg.author) >= 500:
                        if get(client.get_all_members(), id=member_id).voice:
                            await take_money(500, msg.author)
                            member = get(client.get_all_members(), id=member_id)
                            await member.move_to(None)
                            await msg.author.send('Пользователь кикнут')
                        else:
                            await msg.author.send('Ошибка: Пользователь не в голосовом канале')
                    else:
                        await msg.author.send('Ошибка: У вас недостаточно денег.')
                if re.findall('#voicemute \d{18} \d{1,3}', msg.content):
                    member_id = int(msg.content.split(' ')[1])
                    time = int(msg.content.split(' ')[2])
                    sum = time * 100
                    if await check_money(msg.author) >= sum:
                        if get(client.get_all_members(), id=member_id).voice:
                            if time <= 60:
                                await take_money(sum, msg.author)
                                member = get(client.get_all_members(), id=member_id)
                                await member.edit(mute=True)
                                await msg.author.send('Пользователю выключен микрофон, списано ' + str(sum) + '$.')
                                await asyncio.sleep(time)
                                await member.edit(mute=False)
                                await msg.author.send('Пользователю включен микрофон.')
                            else:
                                await msg.author.send('Ошибка: Предел мута - 60 секунд.')
                        else:
                            await msg.author.send('Ошибка: Пользователь не в голосовом канале')
                    else:
                        await msg.author.send('Ошибка: У вас недостаточно денег.')
                else:
                    await msg.author.send('Ошибка: Неправильная команда / использование команды')
            else:
                await msg.author.send('Команды в лс используются для подшучивания над игроками на сервере за игровую валюту. Список команд дан тут.\n#disconnect (Discord ID участника)  -  Отключение участника от голосового канала (500$)\n#voicemute (Discord ID участника) (время в секундах до 60 секунд)  -  Мут в голосовом канале, 1 сек - 100$')

    if msg.content.startswith('#'):
        file = open('log.txt', 'a')
        now = datetime.now()
        #dt_string = now.strftime("<%d-%m-%Y %H:%M:%S>")
        #file.write(dt_string + ' ' + msg.author.name + ': ' + msg.content + '\n')
        file.close()
        if not type(msg.channel) == discord.channel.DMChannel:
            await msg.delete()
        if console:
            print(msg.author.name + ': ' + msg.content)
    else:
        if not msg.author.bot:
            if client.user.mention in msg.content:
                await msg.channel.send('Не упоминайте меня, это грузит систему')
            if not msg.channel.id == 319283791273:
                economic = await read_file('economic.txt')
                mine_level = economic.get(str(msg.author.id)).get('mine')
                if mine_level > 0:
                    await give_btc(mine_level/10000, msg.author)
                await give_money(5, msg.author)
    '''if msg.content == 'Обновление биткойна':
        await msg.delete()
        open('btc_multi.txt', 'w').write(uniform(float(open('btc_multi.txt', 'r').read().close())-0.2, float(open('btc_multi.txt', 'r').read().close())+0.2)).close()'''
    if not type(msg.channel) == discord.channel.DMChannel:
        await client.process_commands(msg)

@client.event
async def on_reaction_add(reaction, author):
    global count

    if reaction.message.id in help_msgs:
        if reaction.emoji == '⬅️':
            count = count - 1
        if reaction.emoji == '➡️':
            count = count + 1
        if count < 1:
            count = 1
        if count > 5:
            count = 5
        if count == 1:
            newcontent = 'Главные команды:\nПока нет'
        if count == 2:
            newcontent = 'Экономика:\n#balance - узнать свой баланс\n#balance (кого) - узнать чей-то баланс\n#shop - магазин ролей\n#buy (номер) - купить что-то в магазине\n#nick (новый ник) - поменять ник (стоит 50 $)\n#bet ($) - ставки\n#leaderboard - топ по активам (деньгам, биткойнам и ролям)\n#pay (кому) ($) - передать деньги'
        if count == 3:
            newcontent = 'Биткойны:\n#btc - узнать курс биткойна\n#btc_balance - узнать свой биткойн баланс\n#btc_balance (кого) - узнать чей-то биткойн баланс\n#btc_buy ($) - купить биткойн (в долларах)\n#btc_sell ($) - продать биткойн (в долларах)'
        if count == 4:
            newcontent = '3'
        if count == 5:
            newcontent = '4'
        await reaction.message.edit(content=newcontent)
    if reaction.message.id in comp_msgs.keys():
        sum = int(comp_msgs[reaction.message.id]['sum'])
        players = int(comp_msgs[reaction.message.id]['players'])
        check = get(reaction.message.reactions, emoji=reaction.emoji)
        if check.count >= players:
            pre_winners = []
            async for member in check.users():
                if not member.bot:
                    pre_winners.append(member)
            winner = choice(pre_winners)
            await check.message.channel.send('Поздравляем победителя!\n' + winner.mention + ' выигрывает ' + str(sum) + ' $')
            await give_money(sum, winner)
            await check.message.delete()
            comp_msgs.pop(check.message)
            write_file('comps.txt', json.dumps(comp_msgs,indent=4))
    if reaction.message in mine_msgs.keys() and reaction.emoji == '⬆':
        if author.id == mine_msgs[reaction.message]:
            economic = await read_file('economic.txt')
            mine_level = economic.get(str(mine_msgs[reaction.message])).get('mine')
            print(mine_level)
            if await check_money(author) > mine_level*500:
                member = mine_msgs[reaction.message]
                economic = await read_file('economic.txt')
                for v, k in economic.items():
                    if v == str(member):
                        economic.get(str(member)).update({'mine': mine_level+1})
                        economic.update({str(member): economic.get(str(member))})
                        open('economic.txt', 'w').close()
                        await write_file('economic.txt', json.dumps(economic,indent=4))
                await take_money(mine_level*500, author)
                await reaction.message.channel.send('Куплена ' + str(mine_level+1) + '-я майнинг ферма')
            else:
                await reaction.message.channel.send('У вас недостаточно денег')
    if reaction.message in color_msgs:
        await author.remove_roles(get(reaction.message.guild.roles, name='Фиолетовый'))
        await author.remove_roles(get(reaction.message.guild.roles, name='Синий'))
        await author.remove_roles(get(reaction.message.guild.roles, name='Коричневый'))
        await author.remove_roles(get(reaction.message.guild.roles, name='Зеленый'))
        await author.remove_roles(get(reaction.message.guild.roles, name='Оранжевый'))
        await author.remove_roles(get(reaction.message.guild.roles, name='Красный'))
        await author.remove_roles(get(reaction.message.guild.roles, name='Желтый'))
        await author.remove_roles(get(reaction.message.guild.roles, name='Белый'))

        if reaction.emoji == '🟪':
            role = get(author.guild.roles, name='Фиолетовый')
            await author.add_roles(role)
        if reaction.emoji == '🟦':
            role = get(author.guild.roles, name='Синий')
            await author.add_roles(role)
        if reaction.emoji == '🟫':
            role = get(author.guild.roles, name='Коричневый')
            await author.add_roles(role)
        if reaction.emoji == '🟩':
            role = get(author.guild.roles, name='Зеленый')
            await author.add_roles(role)
        if reaction.emoji == '🟧':
            role = get(author.guild.roles, name='Оранжевый')
            await author.add_roles(role)
        if reaction.emoji == '🟥':
            role = get(author.guild.roles, name='Красный')
            await author.add_roles(role)
        if reaction.emoji == '🟨':
            role = get(author.guild.roles, name='Желтый')
            await author.add_roles(role)
        if reaction.emoji == '⬜':
            role = get(author.guild.roles, name='Белый')
            await author.add_roles(role)
        if reaction.emoji == '🇫':
            pass

@client.event
async def on_reaction_remove(reaction, author):
    global count
    if reaction.message.id in help_msgs:
        if reaction.emoji == '⬅️':
            count = count - 1
        if reaction.emoji == '➡️':
            count = count + 1
        if count < 1:
            count = 1
        if count > 5:
            count = 5
        if count == 1:
            newcontent = 'Главные команды:\nПока нет'
        if count == 2:
            newcontent = 'Экономика:\n#balance - узнать свой баланс\n#balance (кого) - узнать чей-то баланс\n#shop - магазин ролей\n#buy (номер) - купить что-то в магазине\n#nick (новый ник) - поменять ник (стоит 50 $)\n#bet ($) - ставки\n#leaderboard - топ по активам (деньгам, биткойнам и ролям)\n#pay (кому) ($) - передать деньги'
        if count == 3:
            newcontent = 'Биткойны:\n#btc - узнать курс биткойна\n#btc_balance - узнать свой биткойн баланс\n#btc_balance (кого) - узнать чей-то биткойн баланс\n#btc_buy ($) - купить биткойн (в долларах)\n#btc_sell ($) - продать биткойн (в долларах)'
        if count == 4:
            newcontent = '3'
        if count == 5:
            newcontent = '4'

        await reaction.message.edit(content=newcontent)


@client.command()
async def rip(ctx, member:discord.Member = None):
    if ctx.author.nick:
        nick = ctx.author.nick
    else:
        nick = ctx.author.name
    if member:
        if member.nick:
            mnick = member.nick
        else:
            mnick = member.name
        embed = discord.Embed(color = 0xffffff, title = mnick + ' сдох')
        embed.set_image(url="https://tenor.com/view/rip-coffin-black-ghana-celebrating-gif-16743302")
        await ctx.channel.send(embed=embed)
    else:
        embed = discord.Embed(color = 0xffffff, title = nick + ' сдох')
        embed.set_image(url='https://tenor.com/view/rip-coffin-black-ghana-celebrating-gif-16743302')
        await ctx.channel.send(embed=embed)

@client.command()
async def voting(ctx, arg):
    if :
        voting_text = arg.replace('_',' ')
        embed = discord.Embed(color = 0xffffff, title = ctx.message.author.name+' объявляет голосование!', description = '@everyone '+voting_text)
        voting_message = await ctx.send(embed = embed)
        await voting_message.add_reaction('👍')
        await voting_message.add_reaction('👎')
    else:
        await ctx.channel.send('Делать голосования можно только в канале "Голосования"!')

@client.command()
async def hentai(ctx, num = 1, category_lib:str = ''):
    if ctx.channel.id == config.nsfw_channel:
        if num < 31:
            if category_lib != '':
                for i in range(num):
                    await ctx.send(hmtai.useHM(version='v1', category=category_lib))
            else:
                for i in range(num):
                    await ctx.send(hmtai.useHM(version='v1', category='hentai'))
        else:
            await ctx.send('Максимальное количество - 30')
    else:
        await ctx.send('Вы не можете использовать эту команду здесь.')

@client.command()
async def mem(ctx, num = 1):
    if ctx.channel.id == config.nsfw_channel:
        if num < 31:
            for i in range(num):
                await ctx.send(hmtai.useHM(version='v1', category=category_lib))
        else:
            await ctx.send('Максимальное количество - 30')
    else:
        await ctx.send('Вы не можете использовать эту команду здесь.')

@client.command()
async def call(ctx, member:discord.Member):
    if member.id != config.server_owner_id:
        for i in range(15):
            await member.send(member.mention)
        await ctx.send('Сообщения отправлены')
    else:
        await ctx.send('😠')

@client.command()
async def random(ctx, arg):
    array = arg.split(',')
    answer = array[(randint(0, len(array)-1))]
    embed = discord.Embed(color = 0xffffff, title = 'Бог рандома вас услышал!', description = ('И он сказал: '+answer))
    await ctx.send(embed = embed)

@client.command()
async def ban(ctx, member:discord.Member, reason=None):
    if ctx.message.author.id == member.id:
        ctx.channel.send('Вы не можете забанить себя')
    if ctx.message.author.top_role > member.top_role:
        if reason:
            embed = discord.Embed(color = 0xffffff, title = (member.name+' был забанен!'), description = ('Администратор '+ctx.author.name+' забанил участника '+member.name+' по причине: '+reason))
        else:
            embed = discord.Embed(color = 0xffffff, title = (member.name+' был забанен!'), description = ('Администратор '+ctx.author.name+' забанил участника '+member.name+'.'))
        random_banhammer = 'https://cdn.discordapp.com/attachments/643078066716803073/'+banhammer_urls[randint(0,15)]
        embed.set_image(url=random_banhammer)
        await ctx.channel.send(embed = embed)
        await ctx.guild.ban(member, reason=reason)
    else:
        ctx.channel.send(ctx.message.author.mention+' роль '+member.name+' выше вашей.')

@client.command()
async def kick(ctx, member:discord.Member, reason=None):
    if ctx.message.author.id == member.id:
        ctx.channel.send('Вы не можете кикуть себя')
    if ctx.message.author.top_role > member.top_role:
        if reason:
            embed = discord.Embed(color = 0xffffff, title = (member.name+' был кикнут!'), description = ('Администратор '+ctx.author.name+' кикнул участника '+member.name+' по причине: '+reason))
        else:
            embed = discord.Embed(color = 0xffffff, title = (member.name+' был кикнут!'), description = ('Администратор '+ctx.author.name+' кикнул участника '+member.name+'.'))
        await ctx.channel.send(embed = embed)
        await ctx.guild.kick(member, reason=reason)
    else:
        ctx.channel.send(ctx.message.author.mention+' роль '+member.name+' выше вашей.')

@client.command()
async def user_info(ctx, member:discord.Member):
    roles_text = ''
    for role in member.roles[1:]:
        roles_text = role.name + '\n'
    info = 'Ник на сервере: '+member.nick+'\nАва: '+str(member.avatar_url)+'\nВысшая роль: '+roles_text
    embed = discord.Embed(color = 0xffffff, title = ('Информация '+member.name), description = info)
    await ctx.channel.send(embed = embed)

@client.command()
async def bot_activity(ctx, arg, arg2):
    activity_type=config.default_activity_type
    arg2 = arg2.replace('_',' ')
    if arg.lower == 'play':
        activity_type=discord.ActivityType.playing
    elif arg.lower == 'listen':
        activity_type=discord.ActivityType.listening
    elif arg.lower == 'watch':
        activity_type=discord.ActivityType.watching
    elif arg.lower == 'custom':
        activity_type=discord.ActivityType.custom
    elif arg.lower == 'default':
        activity_type=config.default_activity_type
        arg2 = config.default_activity_text
    else:
        await ctx.channel.send('Неверный тип активности')
        arg2 = config.default_activity_text

        activity = discord.Activity(name=arg2, type=activity_type)
        await ctx.channel.send('Установлена активность: '+str(activity_type)[13:]+' '+arg2)
    await client.change_presence(activity=activity)

@client.command()
async def bot_status(ctx, arg):
    status = config.default_status
    if arg.lower() == 'online':
        status=discord.Status.online
    elif arg.lower() == 'offline':
        status=discord.Status.offline
    elif arg.lower() == 'idle':
        status=discord.Status.idle
    elif arg.lower() == 'dnd':
        status=discord.Status.dnd
    elif arg.lower() == 'default':
        status = config.default_status
    else:
        await ctx.channel.send('Указан неверный статус!')
    await client    .change_presence(status=status)
    await ctx.channel.send('Статус сменён на: '+str(status))

@client.command()
async def exit(ctx):
    if ctx.author.id == config.server_owner_id:
        await ctx.channel.send('Всем пока!')
        await client.logout()
        await input()
    else:
        await ctx.channel.send(config.permission_error)

@client.command()
async def mute(ctx, member:discord.Member, time:int, reason=None):
    if ctx.message.author.id == member.id:
        ctx.channel.send('Вы не можете замутить себя')
    if ctx.message.author.top_role > member.top_role:
        if reason:
            embed = discord.Embed(color = 0xffffff, title = (member.name+' был замучен!'), description = ('Администратор '+ctx.message.author.name+' замутил участника '+member.name+' на '+str(time)+' минут, по причине: '+reason))
            await ctx.send(embed=embed)
        else:
            embed = discord.Embed(color = 0xffffff, title = (member.name+' был замучен!'), description = ('Администратор '+ctx.message.author.name+' замутил участника '+member.name+' на '+str(time)+' минут'))
            await ctx.send(embed=embed)
        await member.add_roles(discord.Role(config.muted_role_id))
        await asyncio.sleep(time * 60)
        await member.remove_roles(discord.Role(config.muted_role_id))
    else:
        await ctx.channel.send(ctx.message.author.mention+' роль '+member.name+' выше вашей.')

@client.command()
async def tea(ctx):
    await ctx.send(embed=discord.Embed(color = 0xffffff, title = (ctx.message.author.name+' предлагает попить чай!'), description = ('Все кто хочет ждём в голосовом!')))

client.remove_command('help')
@client.command()
async def help(ctx):
    global count
    count = 1
    msg = await ctx.send('Главные команды:\nПока нет')
    await msg.add_reaction('⬅️')
    await msg.add_reaction('➡️')
    help_msgs.append(msg.id)

async def read_file(file_name):
    file = open(file_name, 'r')
    return json.loads(file.read())
    file.close()

async def write_file(file_name,content):
    file = open(file_name, 'w+')
    file.write(content)
    file.close()


#eco start


@client.command()
async def eco_rst(ctx):
    if ctx.author.id == config.server_owner_id:
        economic = {}
        guild_members_list = await ctx.guild.fetch_members(limit=None).flatten()
        for member in guild_members_list:
            economic[member.id] = {'money': 0, 'btc': 0, 'mine': 0}
        await write_file('economic.txt', json.dumps(economic,indent=4))
        await ctx.channel.send('Экономика была сброшена!')
    else:
        await ctx.channel.send(config.permission_error)

@client.command()
async def guild_members(ctx):
    members_list = await ctx.guild.fetch_members(limit=None).flatten()
    members_name_list = list()
    for member in members_list:
        members_name_list.append(member.mention)
    await ctx.channel.send(members_name_list)

@client.command()
async def give(ctx,member:discord.Member,money:int):
    if ctx.author.id in config.server_admins:
        new_money = int(await check_money(member)) + money
        await set_money(new_money, member)
        await ctx.channel.send(member.mention+' выдано '+str(money)+' $!')
    else:
        await ctx.channel.send(config.permission_error)

@client.command()
async def set(ctx,member:discord.Member,money:int):
    if ctx.author.id in config.server_admins:
        await set_money(money, member)
        await ctx.channel.send('Теперь у '+member.mention+' '+str(money)+' $!')
    else:
        await ctx.channel.send(config.permission_error)

@client.command()
async def balance(ctx,member:discord.Member=None):
    if member:
        if member.id in config.server_admins:
            await ctx.channel.send('Баланс '+member.mention+' - ∞.')
        else:
            balance = await check_money(member)
            await ctx.channel.send('Баланс '+member.mention+' - '+str(balance)+' $.')
    else:
        balance = await check_money(ctx.author)
        await ctx.channel.send('Ваш баланс - '+str(balance)+' $.')

@client.command()
async def money(ctx,member:discord.Member=None):
    if member:
        if member.id in config.server_admins:
            await ctx.channel.send('Баланс '+member.mention+' - ∞.')
        else:
            balance = await check_money(member)
            await ctx.channel.send('Баланс '+member.mention+' - '+str(balance)+' $.')
    else:
        balance = await check_money(ctx.author)
        await ctx.channel.send('Ваш баланс - '+str(balance)+' $.')

#@client.command()
#async def ботдайденег(ctx):
#    await give_money(1000000, ctx.author)

async def check_money(member:discord.Member):
    economic = await read_file('economic.txt')
    return int(economic.get(str(member.id)).get('money'))

async def set_money(sum:int, member:discord.Member):
    economic = await read_file('economic.txt')
    for v, k in economic.items():
        if v == str(member.id):
            economic.get(str(member.id)).update({'money': sum})
            economic.update({str(member.id): economic.get(str(member.id))})
            open('economic.txt', 'w').close()
            await write_file('economic.txt', json.dumps(economic,indent=4))

async def give_money(sum:int, member:discord.Member):
    economic = await read_file('economic.txt')
    for v, k in economic.items():
        if v == str(member.id):
            economic.get(str(member.id)).update({'money': await check_money(member)+sum})
            economic.update({str(member.id): economic.get(str(member.id))})
            open('economic.txt', 'w').close()
            await write_file('economic.txt', json.dumps(economic,indent=4))

async def take_money(sum:int, member:discord.Member):
    economic = await read_file('economic.txt')
    for v, k in economic.items():
        if v == str(member.id):
            economic.get(str(member.id)).update({'money': await check_money(member)-sum})
            economic.update({str(member.id): economic.get(str(member.id))})
            open('economic.txt', 'w').close()
            await write_file('economic.txt', json.dumps(economic,indent=4))

@client.command()
async def shop(ctx):
    shop_file = open('shop.txt', 'r')
    shop = json.loads(shop_file.read())
    shop_file.close()
    message_content = ''
    for v, k in shop.items():
        message_content = message_content + '\n' + str(len(message_content.split('\n'))) + '. ' + ctx.guild.get_role(int(v)).name + '  -  ' + str(k) + ' $'
    message_content = message_content + '\nДля покупки: #buy номер'
    await ctx.send(message_content)

@client.command()
async def buy(ctx, number:int):
    if number < 0:
        await ctx.channel.send('Вы не можете использовать отрицательные числа')
        return None
    shop_file = open('shop.txt', 'r')
    shop = json.loads(shop_file.read())
    shop_file.close()
    price = int(list(shop.values())[number-1])
    if(await check_money(ctx.author) > price and not ctx.guild.get_role(int(list(shop.keys())[number-1])) in ctx.author.roles):
        await take_money(price, ctx.author)
        await ctx.author.add_roles(ctx.guild.get_role(int(list(shop.keys())[number-1])))
        await ctx.send(ctx.author.mention + ' купил роль ' + ctx.guild.get_role(int(list(shop.keys())[number-1])).name+'!')
    else:
        await ctx.send('Вы не можете купить ' + ctx.guild.get_role(int(list(shop.keys())[number-1])).name)


@client.command()
async def nick(ctx, new_nick):
    balance = await check_money(ctx.author)
    if ctx.author.nick:
        nick = ctx.author.nick
    else:
        nick = ctx.author.name
    if balance >= 50:
        if ctx.author.nick != new_nick:
            await set_money(await check_money(ctx.author)-50, ctx.author)
            await ctx.author.edit(nick=new_nick)
            await ctx.channel.send('Ник изменен на: ' + new_nick + '!   ')
        else:
            await ctx.channel.send('Вы не можете поменять свой ник на такой же')
    else:
        await ctx.channel.send('У вас недостаточно денег')

@client.command()
async def color(ctx):
    msg = await ctx.channel.send('Для смены цвета, поставьте эмодзи.')
    await msg.add_reaction('🟪')
    await msg.add_reaction('🟦')
    await msg.add_reaction('🟫')
    await msg.add_reaction('🟩')
    await msg.add_reaction('🟧')
    await msg.add_reaction('🟥')
    await msg.add_reaction('🟨')
    await msg.add_reaction('⬜')
    await msg.add_reaction('🇫')
    color_msgs.append(msg)

@client.command()
async def bet(ctx, sum:int):
    if sum < 0:
        await ctx.channel.send('Вы не можете использовать отрицательные числа')
        return None
    if sum == 0:
        await ctx.channel.send('Вы не можете использовать 0')
        return None
    balance = await check_money(ctx.author)
    if balance >= sum:
        if choice([True, False]):
            await ctx.channel.send(ctx.author.mention + ' выиграл ' + str(sum) + ' $')
            await give_money(sum, ctx.author)
        else:
            await ctx.channel.send(ctx.author.mention + ' проиграл ' + str(sum) + ' $')
            await take_money(sum, ctx.author)
    else:
        await ctx.channel.send('У вас недостаточно денег')

def get_dz(day, month, year):
    file = file.open(os.path.join(os.getcwd(), 'dz', year, month, day))


@client.command()
async def dz(ctx, dzdate:str = None):
    if dzdate:
        year = date.today().year
        day, month = dzdate.split('.')
        if day.startswith('0'):
            day = day[1:]
        if month.startswith('0'):
            month = month[1:]
        path = os.path.join(os.getcwd(), 'dz', str(year), str(month), str(day), 'dz.png')
        print(path)
        if os.path.exists(path):
            file = discord.File(path)
            await ctx.send('Электронный дневник на ' + dzdate + ':', file = file)
        else:
            await ctx.send('Электронный дневник на эту дату не выложен')

    else:
        year = date.today().year
        day = date.today().day + 1
        month = date.today().month
        path = os.path.join(os.getcwd(), 'dz', str(year), str(month), str(day), 'dz.png')
        print(path)
        if len(str(day)) == 1:
            day = '0' + str(day)
        if len(str(month)) == 1:
            month = '0' + str(month)
        if os.path.exists(path):
            file = discord.File(path)
            await ctx.send('Электронный дневник на завтра (' + str(day) + '.' + str(month) + '):', file = file)
        else:
            await ctx.send('Электронный дневник на эту дату не выложен')

@client.command()
async def comp(ctx, sum:int, players:int):
    if ctx.author.id in config.server_admins:
        msg = await ctx.send(ctx.author.mention + ' объявляет розыгрыш на ' + str(sum) + '$ для ' + str(players-1) + ' человек!\nДля участия поставьте ✅ ')
        await msg.add_reaction('✅')
        comp_msgs[msg.id] = {'players': players, 'sum': sum}
        write_file('comps.txt', json.dumps(comp_msgs,indent=4))
    else:
        await ctx.channel.send('Вы не можете начать конкурс.')

@client.command()
async def ecomp(ctx, ads):
    pass

@client.command()
async def say(ctx, *text):
    if ctx.author.id in config.server_admins:
        ftext = ''
        for word in text:
            ftext = ftext + word + ' '
        await ctx.send(ftext)
    else:
        await ctx.send('Недостаточно прав')

@client.command()
async def leaderboard(ctx):
    economic = await read_file('economic.txt')
    moneys = {}
    leaderboard = {}
    btc = await get_btc()
    for member_id in list(economic.keys()):
        member = get(client.get_all_members(), id=int(member_id))
        moneys[member_id] = economic.get(member_id)['money'] + (await check_btc(member) * btc)
    shop = await read_file('shop.txt')
    for k, v in shop.items():
        for member_id, money in moneys.items():
            member = get(client.get_all_members(), id=int(member_id))
            for role in member.roles:
                if role.id == int(k):
                    moneys[member_id] = moneys[member_id] + v

    '''economic = await read_file('economic.txt')
    mine_level = economic.get(str(member.id)).get('mine')
    for member_id in moneys.items():
        mine_level = economic.get(str(member_id)).get('mine')
        mine_count = 0
        for i in range(mine_level):
            mine_count = mine_count + i
        moneys[member_id] = moneys[member_id] + mine_count*500'''
    for k in sorted(moneys, key=moneys.get, reverse=True):
        leaderboard[k] = moneys[k]
    msg = ''
    count = 1
    for member_id, money in leaderboard.items():
        if int(member_id) in config.server_admins:
            continue
        if money == 0:
            break
        member = get(client.get_all_members(), id=int(member_id))
        nick = member.nick
        if not nick:
            nick = member.name
        msg = msg + '\n' + str(count) + '. ' + nick + '   -   ' + str(round(money)) + ' $'
        count = count + 1
    await ctx.channel.send(msg)
    print(leaderboard)

@client.command()
async def pay(ctx, member:discord.Member, sum:int):
    if member.bot:
        await ctx.channel.send('Боту нельзя отправить деньги')
        return None
    if member == ctx.author:
        await ctx.channel.send('Себе нельзя отправить деньги')
        return None
    if await check_money(ctx.author) >= sum:
        await take_money(sum, ctx.author)
        await give_money(sum, member)
        await ctx.channel.send(ctx.author.mention + ' передал ' + member.mention + ' ' + str(sum) + ' $!')


# eco end
# cpt start


async def get_btc():
    return round(float(float(Bitfinex().get_current_price())*float(open('btc_multi.txt','r').read())), 2)

async def check_btc(member:discord.Member):
    economic = await read_file('economic.txt')
    return float(economic.get(str(member.id)).get('btc'))

async def set_btc(btc_sum:float, member:discord.Member):
    economic = await read_file('economic.txt')
    for v, k in economic.items():
        if v == str(member.id):
            economic.get(str(member.id)).update({'btc': btc_sum})
            economic.update({str(member.id): economic.get(str(member.id))})
            open('economic.txt', 'w').close()
            await write_file('economic.txt', json.dumps(economic,indent=4))

async def give_btc(btc_sum:float, member:discord.Member):
    economic = await read_file('economic.txt')
    for v, k in economic.items():
        if v == str(member.id):
            economic.get(str(member.id)).update({'btc': await check_btc(member)+btc_sum})
            economic.update({str(member.id): economic.get(str(member.id))})
            open('economic.txt', 'w').close()
            await write_file('economic.txt', json.dumps(economic,indent=4))

async def take_btc(btc_sum:float, member:discord.Member):
    economic = await read_file('economic.txt')
    for v, k in economic.items():
        if v == str(member.id):
            economic.get(str(member.id)).update({'btc': await check_btc(member)-btc_sum})
            economic.update({str(member.id): economic.get(str(member.id))})
            open('economic.txt', 'w').close()
            await write_file('economic.txt', json.dumps(economic,indent=4))

@client.command()
async def btc(ctx):
    await ctx.channel.send('1 btc = ' + str(await get_btc()) + ' $')

@client.command()
async def btc_balance(ctx,member:discord.Member=None):
    if not member:
        member = ctx.author
    if member.bot:
        await ctx.channel.send('У ботом нет биткойнов')
        return None
    btc = await read_file('btc.txt')
    balance = round(await check_btc(member), 6)
    await ctx.channel.send('Биткойн баланс '+member.mention+' - '+str(balance)+' btc, стоимостью ' + str(balance * await get_btc()))

@client.command()
async def btc_money(ctx,member:discord.Member=None):
    if not member:
        member = ctx.author
    if member.bot:
        await ctx.channel.send('У ботом нет биткойнов')
        return None
    btc = await read_file('btc.txt')
    balance = round(await check_btc(member), 6)
    await ctx.channel.send('Биткойн баланс '+member.mention+' - '+str(balance)+' btc, стоимостью ' + str(balance * await get_btc()))

@client.command()
async def btc_buy(ctx, sum:int):
    if sum < 0:
        await ctx.channel.send('Вы не можете использовать отрицательные числа')
        return None
    balance = await check_money(ctx.author)
    if balance >= sum:
        await take_money(sum, ctx.author)
        btc_sum = float(sum / await get_btc())
        await give_btc(btc_sum, ctx.author)
        await ctx.channel.send(ctx.author.mention + ' купил ' + str(round(btc_sum, 6)) + ' btc, стоимостью ' + str(sum) + ' $')
    else:
        await ctx.channel.send('У вас недостаточно денег')

@client.command()
async def btc_sell(ctx, sum:int):
    btc = await read_file('btc.txt')
    balance = await check_money(ctx.author)
    if sum < 0:
        await ctx.channel.send('Вы не можете использовать отрицательные числа')
        return None
    if sum == 0:
        btc_sum = await check_btc(ctx.author)
        sum = round(btc_sum * await get_btc())
        await give_money(sum, ctx.author)
        await take_btc(btc_sum, ctx.author)
        await ctx.channel.send(ctx.author.mention + ' продал ' + str(round(btc_sum, 6)) + ' btc, стоимостью ' + str(sum) + ' $')
    if await check_btc(ctx.author) * await get_btc() >= sum:
        await give_money(sum, ctx.author)
        btc_sum = float(sum / await get_btc())
        await take_btc(btc_sum, ctx.author)
        await ctx.channel.send(ctx.author.mention + ' продал ' + str(round(btc_sum, 6)) + ' btc, стоимостью ' + str(sum) + ' $')
    else:
        await ctx.channel.send('У вас недостаточно биткойнов')

@client.command()
async def mine(ctx, member:discord.Member = None):
    if not member:
        member = ctx.author
    if member.bot:
        await ctx.channel.send('У ботом нет майнинг-ферм.')
        return None
    economic = await read_file('economic.txt')
    mine_level = economic.get(str(member.id)).get('mine')
    msg = await ctx.channel.send('Майнинг ферма ' + member.mention + ':\nУровень: ' + str(mine_level) + '   Прибыль за сообщение: ' + str(mine_level/10000) + ' btc\nСледующий уровень: ' + str(mine_level*500) + ' $   Прибыль за сообщение: ' + str((mine_level+1)/10000) + ' btc\nДля покупки, поставьте ⬆')
    await msg.add_reaction('⬆')
    mine_msgs[msg] = member.id

async def find_member(ctx, member:discord.Member):
    economic_file = open('economic.txt', 'w+')
    economic_file.seek(0)
    economic_file.close()
    economic_file = open('economic.txt', 'w')
    economic = json.loads(economic_file.read())



client.run(config.token)


#cpt end

#@commands.group(pass_context=True, no_pm=True)
#@checks.admin_or_permissions(manage_server=True)