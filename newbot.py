import discord
from discord import app_commands
from discord.ext import commands
from vars import discord_api_key
from newfuncs import * 
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix=commands.when_mentioned, intents=intents)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')

    activity = discord.Activity(type=discord.ActivityType.listening, name="/info")
    await bot.change_presence(activity=activity)
    print(f'Set listening status to "/info"')
    
    try:
        synced = await bot.tree.sync()
        print(f'Synced {len(synced)} commands')
    except Exception as e:
        print(f'Failed to sync commands: {e}')
    

def is_premium():
    async def predicate(interaction: discord.Interaction):
        premium_role = discord.utils.get(interaction.guild.roles, name="Premium")
        if premium_role in interaction.user.roles:
            return True
        await interaction.response.send_message("You don't have the role to use this command.", ephemeral=True)
        return False
    return app_commands.check(predicate)

def is_lite():
    async def predicate(interaction: discord.Interaction):
        premium_role = discord.utils.get(interaction.guild.roles, name="Premium")
        lite_role = discord.utils.get(interaction.guild.roles, name="Oracle Light")
        if premium_role in interaction.user.roles or lite_role in interaction.user.roles:
            return True
        await interaction.response.send_message("You don't have the role to use this command.", ephemeral=True)
        return False
    return app_commands.check(predicate)


def at_is_premium():
    async def predicate(ctx):
        premium_role = discord.utils.get(ctx.guild.roles, name="Premium")
        if premium_role in ctx.author.roles:
            return True
        await ctx.send("You don't have the role to use this command.")
        return False
    
    return commands.check(predicate)

def at_is_lite():
    async def predicate(ctx):
        lite_role = discord.utils.get(ctx.guild.roles, name="Oracle Light")
        premium_role = discord.utils.get(ctx.guild.roles, name="Premium")
        if premium_role in ctx.author.roles or lite_role in ctx.author.roles:
            return True
        await ctx.send("You don't have the role to use this command.")
        return False
    
    return commands.check(predicate)


@bot.tree.command(name='events', description="Gets a list of all events for a given league")
@app_commands.describe(args="league")
async def events(interaction: discord.Interaction, args: str):
    print(f'{interaction.user.name} called a command.')
    await interaction.response.send_message(call_command('events', args), ephemeral=True)

@bot.tree.command(name='odds', description="Gets the live odds for a specific market for a specific match")
@app_commands.describe(args="league, teams, market")
async def odds(interaction: discord.Interaction, args: str):
    print(f'{interaction.user.name} called a command.')
    await interaction.response.send_message(call_command('odds', args), ephemeral=True)

@bot.tree.command(name='markets', description="Gets the available markets for a given league")
@app_commands.describe(args="league")
async def markets(interaction: discord.Interaction, args: str):
    print(f'{interaction.user.name} called a command.')
    await interaction.response.send_message(call_command('markets', args), ephemeral=True)

@bot.tree.command(name='best',description="Gets the best odds for a specific market for a specific match")
@app_commands.describe(args="league, teams, market")
@is_lite()
async def best(interaction: discord.Interaction, args: str):
    print(f'{interaction.user.name} called a command.')
    await interaction.response.send_message(call_command('best', args), ephemeral=True)

@bot.tree.command(name='scores',description="Get the live scores for a given match from up to 3 days ago")
@app_commands.describe(args="league, teams")
@is_lite()
async def scores(interaction: discord.Interaction, args: str):
    print(f'{interaction.user.name} called a command.')
    await interaction.response.send_message(call_command('scores', args), ephemeral=True)

@bot.tree.command(name='arb', description="Looks for available arbitrage opportunities in a given sport")
@app_commands.describe(args="sport")
@is_premium()
async def arb(interaction: discord.Interaction, args: str):
    print(f'{interaction.user.name} called a command.')
    await interaction.response.send_message(call_command('arb', args), ephemeral=True)

@bot.tree.command(name='leagues', description="Gets a list of all available leagues.")
async def leagues(interaction: discord.Interaction):
    print(f'{interaction.user.name} called a command.')
    await interaction.response.send_message(call_command('leagues', []), ephemeral=True)

@bot.tree.command(name='predict',description="Makes a prediction on a given match")
@app_commands.describe(args="league, teams, market")
@is_lite()
async def predict(interaction: discord.Interaction, args: str):
    print(f'{interaction.user.name} called a command.')
    await interaction.response.send_message(call_command('predict', args), ephemeral=True)


