import asyncio
import discord
import config


async def mute(ctx, member: discord.Member, muter: discord.Member, minutes: int = None):
    await member.add_roles(ctx.guild.get_role(config.muted_role))
    if minutes:
        embed = discord.Embed(title=member.display_name + ' был замучен!',
                              description='Администратор ' + muter.display_name + ' замутил ' + member.display_name + ' на ' + str(minutes) + ' минут.',
                              color=config.embed_color)
        await ctx.reply(embed=embed)
        await asyncio.sleep(minutes*60)
        await member.remove_roles(ctx.guild.get_role(config.muted_role))
    else:
        embed = discord.Embed(title=member.display_name + ' был замучен!',
                              description='Администратор ' + muter.display_name + ' замутил ' + member.display_name + '.',
                              color=config.embed_color)
        await ctx.reply(embed=embed)


async def unmute(ctx, member: discord.Member, unmuter: discord.Member):
    await member.remove_roles(ctx.guild.get_role(config.muted_role))
    embed = discord.Embed(title=member.display_name + ' был размучен!',
                          description='Администратор ' + unmuter.display_name + ' размутил ' + member.display_name + '.',
                          color=config.embed_color)
    await ctx.reply(embed=embed)
