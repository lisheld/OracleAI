import requests
import json
from openai import OpenAI
from dotenv import load_dotenv
import os
from collections import defaultdict
load_dotenv()
client = OpenAI(api_key=os.getenv('openai'))
GPT_MODEL = "gpt-3.5-turbo"



player_props = {
    'americanfootball_nfl': [
    "player_pass_tds",
    "player_pass_yds",
    "player_pass_completions",
    "player_pass_attempts",
    "player_pass_interceptions",
    "player_pass_longest_completion",
    "player_rush_yds",
    "player_rush_attempts",
    "player_rush_longest",
    "player_receptions",
    "player_reception_yds",
    "player_reception_longest",
    "player_kicking_points",
    "player_field_goals",
    "player_tackles_assists",
    "player_1st_td",
    "player_last_td",
    "player_anytime_td"
    ],
    'americanfootball_ncaaf': [
    "player_pass_tds",
    "player_pass_yds",
    "player_pass_completions",
    "player_pass_attempts",
    "player_pass_interceptions",
    "player_pass_longest_completion",
    "player_rush_yds",
    "player_rush_attempts",
    "player_rush_longest",
    "player_receptions",
    "player_reception_yds",
    "player_reception_longest",
    "player_kicking_points",
    "player_field_goals",
    "player_tackles_assists",
    "player_1st_td",
    "player_last_td",
    "player_anytime_td"
    ],
    'basketball_nba': [
    "player_points",
    "player_rebounds",
    "player_assists",
    "player_threes",
    "player_blocks",
    "player_steals",
    "player_blocks_steals",
    "player_turnovers",
    "player_points_rebounds_assists",
    "player_points_rebounds",
    "player_points_assists",
    "player_rebounds_assists",
    "player_first_basket",
    "player_double_double",
    "player_triple_double"
    ],
    'basketball_ncaab': [
    "player_points",
    "player_rebounds",
    "player_assists",
    "player_threes",
    "player_blocks",
    "player_steals",
    "player_blocks_steals",
    "player_turnovers",
    "player_points_rebounds_assists",
    "player_points_rebounds",
    "player_points_assists",
    "player_rebounds_assists",
    "player_first_basket",
    "player_double_double",
    "player_triple_double"
    ],
    'basketball_wnba': [
    "player_points",
    "player_rebounds",
    "player_assists",
    "player_threes",
    "player_blocks",
    "player_steals",
    "player_blocks_steals",
    "player_turnovers",
    "player_points_rebounds_assists",
    "player_points_rebounds",
    "player_points_assists",
    "player_rebounds_assists",
    "player_first_basket",
    "player_double_double",
    "player_triple_double"
    ],
    'baseball_mlb': [
    "batter_home_runs",
    "batter_first_home_run",
    "batter_hits",
    "batter_total_bases",
    "batter_rbis",
    "batter_runs_scored",
    "batter_hits_runs_rbis",
    "batter_singles",
    "batter_doubles",
    "batter_triples",
    "batter_walks",
    "batter_strikeouts",
    "batter_stolen_bases",
    "pitcher_strikeouts",
    "pitcher_record_a_win",
    "pitcher_hits_allowed",
    "pitcher_walks",
    "pitcher_earned_runs",
    "pitcher_outs"
    ],
    'icehockey_nhl': [
    "player_points",
    "player_power_play_points",
    "player_assists",
    "player_blocked_shots",
    "player_shots_on_goal",
    "player_goals",
    "player_total_saves",
    "player_goal_scorer_first",
    "player_goal_scorer_last",
    "player_goal_scorer_anytime"
    ],
    'soccer_epl': [
    "player_goal_scorer_anytime",
    "player_first_goal_scorer",
    "player_last_goal_scorer",
    "player_to_receive_card",
    "player_to_receive_red_card",
    "player_shots_on_target",
    "player_shots",
    "player_assists"
    ],
    'soccer_france_ligue_one': [
    "player_goal_scorer_anytime",
    "player_first_goal_scorer",
    "player_last_goal_scorer",
    "player_to_receive_card",
    "player_to_receive_red_card",
    "player_shots_on_target",
    "player_shots",
    "player_assists"
    ],
    'soccer_germany_bundesliga': [
    "player_goal_scorer_anytime",
    "player_first_goal_scorer",
    "player_last_goal_scorer",
    "player_to_receive_card",
    "player_to_receive_red_card",
    "player_shots_on_target",
    "player_shots",
    "player_assists"
    ],
    'soccer_italy_serie_a': [
    "player_goal_scorer_anytime",
    "player_first_goal_scorer",
    "player_last_goal_scorer",
    "player_to_receive_card",
    "player_to_receive_red_card",
    "player_shots_on_target",
    "player_shots",
    "player_assists"
    ],
    'soccer_spain_la_liga': [
    "player_goal_scorer_anytime",
    "player_first_goal_scorer",
    "player_last_goal_scorer",
    "player_to_receive_card",
    "player_to_receive_red_card",
    "player_shots_on_target",
    "player_shots",
    "player_assists"
    ],
    'soccer_usa_mls': [
    "player_goal_scorer_anytime",
    "player_first_goal_scorer",
    "player_last_goal_scorer",
    "player_to_receive_card",
    "player_to_receive_red_card",
    "player_shots_on_target",
    "player_shots",
    "player_assists"
    ]
}