@bot.tree.command(name='advice', description="Suggests a bet for a given market in a given league")
@app_commands.describe(args="league, market")
@is_lite()
async def advice(interaction: discord.Interaction, args: str):
    print(f'{interaction.user.name} called a command.')
    await interaction.response.send_message(call_command('advice', args), ephemeral=True)

@bot.tree.command(name='info', description="Gets info about OracleGPT.")
async def info(interaction: discord.Interaction):
    print(f'{interaction.user.name} called info.')
    await interaction.response.send_message("## OracleGPT: A sports betting analyst\n### General Info:\nOracleGPT does not have any specific syntax requirements, the information just needs to be in the message.\n**Command format: /<command> <arguments>**\n### Free commands:\n* /leagues: Gets a list of all available leagues\n* /events {league}: Gets a list of all events for a given league\n* /odds {league, teams, market}: gets the live odds for a specific market for a specific match\n* /markets {league}: gets the available markets for a specific league\n### Light commands:\n* /best {league, teams, market}: gets the best odds for a specific market for a specific match\n* /scores {league, teams}: get the live scores for a given match from up to 3 days ago\n* /predict {league, teams}: predicts the outcome of a given match\n* /advice {league, market}: suggests a bet for a given market in a given league\n### Premium Commands:\n* /arb {sport}: looks for available arbitrage opportunities in a given sport\n### Error Handling:\nIf you are having trouble getting OracleGPT to interpret your request, use standard english instead. For example, '/best spain france euros h2h' could be rewritten as '/best What are the best h2h odds for the spain vs france uefa euro game?'. If you continue to receive errors, please contact an administrator.", ephemeral=True)

@bot.command(name='events')
@at_is_lite()
async def at_events(ctx, *args):
    print(f'{ctx.author.name} called a command.')
    await ctx.send(call_command('events', args))

@bot.command(name='odds')
@at_is_lite()
async def at_odds(ctx, *args):
    print(f'{ctx.author.name} called a command.')
    await ctx.send(call_command('odds', args))
    
@bot.command(name='markets')
@at_is_lite()
async def at_markets(ctx, *args):
    print(f'{ctx.author.name} called a command.')
    await ctx.send(call_command('markets', args))

@bot.command(name='best')
@at_is_lite()
async def at_best(ctx, *args):
    print(f'{ctx.author.name} called a command.')
    await ctx.send(call_command('best', args))

@bot.command(name='scores')
@at_is_lite()
async def at_scores(ctx, *args):
    print(f'{ctx.author.name} called a command.')
    await ctx.send(call_command('scores', args))

@bot.command(name='arb')
@at_is_premium()
async def at_arb(ctx, *args):
    print(f'{ctx.author.name} called a command.')
    await ctx.send(call_command('arb', args))

@bot.command(name='leagues')
@at_is_lite()
async def at_leagues(ctx):
    print(f'{ctx.author.name} called a command.')
    await ctx.send(call_command('leagues', []))

@bot.command(name='predict')
@at_is_lite()
async def at_predict(ctx, *args):
    print(f'{ctx.author.name} called a command.')
    await ctx.send(call_command('predict', args))

@bot.command(name='advice')
@at_is_lite()
async def at_advice(ctx, *args):
    print(f'{ctx.author.name} called a command.')
    await ctx.send(call_command('advice', args))

@bot.command(name='info')
@at_is_lite()
async def at_info(ctx):
    print(f'{ctx.author.name} called info.')
    await ctx.send("## OracleGPT: A sports betting analyst\n### General Info:\nOracleGPT does not have any specific syntax requirements, the information just needs to be in the message.\n**Command format: /<command> <arguments>**\n### Free commands:\n* /leagues: Gets a list of all available leagues\n* /events {league}: Gets a list of all events for a given league\n* /odds {league, teams, market}: gets the live odds for a specific market for a specific match\n* /markets {league}: gets the available markets for a specific league\n### Light commands:\n* /best {league, teams, market}: gets the best odds for a specific market for a specific match\n* /scores {league, teams}: get the live scores for a given match from up to 3 days ago\n* /predict {league, teams}: predicts the outcome of a given match\n* /advice {league, market}: suggests a bet for a given market in a given league\n### Premium Commands:\n* /arb {sport}: looks for available arbitrage opportunities in a given sport\n### Error Handling:\nIf you are having trouble getting OracleGPT to interpret your request, use standard english instead. For example, '/best spain france euros h2h' could be rewritten as '/best What are the best h2h odds for the spain vs france uefa euro game?'. If you continue to receive errors, please contact an administrator.")

if __name__ == '__main__':
    bot.run(discord_api_key)