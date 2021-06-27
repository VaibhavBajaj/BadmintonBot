import traceback
from typing import Union

import discord
from discord.ext import commands
from helpers.scheduler import Scheduler


# GeneralCog holds all the general commands that the bot handles
class GeneralCog(commands.Cog, name='General'):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.scheduler = Scheduler()

    @staticmethod
    def __parse_slot_reaction(emoji: str):
        slot_emoji = {
            "1️⃣": 1,
            "2️⃣": 2,
            "3️⃣": 3,
            "4️⃣": 4,
            "5️⃣": 5,
            "6️⃣": 6,
            "7️⃣": 7,
            "8️⃣": 8,
            "9️⃣": 9,
            "🔟": 10
        }

        if emoji in slot_emoji:
            return slot_emoji[emoji]
        return None

    async def __book_court(self, reaction: discord.Reaction, user: Union[discord.Member, discord.User]):
        def check(response: discord.Message):
            return response.content.isnumeric()

        await user.send("What slot number did you book?")
        slot_message = await self.bot.wait_for(event='message', check=check)
        await user.send("What court number did you book?")
        court_message = await self.bot.wait_for(event='message', check=check)
        content = self.scheduler.book_slot(reaction.message.content, slot_message.content, court_message.content, user)
        await reaction.message.edit(content=content)

    async def __add_slot_mention(self, reaction: discord.Reaction, user: Union[discord.Member, discord.User], slot_idx: int):
        content = self.scheduler.add_schedule_mention(reaction.message.content, slot_idx, user)
        await reaction.message.edit(content=content)

    @commands.command(help='Check whether bot is alive')
    async def ping(self, ctx: commands.Context):
        await ctx.send("pong")

    @commands.command(help='''
    Schedule a session provided the date, time, level and location.
    React on the scheduled session with a slot number (e.g. :one:, :two:) to join that slot.
    React with the :bookmark: emoji to update the schedule with the booked slot court number.
    ''')
    async def schedule(self, ctx: commands.Context, date: str, start_time: str, end_time: str, location: str):
        try:
            content = self.scheduler.create_schedule(date, start_time, end_time, location)
            schedule_channel_name = str(ctx.channel).split('-')[0] + '-schedule'
            schedule_channel = discord.utils.get(ctx.guild.channels, name=schedule_channel_name)
            await schedule_channel.send(content)
        except Exception as e:
            await ctx.message.author.send(content=str(e))
            print(traceback.format_exc())

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction: discord.Reaction, user: Union[discord.Member, discord.User]):
        try:
            if reaction.emoji == '🔖':
                await self.__book_court(reaction, user)
            else:
                slot_idx = self.__parse_slot_reaction(reaction.emoji)
                if slot_idx is not None:
                    await self.__add_slot_mention(reaction, user, slot_idx)
        except Exception as e:
            await user.send(content=str(e))
            print(traceback.format_exc())

    @commands.Cog.listener()
    async def on_reaction_remove(self, reaction: discord.Reaction, user: Union[discord.Member, discord.User]):
        slot_idx = self.__parse_slot_reaction(reaction.emoji)
        if slot_idx is None:
            return
        try:
            content = self.scheduler.remove_schedule_mention(reaction.message.content, slot_idx, user)
            await reaction.message.edit(content=content)
        except Exception as e:
            await user.send(content=str(e))
            print(traceback.format_exc())


# setup for adding cog to the bot
def setup(bot: commands.Bot):
    cog = GeneralCog(bot)
    bot.add_cog(cog)
