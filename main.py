from openai import OpenAI
import openai
from dotenv import load_dotenv
from helpers import get_endpoint,send_message
import os
import json

load_dotenv()
odds_api_key = os.getenv('odds')
client = OpenAI(api_key=os.getenv('openai'))
GPT_MODEL = "gpt-3.5-turbo"

base_url = 'https://api.the-odds-api.com/v4'
base_params={'apiKey':odds_api_key}
conversation = [
  {"role": "system", "content": "You are a helpful assistant. Only give the answer to the user's questions, no other text."}
  ]
### Get list of valid sports ###
sports_json = get_endpoint(f'{base_url}/sports',params=base_params)
league_dict = {item['title']:item['key'] for item in sports_json if not "winner" in item['key']}

### Identify league ###
possible_leagues = list(league_dict.keys())
league = send_message(f"From these options: {possible_leagues}, what league is this question about?\n{prompt}\nRespond with ERROR if it is about none of the above.", conversation)

def chat_completion_request(messages, functions=None, model=GPT_MODEL):
  try:
    response = client.chat.completions.create(
      model=model,
      messages=messages,
      functions=functions,
    )
    return response
  except Exception as e:
    print("Unable to generate ChatCompletion response")
    print(f"Exception: {e}")
    return e

class Conversation:
  def __init__(self, opening_prompt = "You are a helpful assistant."):
    self.conversation_history = [{"role":"system", "content":opening_prompt}]
    self.vars = {}

  def add_message(self, role, content):
    message = {"role": role, "content": content}
    self.conversation_history.append(message)
  
  def set(self, var,val):
    self.vars[var]=val


def get_odds(sport: str, markets: list, teams: list):
  events = get_endpoint(f"{base_url}/sports/{sport}/events",base_params|{"markets": markets,"regions":"us"})
  eventid = None
  for event in events:
    if {event["home_team"], event["away_team"]} == set(teams):
      eventid = event['id']
      break
  if eventid is None:
    raise ValueError("No events found.")
  odds = get_endpoint(f"{base_url}/sports/{sport}/events/{eventid}/odds",base_params|{})
  

def chat_completion_with_function_execution(messages, functions=[None]):
  """This function makes a ChatCompletion API call with the option of adding functions"""
  response = chat_completion_request(messages, functions)
  full_message = response.choices[0]
  if full_message.finish_reason == "function_call":
    print(f"Function generation requested, calling function")
    return call_odds_function(messages, full_message)
  else:
    print(f"Function not required, responding to user")
    return response

def call_odds_function():
    ...




available_functions = [
    {
        "name":"get_odds",
        "description": "Use this function to get all the live odds for the sport the user wants advice on.",
        "parameters": {
            "type":"object",
            "properties": {
                "league": {
                    "type":"string",
                    "description":"The league the user is requesting advice on.",
                    "enum":possible_leagues
                }
            }
        }
    }
  ]
assistant = client.beta.assistants.create(
  instructions="You are a sports betting advisor. Use the provided tools to answer the user questions.",
  model="gpt-3.5-turbo",
  tools=available_functions
)