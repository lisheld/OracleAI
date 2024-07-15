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
    

def is_premium():
    async def predicate(interaction: discord.Interaction):
        premium_role = discord.utils.get(interaction.guild.roles, name="premium")
        if premium_role in interaction.user.roles:
            return True
        await interaction.response.send_message("You don't have the premium role to use this command.", ephemeral=True)
        return False
    return app_commands.check(predicate)

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


@bot.tree.command(name='events', description="Gets a list of all events for a given league")
@app_commands.describe(args="league")
async def events(interaction: discord.Interaction, args: str):
    await interaction.response.send_message(call_command('events', args), ephemeral=True)

@bot.tree.command(name='odds', description="Gets the live odds for a specific market for a specific match")
@app_commands.describe(args="league, teams, market")
async def odds(interaction: discord.Interaction, args: str):
    await interaction.response.send_message(call_command('odds', args), ephemeral=True)
    
@bot.tree.command(name='markets', description="Gets the available markets for a given league")
@app_commands.describe(args="league")
async def markets(interaction: discord.Interaction, args: str):
    await interaction.response.send_message(call_command('markets', args), ephemeral=True)

@bot.tree.command(name='best',description="Gets the best odds for a specific market for a specific match")
@app_commands.describe(args="league, teams, market")
@is_premium()
async def best(interaction: discord.Interaction, args: str):
    await interaction.response.send_message(call_command('best', args), ephemeral=True)

@bot.tree.command(name='scores',description="Get the live scores for a given match from up to 3 days ago")
@app_commands.describe(args="league, teams")
@is_premium()
async def scores(interaction: discord.Interaction, args: str):
    await interaction.response.send_message(call_command('scores', args), ephemeral=True)

@bot.tree.command(name='arb', description="Looks for available arbitrage opportunities in a given league")
@app_commands.describe(args="league")
@is_premium()
async def arb(interaction: discord.Interaction, args: str):
    await interaction.response.send_message(call_command('arb', args), ephemeral=True)

@bot.tree.command(name='leagues', description="Gets a list of all available leagues.")
async def leagues(interaction: discord.Interaction):
    await interaction.response.send_message(call_command('leagues', []), ephemeral=True)

@bot.tree.command(name='predict',description="Makes a prediction on a given match")
@app_commands.describe(args="league, teams, market")
@is_premium()
async def predict(interaction: discord.Interaction, args: str):
    await interaction.response.send_message(call_command('predict', args), ephemeral=True)

@bot.tree.command(name='advice', description="Suggests a bet for a given market in a given league")
@app_commands.describe(args="league, market")
@is_premium()
async def advice(interaction: discord.Interaction, args: str):
    await interaction.response.send_message(call_command('advice', args), ephemeral=True)

@bot.tree.command(name='info', description="Gets info about OracleAI.")
async def leagues(interaction: discord.Interaction):
    await interaction.response.send_message("## OracleAI: A sports betting analyst\n### General Info:\nOracleAI does not have any specific syntax requirements, the information just needs to be in the message.\n**Command format: /<command> <arguments>**\n### Free commands:\n* /leagues: Gets a list of all available leagues\n* /events {league}: Gets a list of all events for a given league\n* /odds {league, teams, market}: gets the live odds for a specific market for a specific match\n* /markets {league}: gets the available markets for a specific league\n### Premium commands:\n* /best {league, teams, market}: gets the best odds for a specific market for a specific match\n* /scores {league, teams}: get the live scores for a given match from up to 3 days ago\n* /arb {league}: looks for available arbitrage opportunities in a given league\n* /predict {league, teams}: predicts the outcome of a given match\n* /advice {league, market}: suggests a bet for a given market in a given league\n### Error Handling:\nIf you are having trouble getting OracleAI to interpret your request, use standard english instead. For example, '/best spain france euros h2h' could be rewritten as '/best What are the best h2h odds for the spain vs france uefa euro game?'. If you continue to receive errors, please contact an administrator.", ephemeral=True)

if __name__ == '__main__':
    bot.run(discord_api_key)