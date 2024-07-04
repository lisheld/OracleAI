from openai import OpenAI
from helpers import *
from functions import *
import json
from vars import openai_api_key, base_url, base_params

client = OpenAI(api_key=openai_api_key)

league_json = get_endpoint(f'{base_url}/sports', params = base_params)
league_keys = [item['key'] for item in league_json]

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
                } 
            }
        }
    }
    ]

def function_parser(convo,full_message):
    func = full_message.message.function_call
    # try:
    parsed_output = json.loads(func.arguments)
    name = func.name
    print(f'Calling function: {name}')
    if name == 'init':
        out = init(convo,parsed_output, frozenset(['get_odds','get_advice','get_scores','get_markets','get_events']))
    elif name == 'get_events':
        out = get_events(convo,parsed_output)
    elif name == 'get_markets':
        out = get_markets(convo,parsed_output)
    elif name == 'get_scores':
        out = get_scores(convo,parsed_output)
    elif name == 'get_odds':
        out = get_odds(convo,parsed_output)
    elif name == 'get_advice':
        out = get_advice(convo,parsed_output)
    for line in out:
        out = print(line)  
    # except Exception as e:
    #     print(f'Error: {e}')
    
    
main = Conversation(
    """You are a sports betting advisor. Use the functions to answer the users questions. ALWAYS call the init function first when responding to the user.""", 
    functions=starting_functions, 
    callback=function_parser
    )
# prompt = input("Enter your question: ")
prompt = 'what is your advice for the spain germany euros game?'
main.add_message("user", prompt)
main.complete(onlyFunc=True)
        
        
