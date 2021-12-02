import asyncio
import discord
import config


async def mute(ctx, member: discord.Member, muter: discord.Member, time: str = None):
    
    if time:
    
        t_minutes = 0
        time_str = ''
    
        try:
            for part in time.split():
                num = int(part[:-1])
                time_name = part[-1:]
                if time_name == 'y':
                    t_minutes += 525600 * num
                    time_str = time_str + f'{num} лет '
                if time_name == 'M':
                    t_minutes += 43200 * num
                    time_str = time_str + f'{num} месяцев '
                if time_name == 'w':
                    t_minutes += 10080 * num
                    time_str = time_str + f'{num} недель '
                if time_name == 'd':
                    t_minutes += 1440 * num
                    time_str = time_str + f'{num} дней '
                if time_name == 'h':
                    t_minutes += 60 * num
                    time_str = time_str + f'{num} часов '
                if time_name == 'm':
                    t_minutes += num
                    time_str = time_str + f'{num} минут '
                

            await member.add_roles(ctx.guild.get_role(config.muted_role))
            embed = discord.Embed(title=member.display_name + ' был замучен!',
                                  description='Администратор ' + muter.display_name + ' замутил ' + member.display_name + ' на ' + time_str,
                                  color=config.embed_color)
            await ctx.reply(embed=embed)
            await asyncio.sleep(t_minutes * 60)
            await member.remove_roles(ctx.guild.get_role(config.muted_role))
            await ctx.send(member.mention + ' был размучен')
    
        except:
            await ctx.reply('Ошибка определения времени мута')
            return None

    else:
        await member.add_roles(ctx.guild.get_role(config.muted_role))
        embed = discord.Embed(title=member.display_name + ' был замучен!',
                              description='Администратор ' + muter.display_name + ' замутил ' + member.display_name,
                              color=config.embed_color)
        await ctx.reply(embed=embed)


async def unmute(ctx, member: discord.Member, unmuter: discord.Member):
    await member.remove_roles(ctx.guild.get_role(config.muted_role))
    embed = discord.Embed(title=member.display_name + ' был размучен!',
                          description='Администратор ' + unmuter.display_name + ' размутил ' + member.display_name + '.',
                          color=config.embed_color)
    await ctx.reply(embed=embed)
