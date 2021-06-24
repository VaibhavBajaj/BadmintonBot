import discord
from discord.ext import commands

SCHEDULE_MESSAGE = '''
    **__{date}__**, {start_time} to {end_time} at {location}
    Level: {level}
    Slot {slot_idx}: {attendees}
    **Status:** Awaiting more players
    '''


# GeneralCog holds all the general commands that the bot handles
class GeneralCog(commands.Cog, name='General'):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(help='Check whether bot is alive')
    async def ping(self, ctx: commands.bot.Context):
        await ctx.send("pong")

    @commands.command(help='Schedule a slot provided the date, time, level and location')
    async def schedule(self, ctx: commands.bot.Context, date: str, start_time: str, end_time: str, level: str, location: str):
        # TODO: Update slot_idx using a python dict of key (date, location) and value slot_idx
        slot_idx = 1
        msg = SCHEDULE_MESSAGE.format(date=date, start_time=start_time, end_time=end_time, level=level,
                                      location=location, slot_idx=slot_idx, attendees="")

        schedule_name = str(ctx.channel).split('-')[0] + '-schedule'
        schedule_channel = discord.utils.get(ctx.guild.channels, name=schedule_name)

        await schedule_channel.send(msg)

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction: discord.Reaction, user: discord.User):
        # TODO: Add user display name to attendees list in slot (later this must be done by level)
        print("Someone reacted to a message")
        print(reaction)
        print(user.display_name)

    @commands.Cog.listener()
    async def on_reaction_remove(self, reaction: discord.Reaction, user: discord.User):
        # TODO: Remove user display name from attendees list in slot
        pass


# setup for adding cog to the bot
def setup(bot: commands.Bot):
    cog = GeneralCog(bot)
    bot.add_cog(cog)
