import requests
from openai import OpenAI
from vars import GPT_MODEL, openai_api_key
import json
client = OpenAI(api_key=openai_api_key)


def get_endpoint(url,params):
    response = requests.get(url,params=params)
    print(response.url)
    if (code:=response.status_code) != 200:
        raise ValueError(f"Failed to fetch data. Status code: {code}")
    return response.json()

def chat_completion_request(messages, model=GPT_MODEL, output_type="text"):
    response = client.chat.completions.create(
    model=model,
    messages=messages,
    response_format={'type': output_type}
    )
    return response

class Conversation:
    def __init__(self, opening_prompt = "You are a helpful assistant."):
        self.conversation_history = [{"role":"system", "content":opening_prompt}]

    def add_message(self, role, content):
        self.conversation_history.append({"role": role, "content": content})
    
    def complete(self, output_type="text"):
        response = chat_completion_request(self.conversation_history, output_type=output_type)

        text = response.choices[0].message.content
        self.add_message("assistant",text)
        return text
    
    def __repr__(self):
        return '\n'.join([message['content'] for message in self.conversation_history])

def classify_league(inp, options):
    main = Conversation(f"""The user is asking for sports related information. You are an expert in identifying the league of the event they are requesting information on. Select one of the following leagues: {options}, or return an error if none of the options match, but ONLY select an option if they have mentioned it in some form in their input. Return the output as a JSON object with one entry of the form "league":"example_league".""")
    print(inp)
    main.add_message("user", inp)
    out = json.loads(main.complete(output_type="json_object"))
    print(out)
    if "error" in out:
        raise Exception(out['error'])
    out_message = list(out.values())[0]
    if out_message in options:
        return out_message
    else:
        raise Exception("Unable to determine league. Use /leagues to see a list of all leagues.")

def classify_teams(inp, options):
    main = Conversation(f"""The user is asking for sports related information. You are an expert in identifying the teams involved in the event they are requesting information on. Select ONLY one of the following matchups: {options}, or return an error if none of the options match, but ONLY select an option if they have mentioned it in some form in their input. Return the output as a JSON object with one entry of the form "matchup":"team1 vs team2".""")
    main.add_message("user", inp)
    out = json.loads(main.complete(output_type="json_object"))
    print(out)
    if "error" in out:
        raise Exception(out['error'])
    out_message = list(out.values())[0]
    if out_message in options:
        return out_message
    else:
        raise Exception("Unable to determine teams. Use /events {league} to see a list of all events.")

def classify_market(inp, options):
    main = Conversation(f"""The user is asking for sports betting information. You are an expert in identifying the market they want sports betting advice for. Select ONLY one of the following markets: {options}, or return an error if none of the markets match, but ONLY select an option if they have mentioned it in some form in their input. Return the output as a JSON object with one entry of the form "market":"example_market".""")
    main.add_message("user", inp)
    out = json.loads(main.complete(output_type="json_object"))
    print(out)
    if "error" in out:
        raise Exception(out['error'])
    out_message = list(out.values())[0]
    if out_message in options:
        return out_message
    else:
        raise Exception("Unable to determine market. Use /market {league} to see a list of all markets.")
    
def classify_sport(inp, options):
    main = Conversation(f"""The user is asking for sports betting information. You are an expert in identifying the sport they want sports betting advice for. Select ONLY one of the following sports: {options}, or return an error if none of the sports match, but ONLY select an option if they have mentioned it in some form in their input. Return the output as a JSON object with one entry of the form "sport":"example_sport".""")
    main.add_message("user", inp)
    out = json.loads(main.complete(output_type="json_object"))
    print(out)
    if "error" in out:
        raise Exception(out['error'])
    out_message = list(out.values())[0]
    if out_message in options:
        return out_message
    else:
        raise Exception("Unable to determine sport. Use /leagues to see a list of all sports.")

def add_tuples(t1,t2):
    return tuple(i+j for i,j in zip(t1,t2))
    