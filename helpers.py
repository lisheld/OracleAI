import requests
import json
from openai import OpenAI
from dotenv import load_dotenv
import os
load_dotenv()
client = OpenAI(api_key=os.getenv('openai'))

def get_endpoint(url,params):
    response = requests.get(url,params=params)
    if (code:=response.status_code) != 200:
        raise ValueError(f"Failed to fetch data. Status code: {code}")
    return response.json()

def send_message(message,conversation):
    conversation.append({"role": "user","content":message})
    response = client.chat.completions.create(
        messages=conversation,
        model="gpt-3.5-turbo"
    )
    out = response.choices[0].message['content']
    conversation.append({"role": "assistant","content":out})
    return out

