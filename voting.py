import discord, config, asyncio
from admin_commands import mute
from utils import get_role_by_id
from discord_slash import SlashContext, ComponentContext
from discord_slash.utils import manage_components
from discord_slash.model import ButtonStyle

votings = {}


async def send_for_three_seconds(ctx: SlashContext, text: str):
    msg = await ctx.reply(text)
    await asyncio.sleep(3)
    await msg.delete()


class Voting:
    def __init__(self,
                 client: discord.Client,
                 name: str,
                 description: str,
                 ctx: SlashContext,
                 buttons: list = None):

        self.client = client
        self.name = name
        self.description = description
        self.ctx = ctx
        self.votes = {}
        self.spam_count = {}

        actions = []
        if buttons:
            for button in buttons:
                actions.append(manage_components.create_button(label=button, style=ButtonStyle.gray))
        else:
            buttons = ['👍', '👎']
            actions = [manage_components.create_button(label='👍', style=ButtonStyle.gray),
                       manage_components.create_button(label='👎', style=ButtonStyle.gray)]

        for button in buttons:
            self.votes[button] = []
        self.action_rows = manage_components.create_actionrow(*actions)
        self.buttons = buttons
        self.components = actions

    async def send_voting(self):
        self.embed = discord.Embed(title=self.ctx.author.display_name + ' объявляет голосование!',
                                   description=self.description,
                                   color=config.embed_color)

        self.message = await self.ctx.reply(embed=self.embed, components=[self.action_rows])
        votings[self.name] = self

    async def vote(self, ctx: ComponentContext):
        vote_members = []
        for members_list in self.votes.values():
            for member in members_list:
                vote_members.append(member)

        if ctx.author in vote_members:
            muted_role = await get_role_by_id(ctx, config.muted_role)
            if not muted_role in ctx.author.roles:
                msg = await ctx.reply(ctx.author.display_name + ', вы уже проголосовали')
                self.spam_count[ctx.author] = self.spam_count[ctx.author] + 1
                if self.spam_count[ctx.author] >= 5:
                    await mute(ctx=ctx, member=ctx.author, muter=self.client.user, minutes=1)
                await asyncio.sleep(3)
                await msg.delete()
        else:
            self.votes[ctx.component.get('label')].append(ctx.author)
            self.spam_count[ctx.author] = 1
            msg = await ctx.reply(ctx.author.display_name + ' проголосовал')
            await asyncio.sleep(3)
            await msg.delete()

    async def complete_voting(self, ctx: SlashContext):

        embed = discord.Embed(title='Результаты голосования: ' + self.description,
                              color=config.embed_color)

        for (button, members) in self.votes.items():

            description = ''
            if len(members) > 0:
                for member in members:
                    description = description + member.display_name + '\n'
            else:
                description = 'Нет проголосовавших'

            embed.add_field(name='```' + button + ' (' + str(len(self.votes[button])) + ')```',
                            value=description,
                            inline=True)

        await self.message.delete()
        await ctx.reply(embed=embed)

    async def cancel_voting(self, ctx: SlashContext):
        await self.message.delete()
        await send_for_three_seconds(ctx, 'Голосование отменено.')
        votings.pop(self.name)
