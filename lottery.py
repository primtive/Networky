import discord, config, asyncio
from admin_commands import mute
from utils import get_role_by_id
from discord_slash import SlashContext, ComponentContext
from discord_slash.utils import manage_components
from discord_slash.model import ButtonStyle
import economic
import random

lotteries = {}


async def send_for_three_seconds(ctx: SlashContext, text: str):
    msg = await ctx.reply(text)
    await asyncio.sleep(3)
    await msg.delete()


class Lottery:
    def __init__(self,
                 client: discord.Client,
                 name: str,
                 money: int,
                 ctx: SlashContext):

        self.client = client
        self.name = name
        self.money = money
        self.ctx = ctx
        self.takes_part = []
        self.spam_count = {}
        self.components = [manage_components.create_button(label='Учавствовать!', style=ButtonStyle.green)]
        self.action_rows = manage_components.create_actionrow(*self.components)

    async def send_lottery(self):
        embed = discord.Embed(title=self.ctx.author.display_name + ' объявляет лотерею на ' + str(self.money) + ' $!',
                              description='Чтобы учавствовать нажмите кнопку ниже.',
                              color=config.embed_color)

        self.message = await self.ctx.reply(embed=embed, components=[self.action_rows])
        lotteries[self.name] = self

    async def take_part(self, ctx: ComponentContext):

        if ctx.author in self.takes_part:
            muted_role = await get_role_by_id(ctx, config.muted_role)
            if not muted_role in ctx.author.roles:
                msg = await ctx.reply(ctx.author.display_name + ', вы уже учавствуете')
                self.spam_count[ctx.author] = self.spam_count[ctx.author] + 1
                if self.spam_count[ctx.author] >= 5:
                    await mute(ctx=ctx, member=ctx.author, muter=self.client.user, minutes=1)
                await asyncio.sleep(3)
                await msg.delete()
        else:
            self.takes_part.append(ctx.author)
            self.spam_count[ctx.author] = 1
            msg = await ctx.reply(ctx.author.display_name + ' теперь учавствует')
            await asyncio.sleep(3)
            await msg.delete()

    async def complete_lottery(self, ctx: SlashContext):

        winner = random.choice(self.takes_part)

        embed = discord.Embed(title='Результаты лотереи на ' + str(self.money) + ' $',
                              description='Побeдитель - ' + winner.display_name + '!',
                              color=config.embed_color)

        economic.give_money(winner, self.money)

        await self.message.delete()
        await ctx.reply(embed=embed)

    async def cancel_lottery(self, ctx: SlashContext):
        await self.message.delete()
        await send_for_three_seconds(ctx, 'Лотерея отменена.')
        lotteries.pop(self.name)
