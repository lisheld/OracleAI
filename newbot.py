import discord
from discord import app_commands
from discord.ext import commands
from vars import discord_api_key
from newfuncs import * 
catch_errors = False
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix=commands.when_mentioned_or('/'), intents=intents)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')
    try:
        synced = await bot.tree.sync()
        print(f'Synced {len(synced)} commands')
    except Exception as e:
        print(f'Failed to sync commands: {e}')
    

async def is_premium(ctx):
    return "Premium" in ctx.author.roles

def call_command(command, args):
    inp = ' '.join(args) if isinstance(args,(tuple,list)) else args
    if catch_errors:
        try:
            print(func_dict)
            func_out = func_dict[command](inp)
        except Exception as e:
            func_out = [f"### Error: {e}"]
    else:
        func_out = func_dict[command](inp)
    return '\n'.join(func_out)


@bot.tree.command(name='events')
async def events(ctx, *args):
    await ctx.send(call_command('events', args))

@bot.tree.command(name='odds')
async def odds(ctx, *args):
    await ctx.send(call_command('odds', args))
    
@bot.tree.command(name='markets')
async def markets(ctx, *args):
    await ctx.send(call_command('markets', args))

@bot.tree.command(name='best')
@commands.check(is_premium)
async def best(ctx, *args):
    await ctx.send(call_command('best', args))

@bot.tree.command(name='scores')
@commands.check(is_premium)
async def scores(ctx, *args):
    await ctx.send(call_command('scores', args))

@bot.tree.command(name='arb')
@commands.check(is_premium)
async def arb(ctx, *args):
    await ctx.send(call_command('arb', args))

@bot.tree.command(name='leagues')
async def leagues(ctx):
    await ctx.send(call_command('leagues', []))

@bot.tree.command(name='predict')
@commands.check(is_premium)
async def predict(ctx, *args):
    await ctx.send(call_command('predict', args))

@bot.tree.command(name='advice')
@commands.check(is_premium)
async def advice(ctx, *args):
    await ctx.send(call_command('advice', args))


@bot.tree.command(name='info')
async def help(ctx):
    await ctx.send("## OracleAI: A sports betting analyst\n### General Info:\nOracleAI does not have any specific syntax requirements, the information just needs to be in the message.\n**Command format: /<command> <arguments>**\n###Free commands:\n* /leagues: Gets a list of all available leagues\n* /events {league}: Gets a list of all events for a given league\n* /odds {league, teams, market}: gets the live odds for a specific market for a specific match\n* /markets {league}: gets the available markets for a specific league\n###Premium commands:\n* /best {league, teams, market}: gets the best odds for a specific market for a specific match\n* /scores {league, teams}: get the live scores for a given match from up to 3 days ago\n* /arb {league}: looks for available arbitrage opportunities in a given league\n* /predict {league, teams}: predicts the outcome of a given match\n* /advice {league, market}: suggests a bet for a given market in a given league\n### Error Handling:\nIf you are having trouble getting OracleAI to interpret your request, use standard english instead. For example, '/best spain france euros h2h' could be rewritten as '/best What are the best h2h odds for the spain vs france uefa euro game?'. If you continue to receive errors, please contact an administrator.")

if __name__ == '__main__':
    bot.run(discord_api_key)