def get_endpoint(url,params):
    response = requests.get(url,params=params)
    if (code:=response.status_code) != 200:
        raise ValueError(f"Failed to fetch data. Status code: {code}")
    return response.json()

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
    
    def complete(self, noFunc = False, onlyFunc=False):
        if not self.functions or noFunc:
            response = chat_completion_request(self.conversation_history)
            text = response.choices[0].message.content
            self.add_message("assistant",text)
            return text
        else:
            response = chat_completion_request(self.conversation_history, self.functions)
            full_message = response.choices[0]
            if full_message.finish_reason == "function_call":
                if self.callback is None:
                    raise AttributeError("No callback function defined.")
                return self.callback(self, full_message)
            elif not onlyFunc:
                text = full_message.message.content
                self.add_message("assistant", text)
                return text
            else:
                raise ValueError("I can't do that with my current capabilities, sorry!")
    
    def __setitem__(self, var, val):
        self.vars[var] = val
    
    def __getitem__(self, var):
        return self.vars.get(var, None)
    
    def add_func(self,func):
        self.functions.append(func)

def add_outcomes(dict1,dict2):
    """Adding two dictionaries of outcomes together. The first dictionary is the one that will be modified."""
    assert isinstance(dict1,dict) and isinstance(dict2,dict), "Both inputs must be dictionaries"
    for outcome, info2 in dict2.items():
        if outcome in dict1:
            info1 = dict1[outcome]
            newinfo = {val: info1[val] + info2[val] for val in info2}
            dict1[outcome] = newinfo 
        else:
            dict1[outcome] = info2
def outcomes_to_dict(outcomes):
    out = {}
    initial = outcomes[0]
    if 'description' in initial:
        for outcome in outcomes:
            description = outcome['description']
            name = outcome['name']
            other = {i:outcome[i] for i in outcome if i not in {'description','name'}}|{'count':1}
            out[f'{name}, {description}'] = other
    else: 
        for outcome in outcomes:
            name = outcome['name']
            other = {i:outcome[i] for i in outcome if i !='name'}|{'count':1}
            out[name] = other
    return out

def average_market_odds(event):
    new_outcomes = outcomes_to_dict(event['bookmakers'][0]['markets'][0]['outcomes'])
    for bookmaker in event['bookmakers'][1:]:
        add_outcomes(new_outcomes,outcomes_to_dict(bookmaker['markets'][0]['outcomes']))
    
    for outcome, info in new_outcomes.items():
        count = info['count']
        new_outcomes[outcome] = {i: round(info[i]/count, 2) for i in info if i != 'count'}
    return new_outcomes


