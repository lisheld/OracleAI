import discord
from discord.ext import commands
from vars import discord_api_key
from newfuncs import *

intents = discord.Intents.default()
intents.message_content = True
# Create a bot instance with a specified command prefix
bot = commands.Bot(command_prefix='/', intents=intents)

# Event listener for when the bot has switched from offline to online.
@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')

def call_command(command, args):
    inp = ' '.join(args)
    func_dict = {
        'events': get_events,
        'odds': get_odds,
        'markets': get_markets,
        'best': get_best_odds,
        'scores': get_scores,
        'arb': get_arbitrages,
        'leagues': get_leagues
    }
    try:
        func_out = func_dict[command](inp)
        
    except Exception as e:
        func_out = [f"### Error: {e}"]
    return '\n'.join(func_out)


@bot.command(name='events')
async def events(ctx, *args):
    await ctx.send(call_command('events', args))

@bot.command(name='odds')
async def odds(ctx, *args):
    await ctx.send(call_command('odds', args))
    
@bot.command(name='markets')
async def markets(ctx, *args):
    await ctx.send(call_command('markets', args))

@bot.command(name='best')
async def best(ctx, *args):
    await ctx.send(call_command('best', args))

@bot.command(name='scores')
async def scores(ctx, *args):
    await ctx.send(call_command('scores', args))

@bot.command(name='arb')
async def arb(ctx, *args):
    await ctx.send(call_command('arb', args))

@bot.command(name='leagues')
async def leagues(ctx):
    await ctx.send(call_command('leagues', []))
    
@bot.command(name='info')
async def help(ctx):
    await ctx.send("## OracleAI: A sports betting analyst\n### General Info:\nOracleAI does not have any specific syntax requirements, the information just needs to be in the message. Command requests are limited to 30 characters, so be as concise as possible.\n### Commands:\nCommand format: /<command> <arguments>\n* /leagues: Gets a list of all available leagues\n* /events {league}: Gets a list of all events for a given league\n* /odds {league, teams, market}: gets the live odds for a specific market for a specific match\n* /markets {league}: gets the available markets for a specific league\n* /best {league, teams, market}: gets the best odds for a specific market for a specific match\n* /scores {league, teams}: get the live scores for a given match from up to 3 days ago\n* /arb {league}: looks for available arbitrage opportunities in a given league")

bot.run(discord_api_key)