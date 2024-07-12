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

def chat_completion_request(messages, functions=None, model=GPT_MODEL, output_type="text"):
    try:
        response = client.chat.completions.create(
        model=model,
        messages=messages,
        functions=functions,
        response_format={'type': output_type}
        )
        return response
    except Exception as e:
        print("Unable to generate ChatCompletion response")
        print(f"Exception: {e}")
        return e

class Conversation:
    def __init__(self, opening_prompt = "You are a helpful assistant.", functions=None, callback=None):
        self.conversation_history = [{"role":"system", "content":opening_prompt}]
        self.functions = functions if functions is not None else []
        self.callback = callback
        self.vars = {}

    def add_message(self, role, content, name=None):
        if role =='function':
            if name is not None:
                message = {"role": role, "content": content, "name":name}
            else:
                raise ValueError("Name needs to be defined for functions.")
        else:
            message = {"role": role, "content": content}
        self.conversation_history.append(message)
    
    def complete(self, funcToCall = None, output_type="text"):
        if not self.functions:
            response = chat_completion_request(self.conversation_history, output_type=output_type)
            print(response)
            text = response.choices[0].message.content
            self.add_message("assistant",text)
            return text
        else:
            response = chat_completion_request(self.conversation_history, self.functions)
            full_message = response.choices[0]
            if full_message.finish_reason == "function_call":
                if self.callback is None:
                    raise AttributeError("No callback function defined.")
                return self.callback(self, full_message, funcToCall)
            else:
                text = full_message.message.content
                self.add_message("assistant", text)
                return text
    
    def __setitem__(self, var, val):
        self.vars[var] = val
    
    def __getitem__(self, var):
        return self.vars.get(var, None)
    
    def add_func(self,func):
        self.functions.append(func)
    
    def __repr__(self):
        return '\n'.join([message['content'] for message in self.conversation_history])

def check(keys:list,dictionary:dict, message:str=None):
    error_messages = {
    'key': lambda key: f"{key} is not a valid key.",
    'teams': lambda teams: f"{teams} is not a valid event.",
    'league': lambda league: f"{league} is not a valid league.",
    'market': lambda market: f"{market} is not a valid market.",
    }
    for key in keys:
        if key not in dictionary:
            if message is not None:
                raise KeyError(error_messages[message](key))
            else:
                raise KeyError(f"{key} is not a valid key.")


def classify(inp:str, type_of_input:str, options:list):
    main = Conversation(f"""
                        You are an expert in identifying {type_of_input} from a user input. Select {type_of_input} from the following options: {options}, and return an error if none of the options match. Return the output as a JSON object.""")
    main.add_message("user",inp)
    out = json.loads(main.complete(output_type="json_object"))
    if "error" in out:
        raise Exception(out['error'])
    return list(out.values())[0]
    






