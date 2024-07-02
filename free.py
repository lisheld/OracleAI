from openai import OpenAI
from dotenv import load_dotenv
from helpers import *
import os
import json
from collections import defaultdict
import json

## Load environment variables ##
load_dotenv()
odds_api_key = os.getenv('odds')
client = OpenAI(api_key=os.getenv('openai'))
GPT_MODEL = "gpt-3.5-turbo"

## Set base params for oddsapi ##
base_url = 'https://api.the-odds-api.com/v4'
base_params = {'apiKey': odds_api_key}    

### Get list of valid leagues ###
league_json = get_endpoint(f'{base_url}/sports', params = base_params)
league_keys = [item['key'] for item in league_json]


    

def events(league_key=None):
    """Function to get events for a specific league."""
    if league_key is None:
        raise ValueError("I couldn't find that league or no league were specified.")
    events_json = get_endpoint(f"{base_url}/sports/{league_key}/events",base_params)
    return [f"{event['home_team']} vs {event['away_team']}" for event in events_json]

def scores(teams=None,league_key=None):
    """Function to get scores for a specific league."""
    if league_key is None:
        raise ValueError("I couldn't find that league or no league were specified.")
    if teams is None:
        raise ValueError("I couldn't find those teams or no teams were specified.")
    scores_json = get_endpoint(f"{base_url}/sports/{league_key}/scores", base_params|{"daysFrom":3})
    home,away = teams.split(',')
    for event in scores_json[::-1]:
        if event['home_team'] == home and event['away_team'] == away:
            scores = event['scores']
            return [f"{team['name']}: {team['score']}" for team in scores]



def markets(league_key=None): 
    if league_key is None:
            raise ValueError("I couldn't find that league or no league were specified.")
    if 'winner' in league_key:
        return ['outrights']
    return ['head-to-head','spreads','totals']+(player_props[league_key] if league_key in player_props else [])

def odds(teams=None,league_key=None,market=None):    
    if league_key is None:
        raise ValueError("I couldn't find that league or no league were specified.")
    if teams is None:
        raise ValueError("I couldn't find those teams or no teams were specified.")
    if market is None:
        raise ValueError("I couldn't find that market or no market was specified.")

def function_parser(convo,full_message):
    func = full_message.message.function_call
    try:
        parsed_output = json.loads(func.arguments)
        name = func.name
        if name == 'set_league':
            convo['league'] = parsed_output['league']
            events_json = get_endpoint(f"{base_url}/sports/{convo['league']}/events",base_params)
            convo['event_dict'] = {f'{event["home_team"]},{event["away_team"]}': event['id'] for event in events_json} if convo['league'] != "upcoming" else {f'{event["home_team"]},{event["away_team"]}': (event['id'],event['key']) for event in events_json}
            out = "League has been set."
        elif name == 'get_events':
            odds_function = 
            all_odds_function = {
                "name":"get_all_odds",
                "description": "Use this function to get all odds for the league the user is requesting info on.",
                "parameters": {
                    "type":"object",
                    "properties": {
                        "league": {
                            "type":"string",
                            "description":"The league the user is requesting info on",
                            "enum": league_keys
                        },
                        "market": {
                            "type":"string",
                            "description":"The type of odds to get. If unsure, use 'h2h'.",
                            "enum":markets(convo['league'])
                        }
                    },
                    "required":["market"]
                }
            }
            convo.add_func(odds_function)
            convo.add_func(all_odds_function)
            out = []
    except:
        ...
starting_functions = [
    {
        "name":"get_league",
        "description": "Use this function to internally set the league the user is requesting information on.",
        "parameters": {
            "type":"object",
            "properties": {
                "league": {
                    "type":"string",
                    "description":"The league the user is requesting info on",
                    "enum": league_keys+['upcoming']
                },
                
            }
        }
    },
    {
        "name":"get_events",
        "description": "Use this function to get the events for the league the user is requesting info on."
    },
    {
        "name":"get_odds",
        "description": "Use this function to get the specific live odds for the event the user wants advice on.",
        "parameters": {
            "type":"object",
            "properties": {
                "teams": {
                    "type":"string",
                    "description":"The teams involved in the event",
                    "enum": list(convo['event_dict'].keys())
                },
                "market": {
                    "type":"string",
                    "description":"The type of odds to get.",
                    "enum": markets(convo['league'])
                }
            },
            "required":["market"]
        }
    }
    ]
main = Conversation(
    """You are a sports betting advisor. Use the functions to answer the users questions. ALWAYS call the set_league function first.""", 
    functions=starting_functions, 
    callback=function_parser
    )
prompt = input("Enter your question: ")
while prompt != "exit":
    main.add_message("user", prompt)
    print(main.complete())
    prompt = input("Enter your question: ")
        
        
