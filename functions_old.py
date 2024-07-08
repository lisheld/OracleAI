from helpers import *
from vars import player_props, base_url, base_params
from collections import defaultdict



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
    convo['score_dict'] = {f'{event["scores"][0]["name"]}, {event["scores"][1]["name"]}': f"### {event['scores'][0]['name']}: {event['scores'][0]['score']}\n### {event['scores'][1]['name']}: {event['scores'][1]['score']}" for event in scores_json if event['scores'] is not None}
    convo['event_list'] = [f"* {event['home_team']} vs {event['away_team']}" for event in events_json]
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
            "name":"get_best_odds",
            "description": "Use this function to get the best odds across bookmakers for a certain event.",
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
    convo.add_func(
        {
            "name":"get_arb",
            "description": "Use this function to find arbitrage bets for the league the user is requesting info on."
        }
    )
    if funcToCall:
        convo.add_message('function', f'Successfully initialized. Call the function {funcToCall} now.', 'init')
    else:
        convo.add_message('function', 'Successfully initialized. Call the function the user wants now.', 'init')
    return convo.complete(onlyFunc = True)

def get_events(convo,_):
    return [f'## Upcoming {convo["league_key"]} matches: '] + convo['event_list']

def get_odds(convo,parsed_output):
    check_keys(['teams','market'],parsed_output)
    teams = parsed_output['teams']
    market = parsed_output['market']
    league_key = convo['league_key']
    check_teams(teams,convo['event_dict'])
    id = convo['event_dict'][teams]
    odds_json = get_endpoint(f"{base_url}/sports/{league_key}/events/{id}/odds", base_params | {'regions':'us','markets':market, "oddsFormat":"american"})
    out = [f"## The odds for {market} on {teams} are: "]
    for bookmaker in odds_json['bookmakers']:
        out.append(f"### {bookmaker['title']}:")
        outcomes = bookmaker['markets'][0]['outcomes']
        initial_outcome = outcomes[0]
        if 'description' in initial_outcome:
            if 'point' in initial_outcome:
                for outcome in outcomes:
                    if outcome['price'] > 0:
                        out.append(f"* {outcome['description']}, {outcome['name']} {outcome['point']}: +{outcome['price']}")
                    else:
                        out.append(f"* {outcome['description']}, {outcome['name']} {outcome['point']}: {outcome['price']}")
                    
            else:
                for outcome in outcomes:
                    if outcome['price'] > 0:
                        out.append(f"* {outcome['description']}, {outcome['name']}: +{outcome['price']}")
                    else:
                        out.append(f"* {outcome['description']}, {outcome['name']}: {outcome['price']}")
        elif 'point' in initial_outcome:
            for outcome in outcomes:
                if outcome['price'] > 0:
                    out.append(f"* {outcome['name']} {outcome['point']}: +{outcome['price']}")
                else:
                    out.append(f"* {outcome['name']} {outcome['point']}: {outcome['price']}")
        else:
            for outcome in outcomes:
                if outcome['price'] > 0:
                    out.append(f"* {outcome['name']}: +{outcome['price']}")
                else:
                    out.append(f"* {outcome['name']}: {outcome['price']}")
        out.append('')
    return out

def get_scores(convo,parsed_output):
    check_keys(['teams'],parsed_output)
    teams = parsed_output['teams']
    check_teams(teams,convo['score_dict'])
    return [convo['score_dict'][teams]]

def get_markets(convo,_):
    return [f'## Here are the available markets for {convo["league_key"]}: ']+[f"* {market}" for market in convo['markets']]

def get_best_odds(convo,parsed_output):
    check_keys(['teams','market'],parsed_output)
    teams = parsed_output['teams']
    market = parsed_output['market']
    league_key = convo['league_key']
    check_teams(teams,convo['event_dict'])
    id = convo['event_dict'][teams]
    odds_json = get_endpoint(f"{base_url}/sports/{league_key}/events/{id}/odds", base_params | {'regions':'us','markets':market, "oddsFormat":"american"})
    current_best = {}
    probe = odds_json['bookmakers'][0]['markets'][0]['outcomes'][0]
    
    def helper(type):
        title_dict = {'dp': lambda x: (x['name'],x['description'],x['point']),
                      'p': lambda x: (x['name'],x['point']),
                      'd': lambda x: (x['name'],x['description']),
                      'n': lambda x: x['name']}
        format_dict = {'dp': lambda k,v: f"* {k[1]}, {k[0]} {k[2]}: {v[0]} ({v[1]})",
                       'p': lambda k,v: f"* {k[0]} {k[1]}: {v[0]} ({v[1]})",
                       'd': lambda k,v: f"* {k[1]}, {k[0]}: {v[0]} ({v[1]})",
                       'n': lambda k,v: f"* {k}: {v[0]} ({v[1]})"
                       }
        for bookmaker in odds_json['bookmakers']:
                outcomes = bookmaker['markets'][0]['outcomes']
                for outcome in outcomes:
                    title = title_dict[type](outcome)
                    if current_best.get(title) is None:
                        current_best[title] = (outcome['price'],bookmaker['title'])
                    elif outcome['price'] > current_best[title][0]:
                            current_best[title] = (outcome['price'],bookmaker['title'])
        for k,v in current_best.items():
            if v[0] > 0:
                current_best[k] = (f'+{v[0]}',v[1])
        return [f"## The best odds for {market} on {teams} are: "]+[format_dict[type](bet,value) for bet,value in current_best.items()]
    
    if 'description' in probe:
        if 'point' in probe:
            return helper('dp')
        else:
            ### This is a non-over/under player prop bet ###
            return helper('d')   
    elif 'point' in probe:
        ### This is a spread or totals bet ###
        return helper('p')
                    
    else:
        ### This is a moneyline bet ###
        return helper('n')
                        
