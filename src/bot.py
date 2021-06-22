from discord.ext import commands


bot = commands.Bot(command_prefix='!')


@bot.command(name='ping', help='Check whether the bot is alive')
async def ping(ctx):
    await ctx.send("pong")


@bot.command(name='schedule', help='Schedule slots for a specific data, time, location and level')
async def schedule(ctx: commands.bot.Context, date: str, start_time: str, end_time: str, level: str, location: str):
    msg = '''
    **__{date}__**, {start_time} to {end_time} at {location}
    Level: {level}
    **Status:** Awaiting more players
    '''.format(date=date, start_time=start_time, end_time=end_time, level=level, location=location)

    await ctx.send(ctx.channel)
