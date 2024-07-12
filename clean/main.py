from openai import OpenAI
from dotenv import load_dotenv
from helpers import *
import os
import json


load_dotenv()
odds_api_key = os.getenv('odds')
client = OpenAI(api_key=os.getenv('openai'))
GPT_MODEL = "gpt-3.5-turbo"

base_url = 'https://api.the-odds-api.com/v4'
base_params={'apiKey':odds_api_key}    


def call_odds_function(convo, full_message):
    """Function calling function which executes function calls when the model believes it is necessary.
    Currently extended by adding clauses to this if statement."""
    func = full_message.message.function_call
    try:
        parsed_output = json.loads(func.arguments)
        name = func.name
        if name == "get_events":
            convo['league'] = parsed_output["league"] if "league" in parsed_output else "upcoming"
            events_json = get_endpoint(f"{base_url}/sports/{convo['league']}/events",base_params)
            convo['event_dict'] = {f'{event["home_team"]},{event["away_team"]}': event['id'] for event in events_json} if convo['league'] != "upcoming" else {f'{event["home_team"]},{event["away_team"]}': (event['id'],event['key']) for event in events_json}
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
                            "enum":['h2h','spreads','totals','outrights']
                        }
                    },
                    "required":["market"]
                }
            }
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
                            "enum":['h2h','spreads','totals']
                        }
                    },
                    "required":["market"]
                }
            }
            convo.add_func(odds_function)
            convo.add_func(all_odds_function)
            out = "Events have been fetched."
            
        elif name == "get_odds":
            if "teams" not in parsed_output:
                raise ValueError("No teams provided. Ask the user to be more explicit.")
            league_key = convo['league']
            event_dict = convo['event_dict']
            if league_key is None or event_dict is None:
                raise ValueError("League and events must be defined by calling get_events before calling get_odds")
            teams = parsed_output['teams']
            if teams not in event_dict:
                raise ValueError("That match does not exist in the league requested. Please try again with a different league.")
            id = event_dict[teams]
            if league_key == "upcoming":
                events_json = get_endpoint(f"{base_url}/sports/upcoming/events",base_params)
                for event in events_json:
                    if event['id'] == id:
                        event = event
                        break
            event = get_endpoint(f"{base_url}/sports/{league_key}/events/{id}/odds", base_params|{"regions":"us","markets":parsed_output['market']})
            new_outcomes = average_market_odds(event)
            out = json.dumps(new_outcomes)
        elif name == "get_all_odds":
            if "league" not in parsed_output:
                raise ValueError("No league provided. Ask the user to be more explicit.")
            events = []
            market = parsed_output["market"]
            league_key = parsed_output["league"]
            odds = get_endpoint(f"{base_url}/sports/{league_key}/odds", base_params|{"regions":"us","markets":market})
            for event in odds:
                appended_event = {'home_team':event['home_team'],'away_team':event['away_team']}
                new_outcomes = average_market_odds(event)
                appended_event['outcomes'] = new_outcomes
                events.append(appended_event)
            out = json.dumps(events)        
        else:
            raise ValueError("Function does not exist and cannot be called")
    except Exception as e:
        print(f'Error: {e}')
        out = e
    convo.add_message("function", str(out), name)
    response = convo.complete()
    return response


### Get list of valid leagues ###
league_json = get_endpoint(f'{base_url}/sports',params=base_params)
league_keys = [item['key'] for item in league_json]

    

starting_functions = [
    {
        "name":"get_events",
        "description": "Use this function to get the events for the league the user is requesting info on.",
        "parameters": {
            "type":"object",
            "properties": {
                "league": {
                    "type":"string",
                    "description":"The league the user is requesting info on",
                    "enum": league_keys
                },
                
            }
        }
    }
    ]
main = Conversation(
    """You are a sports betting advisor. Use the functions to answer the users questions. 
    Be consise in your answer, combining data from multiple sources when possible. 
    Only give your recommendation with a very brief description of the odds.""", 
    functions=starting_functions, 
    callback=call_odds_function
    )
prompt = input("Enter your question: ")
while prompt != "exit":
    main.add_message("user", prompt)
    print(main.complete())
    prompt = input("Enter your question: ")


