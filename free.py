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


    

# def events(league_key=None):
#     """Function to get events for a specific league."""
#     if league_key is None:
#         raise ValueError("I couldn't find that league or no league were specified.")
#     events_json = get_endpoint(f"{base_url}/sports/{league_key}/events",base_params)
#     return [f"{event['home_team']} vs {event['away_team']}" for event in events_json]

# def scores(teams=None,league_key=None):
#     """Function to get scores for a specific league."""
#     if league_key is None:
#         raise ValueError("I couldn't find that league or no league were specified.")
#     if teams is None:
#         raise ValueError("I couldn't find those teams or no teams were specified.")
#     scores_json = get_endpoint(f"{base_url}/sports/{league_key}/scores", base_params|{"daysFrom":3})
#     home,away = teams.split(',')
#     for event in scores_json[::-1]:
#         if event['home_team'] == home and event['away_team'] == away:
#             scores = event['scores']
#             return [f"{team['name']}: {team['score']}" for team in scores]



def markets(league_key=None): 
    if league_key is None:
            raise ValueError("I couldn't find that league or no league were specified.")
    if 'winner' in league_key:
        return ['outrights']
    return ['head-to-head','spreads','totals']+(player_props[league_key] if league_key in player_props else [])

# def odds(teams=None,league_key=None,market=None):    
#     if league_key is None:
#         raise ValueError("I couldn't find that league or no league were specified.")
#     if teams is None:
#         raise ValueError("I couldn't find those teams or no teams were specified.")
#     if market is None:
#         raise ValueError("I couldn't find that market or no market was specified.")

def function_parser(convo,full_message):
    func = full_message.message.function_call
    # try:
    parsed_output = json.loads(func.arguments)
    name = func.name
    print(f'Calling function: {name}')
    if name == 'init':
        if 'league' not in parsed_output:
            raise ValueError("I couldn't find that league or no league was specified.")
        convo['league'] = parsed_output['league']
        print(convo['league'])          
        events_json = get_endpoint(f"{base_url}/sports/{convo['league']}/events",base_params)
        print(events_json)
        convo['event_dict'] = {f'{event["home_team"]},{event["away_team"]}': event['id'] for event in events_json} if convo['league'] != "upcoming" else {f'{event["home_team"]},{event["away_team"]}': (event['id'],event['key']) for event in events_json}
        convo['markets'] = markets(convo['league'])
        odds_function = {
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
                        "enum": convo['markets']
                    }
                }
            }
        }
        advice_function = {
            "name":"advice",
            "description": "Use this function to give betting advice on a certain event",
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
                        "enum": convo['markets']
                    }
                }
            }
        }
        convo.add_func(odds_function)
        convo.add_func(advice_function)
        convo.add_message('function', 'Successfully initialized. Call the function the user wants now.', 'init')
        convo.complete(onlyFunc = True)
        return
    elif name == 'get_events':
        event_dict = convo['event_dict']
        out = ["Here are the matches: "]+[f"{(teams:=team.split(','))[0]} vs {teams[1]}" for team in event_dict]
    elif name == 'get_markets':
        out = f'Here are the available markets: {convo["markets"]}'
    elif name == 'get_scores':
        teams = parsed_output['teams']
        if convo['league'] == 'upcoming':
            raise ValueError("Please specify a league.")
        if teams is None:
            raise ValueError("I couldn't find those teams or no teams were specified.")
        scores_json = get_endpoint(f"{base_url}/sports/{convo['league_key']}/scores", base_params|{"daysFrom":3})
        home,away = teams.split(',')
        for event in scores_json[::-1]:
            if event['home_team'] == home and event['away_team'] == away:
                scores = event['scores']
                out = [f"{team['name']}: {team['score']}" for team in scores]
                break
    elif name == 'get_odds':
        teams = parsed_output['teams']
        market = parsed_output['market']
        league_key = parsed_output['league']
        if teams is None:
            raise ValueError("I couldn't find those teams or no teams were specified.")
        if market is None:
            raise ValueError("I couldn't find that market or no market was specified.")
        id = convo['event_dict'][teams]
        odds_json = get_endpoint(f"{base_url}/sports/{league_key}/events/{id}/odds", base_params|{'regions':'us','markets':market, "oddsFormat":"american"})
        out = []
        for bookmaker in odds_json['bookmakers']:
            out.append(bookmaker['title'])
            outcomes = bookmaker['markets'][0]['outcomes']
            initial_outcome = outcomes[0]
            if 'description' in initial_outcome:
                for outcome in outcomes:
                        out.append(f"   {outcome['description']} - {outcome['name']} {outcome['point']}: {outcome['price']}")
            elif 'point' in initial_outcome:
                for outcome in outcomes:
                        out.append(f"   {outcome['name']} {outcome['point']}: {outcome['price']}")
            else:
                for outcome in outcomes:
                    out.append(f"   {outcome['name']}: {outcome['price']}")
    elif name == 'advice':
        market = parsed_output['market']
        league_key = convo['league_key']
        teams = parsed_output['teams']
        raise NotImplementedError("Not implemented yet.")
    for line in out:
        print(line)  
    # except Exception as e:
    #     print(f'Error: {e}')
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
                    "enum": league_keys
                },
                
            }
        }
    },
    {
        "name":"get_events",
        "description": "Use this function to get the events for the league the user is requesting info on."
    }
    ]
main = Conversation(
    """You are a sports betting advisor. Use the functions to answer the users questions. ALWAYS call the init function first when responding to the user.""", 
    functions=starting_functions, 
    callback=function_parser
    )
# prompt = input("Enter your question: ")
prompt = 'what are the odds on the spain germany euros game?'
main.add_message("user", prompt)
main.complete(onlyFunc=True)
        
        
