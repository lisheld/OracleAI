import discord
from discord.ext import commands
from vars import discord_api_key
from functions import *
from helpers import *
import json
from collections import defaultdict

intents = discord.Intents.default()
intents.message_content = True
# Create a bot instance with a specified command prefix
bot = commands.Bot(command_prefix='/', intents=intents)

# Event listener for when the bot has switched from offline to online.
@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')

league_json = get_endpoint(f'{base_url}/sports', params = base_params)
league_names = []
league_keydict = {}
league_groups = defaultdict(list)
for item in league_json:
    if not item['has_outrights']:
        league_names.append(item['title'])
        league_keydict[item['title']] = item['key']
        league_groups[item['group']].append(item['title'])
print(league_names)
def initialize():

    starting_functions = [
        {
            "name":"init",
            "description": "Use this function to set the correct internal parameters based on the users request.",
            "parameters": {
                "type":"object",
                "properties": {
                    "league": {
                        "type":"string",
                        "description":"The league the user is requesting info on.",
                        "enum": league_names
                    } 
                },
                "required": ["league"]
            }
        }
        ]
    def function_parser(convo,full_message,funcToCall):
        func = full_message.message.function_call
        parsed_output = json.loads(func.arguments)
        name = func.name
        print(f'Calling function: {name}')
        try:
            if name == 'init':
                out = init(convo,parsed_output, funcToCall, league_keydict)
            elif name == 'get_events':
                out = get_events(convo,parsed_output)
            elif name == 'get_markets':
                out = get_markets(convo,parsed_output)
            elif name == 'get_scores':
                out = get_scores(convo,parsed_output)
            elif name == 'get_odds':
                out = get_odds(convo,parsed_output)
            elif name == 'get_best_odds':
                out = get_best_odds(convo,parsed_output)
            elif name == 'get_arb':
                out = get_arbitrages(convo,parsed_output)
            return out
        except Exception as e:
            return [str(e)]
    main = Conversation(
        """You are a sports betting advisor. Use the functions to answer the users questions. NEVER make assumptions about parameters to pass in. If the user's request is unclear, ask for clarification. ALWAYS call the init function first when responding to user input, but ONLY if they have specified a sports league.""", 
        functions=starting_functions, 
        callback=function_parser
        )
    
    return main
def call_function(func, args):
    joined = ' '.join(args)
    main = initialize()
    main.add_message("user", joined)
    out = main.complete(funcToCall = func)
    print(out)
    return '\n'.join(out) if isinstance(out, list) else out
@bot.command(name='events')
async def events(ctx, *args):
    await ctx.send(call_function('get_events', args))

@bot.command(name='odds')
async def odds(ctx, *args):
    await ctx.send(call_function('get_odds', args))

@bot.command(name='markets')
async def markets(ctx, *args):
    await ctx.send(call_function('get_markets', args))

@bot.command(name='best')
async def best(ctx, *args):
    await ctx.send(call_function('get_best_odds', args))

@bot.command(name='scores')
async def scores(ctx, *args):
    await ctx.send(call_function('get_scores', args))

@bot.command(name='arb')
async def arb(ctx, *args):
    await ctx.send(call_function('get_arb', args))

@bot.command(name='leagues')
async def leagues(ctx):
    out = [f"## Available Leagues: "]
    for group in league_groups:
        out.append(f"### {group}")
        out.extend([f"* {league}" for league in league_groups[group]])
    await ctx.send('\n'.join(out))
    
@bot.command(name='info')
async def help(ctx):
    await ctx.send("## OracleAI: A sports betting analyst\n### General Info:\nOracleAI does not have any specific syntax requirements, the information just needs to be in the message. Command requests are limited to 30 characters, so be as concise as possible.\n### Commands:\nCommand format: /<command> <arguments>\n* /leagues: Gets a list of all available leagues\n* /events {league}: Gets a list of all events for a given league\n* /odds {league, teams, market}: gets the live odds for a specific market for a specific match\n* /markets {league}: gets the available markets for a specific league\n* /best {league, teams, market}: gets the best odds for a specific market for a specific match\n* /scores {league, teams}: get the live scores for a given match from up to 3 days ago\n* /arb {league}: looks for available arbitrage opportunities in a given league")

bot.run(discord_api_key)