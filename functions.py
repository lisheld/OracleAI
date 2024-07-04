from helpers import *
from vars import player_props, base_url, base_params



def markets(league_key):
    if 'winner' in league_key:
        return ['outrights']
    return ['h2h','spreads','totals']+(player_props[league_key] if league_key in player_props else [])

def init(convo,parsed_output, funcToCall:str = None):
    check_keys(['league'],parsed_output)
 
    convo['league_key'] = parsed_output['league']
    events_json = get_endpoint(f"{base_url}/sports/{convo['league_key']}/events",base_params)
    scores_json = get_endpoint(f"{base_url}/sports/{convo['league_key']}/scores",base_params|{'daysFrom':3})
    convo['event_dict'] = {f'{event["home_team"]}, {event["away_team"]}': event['id'] for event in events_json}
    convo['markets'] = markets(convo['league_key'])
    convo['score_dict'] = {f'{event["scores"][0]["name"]}, {event["scores"][1]["name"]}': f"{event['scores'][0]['name']}: {event['scores'][0]['score']}\n{event['scores'][1]['name']}: {event['scores'][1]['score']}" for event in scores_json if event['scores'] is not None}
    convo['event_list'] = [f"{event['home_team']} vs {event['away_team']}" for event in events_json]
    convo.add_func(
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
                            "enum": convo['markets']
                        }
                    }
                }
            }
        )
    convo.add_func(
        {
            "name":"get_advice",
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
    )
    convo.add_func(
        {
            "name":"get_scores",
            "description": "Use this function to get the scores for the league the user is requesting info on.",
            "parameters": {
                'type':'object',
                'properties':{
                    'teams':{
                        'type':'string',
                        'description':'The teams involved in the event',
                        'enum': list(convo["score_dict"].keys())
                    }
                }
            }
        }
    )
    convo.add_func(
        {
            "name":"get_markets",
            "description": "Use this function to get the markets for the league the user is requesting info on."
        }
    )
    convo.add_func(
        {
            "name":"get_events",
            "description": "Use this function to get the events for the league the user is requesting info on."
        }
    )
    if funcToCall:
        convo.add_message('function', f'Successfully initialized. Call the function {funcToCall} now.', 'init')
    else:
        convo.add_message('function', 'Successfully initialized. Call the function the user wants now.', 'init')
    convo.complete(onlyFunc = True)
    return []

def get_events(convo,parsed_output):
    return ['Here are the matches: ']+convo['event_list']

def get_odds(convo,parsed_output):
    check_keys(['teams','market'],parsed_output)
    teams = parsed_output['teams']
    market = parsed_output['market']
    league_key = convo['league_key']
    id = convo['event_dict'][teams]
    odds_json = get_endpoint(f"{base_url}/sports/{league_key}/events/{id}/odds", base_params | {'regions':'us','markets':market, "oddsFormat":"american"})
    out = []
    for bookmaker in odds_json['bookmakers']:
        out.append(f"{bookmaker['title']}:")
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
    return out

def get_scores(convo,parsed_output):
    check_keys(['teams'],parsed_output)
    teams = parsed_output['teams']
    return [convo['score_dict'][teams]]

def get_markets(convo,parsed_output):
    return [f'Here are the available markets for {convo["league_key"]}: {convo["markets"]}']

def get_advice(convo,parsed_output):
    check_keys(['teams','market'],parsed_output)
    teams = parsed_output['teams']
    market = parsed_output['market']
    league_key = convo['league_key']
    id = convo['event_dict'][teams]
    odds_json = get_endpoint(f"{base_url}/sports/{league_key}/events/{id}/odds", base_params | {'regions':'us','markets':market, "oddsFormat":"american"})
    current_best = {}
    probe = odds_json['bookmakers'][0]['markets'][0]['outcomes'][0]
    print(probe)
    if 'description' in probe:
        for bookmaker in odds_json['bookmakers']:
            outcomes = bookmaker['markets'][0]['outcomes']
            for outcome in outcomes:
                title = (outcome['name'],outcome['description'])
                if current_best.get(title) is None:
                    current_best[title] = (outcome['price'],bookmaker['title'])
                elif outcome['price'] < current_best[title][0]:
                        current_best[title] = (outcome['price'],bookmaker['title'])
    else:
        for bookmaker in odds_json['bookmakers']:
            outcomes = bookmaker['markets'][0]['outcomes']
            for outcome in outcomes:
                title = outcome['name']
                if current_best.get(title) is None:
                    current_best[title] = (outcome['price'],bookmaker['title'])
                elif outcome['price'] < current_best[title][0]:
                        current_best[title] = (outcome['price'],bookmaker['title'])
    return [f"The best odds for {market} on {teams} are: "]+[f"{bet}: {value[0]} ({value[1]})" for bet,value in current_best.items()]
    