def get_arbitrages(convo, _):
    league_key = convo['league_key']
    all_odds_json = get_endpoint(f"{base_url}/sports/{league_key}/odds", base_params | {'regions':'us', "oddsFormat":"american", "markets":"h2h,spreads,totals"})
    
    # all_odds_json = [
    #     {
    #         "id": "0eecd9a36a6a7664e2080ed929e1ca8e",
    #         "sport_key": "soccer_uefa_european_championship",
    #         "sport_title": "UEFA Euro 2024",
    #         "commence_time": "2024-07-09T19:00:00Z",
    #         "home_team": "Spain",
    #         "away_team": "France",
    #         "bookmakers": [
    #         {
    #             "key": "betrivers",
    #             "title": "BetRivers",
    #             "last_update": "2024-07-07T17:32:04Z",
    #             "markets": [
    #             {
    #                 "key": "spreads",
    #                 "last_update": "2024-07-07T17:32:04Z",
    #                 "outcomes": [
    #                 {"name": "France", "price": 120, "point": 0.5},
    #                 {"name": "Spain", "price": -110, "point": -0.5},
    #                 {"name": "France", "price": 130, "point": 1.0},
    #                 {"name": "Spain", "price": -105, "point": -1.0}
    #                 ]
    #             }
    #             ]
    #         },
    #         {
    #             "key": "betmgm",
    #             "title": "BetMGM",
    #             "last_update": "2024-07-07T17:30:46Z",
    #             "markets": [
    #             {
    #                 "key": "spreads",
    #                 "last_update": "2024-07-07T17:30:46Z",
    #                 "outcomes": [
    #                 {"name": "France", "price": 110, "point": 0.5},
    #                 {"name": "Spain", "price": 100, "point": -0.5},
    #                 {"name": "France", "price": 125, "point": 1.0},
    #                 {"name": "Spain", "price": -100, "point": -1.0}
    #                 ]
    #             }
    #             ]
    #         },
    #         {
    #             "key": "fanduel",
    #             "title": "FanDuel",
    #             "last_update": "2024-07-07T17:31:35Z",
    #             "markets": [
    #             {
    #                 "key": "spreads",
    #                 "last_update": "2024-07-07T17:31:35Z",
    #                 "outcomes": [
    #                 {"name": "France", "price": 115, "point": 0.5},
    #                 {"name": "Spain", "price": -105, "point": -0.5},
    #                 {"name": "France", "price": 135, "point": 1.0},
    #                 {"name": "Spain", "price": -102, "point": -1.0}
    #                 ]
    #             }
    #             ]
    #         }
    #         ]
    #     }
    # ]

    # all_odds_json = [
    #     {
    #         "id": "0eecd9a36a6a7664e2080ed929e1ca8e",
    #         "sport_key": "soccer_uefa_european_championship",
    #         "sport_title": "UEFA Euro 2024",
    #         "commence_time": "2024-07-09T19:00:00Z",
    #         "home_team": "Spain",
    #         "away_team": "France",
    #         "bookmakers": [
    #         {
    #             "key": "betrivers",
    #             "title": "BetRivers",
    #             "last_update": "2024-07-07T17:32:04Z",
    #             "markets": [
    #             {
    #                 "key": "h2h",
    #                 "last_update": "2024-07-07T17:32:04Z",
    #                 "outcomes": [
    #                 {"name": "France", "price": 250},
    #                 {"name": "Spain", "price": 180},
    #                 {"name": "Draw", "price": 210}
    #                 ]
    #             }
    #             ]
    #         },
    #         {
    #             "key": "betmgm",
    #             "title": "BetMGM",
    #             "last_update": "2024-07-07T17:30:46Z",
    #             "markets": [
    #             {
    #                 "key": "h2h",
    #                 "last_update": "2024-07-07T17:30:46Z",
    #                 "outcomes": [
    #                 {"name": "France", "price": 200},
    #                 {"name": "Spain", "price": 190},
    #                 {"name": "Draw", "price": 220}
    #                 ]
    #             }
    #             ]
    #         },
    #         {
    #             "key": "fanduel",
    #             "title": "FanDuel",
    #             "last_update": "2024-07-07T17:31:35Z",
    #             "markets": [
    #             {
    #                 "key": "h2h",
    #                 "last_update": "2024-07-07T17:31:35Z",
    #                 "outcomes": [
    #                 {"name": "France", "price": 220},
    #                 {"name": "Spain", "price": 200},
    #                 {"name": "Draw", "price": 205}
    #                 ]
    #             }
    #             ]
    #         }
    #         ]
    #     }
    # ]

    # all_odds_json = [
    #     {
    #         "id": "0eecd9a36a6a7664e2080ed929e1ca8e",
    #         "sport_key": "soccer_uefa_european_championship",
    #         "sport_title": "UEFA Euro 2024",
    #         "commence_time": "2024-07-09T19:00:00Z",
    #         "home_team": "Spain",
    #         "away_team": "France",
    #         "bookmakers": [
    #         {
    #             "key": "betrivers",
    #             "title": "BetRivers",
    #             "last_update": "2024-07-07T17:32:04Z",
    #             "markets": [
    #             {
    #                 "key": "totals",
    #                 "last_update": "2024-07-07T17:32:04Z",
    #                 "outcomes": [
    #                 {"name": "Over", "price": 110, "point": 2.5},
    #                 {"name": "Under", "price": -105, "point": 2.5},
    #                 {"name": "Over", "price": 115, "point": 3.0},
    #                 {"name": "Under", "price": -110, "point": 3.0}
    #                 ]
    #             }
    #             ]
    #         },
    #         {
    #             "key": "betmgm",
    #             "title": "BetMGM",
    #             "last_update": "2024-07-07T17:30:46Z",
    #             "markets": [
    #             {
    #                 "key": "totals",
    #                 "last_update": "2024-07-07T17:30:46Z",
    #                 "outcomes": [
    #                 {"name": "Over", "price": 105, "point": 2.5},
    #                 {"name": "Under", "price": -100, "point": 2.5},
    #                 {"name": "Over", "price": 120, "point": 3.0},
    #                 {"name": "Under", "price": -105, "point": 3.0}
    #                 ]
    #             }
    #             ]
    #         },
    #         {
    #             "key": "fanduel",
    #             "title": "FanDuel",
    #             "last_update": "2024-07-07T17:31:35Z",
    #             "markets": [
    #             {
    #                 "key": "totals",
    #                 "last_update": "2024-07-07T17:31:35Z",
    #                 "outcomes": [
    #                 {"name": "Over", "price": 108, "point": 2.5},
    #                 {"name": "Under", "price": -103, "point": 2.5},
    #                 {"name": "Over", "price": 118, "point": 3.0},
    #                 {"name": "Under", "price": -107, "point": 3.0}
    #                 ]
    #             }
    #             ]
    #         }
    #         ]
    #     }
    # ]


    arbitrages = defaultdict(list)
    for event in all_odds_json:
        home_team,away_team = event['home_team'],event['away_team']
        current_best = defaultdict(dict)
        for bookmaker in event['bookmakers']:
            for market in bookmaker['markets']:
                name = market['key']
                probe = market['outcomes'][0]
                if 'point' in probe:
                    titlefunc = lambda x: (x['name'],x['point'])
                else:
                    titlefunc = lambda x: (x['name'],)
                for outcome in market['outcomes']:
                    title = titlefunc(outcome)
                    if current_best[name].get(title) is None:
                        current_best[name][title] = (outcome['price'],bookmaker['title'])
                    elif outcome['price'] > current_best[name][title][0]:
                        current_best[title] = (outcome['price'],bookmaker['title'])
        for market,best in current_best.items():
            print(best)
            if market == 'h2h':
                if sum([price/(price-100) if price < 0 else (100/(price+100)) for price,_ in best.values()]) < 1:
                    arbitrages[(home_team,away_team)].append(best)  
            elif market == 'spreads':
                counter = 1
                keydict = {}
                sumdict = defaultdict(int)
                for (team,point),(price,_) in best.items():
                    if (team,point) not in keydict:
                        keydict[(team,point)] = counter
                        other_team = home_team if team == away_team else away_team
                        keydict[(other_team,-point)] = counter
                        counter += 1
                    key = keydict[(team,point)]
                    sumdict[key] += price/(price-100) if price < 0 else (100/(price+100))
                for k,v in sumdict.items():
                    if v < 1:
                        bets = {}
                        for bet, key in keydict.items():
                            if key == k:
                                bets[bet] = best[bet]
                        arbitrages[(home_team,away_team)].append(bets)
            elif market == 'totals':
                sumdict = defaultdict(int)
                for (_,point),(price,__) in best.items():
                    if price >= 0:  
                        sumdict[point] += (100/(price+100))
                    else:
                        sumdict[point] += price/(price-100)
                for bet,prob in sumdict.items():
                    if prob < 1:
                        arbitrages[(home_team,away_team)].append({k:v for k,v in best.items() if k[1] == bet})
    if arbitrages:
        out = [f'## Arbitrages found!']
        for (home,away),bets in arbitrages.items():
            out.append(f'{home} vs {away}')
            for bet in bets:
                for leg,(price,bookmaker) in bet.items():
                    title = leg[0] if len(leg) == 1 else f'{leg[0]}, {leg[1]}'
                    out.append(f'* {title}: {price} ({bookmaker})')
        return out
                    
    else:
        return [f'## No arbitrages found. Try a different league or try again later.']
