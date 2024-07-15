from newhelpers import classify_teams,classify_league,classify_market,get_endpoint,add_tuples
from vars import base_url, base_params, player_props
from collections import defaultdict
from datetime import datetime
import numpy as np


def get_leagues(_):
    league_json = get_endpoint(f'{base_url}/sports', params = base_params)
    league_groups = defaultdict(list)
    for item in league_json:
        if not item['has_outrights']:
            league_groups[item['group']].append(item['title'])
    out = [f"## Available Leagues: "]
    for group in league_groups:
        out.append(f"### {group}")
        out.extend([f"* {league}" for league in league_groups[group]])
    return out

def get_events(inp:str):
    league_json = get_endpoint(f'{base_url}/sports', params = base_params)
    league_names = []
    league_keydict = {}
    for item in league_json:
        if not item['has_outrights']:
            league_names.append(item['title'])
            league_keydict[item['title']] = item['key']
    league = classify_league(inp, league_names)
    league_key = league_keydict[league]
    events_json = get_endpoint(f"{base_url}/sports/{league_key}/events",base_params)
    event_list = []
    for event in events_json:
        dt = datetime.strptime(event['commence_time'], '%Y-%m-%dT%H:%M:%SZ')
        time = dt.strftime("%B %d, %I:%M %p UTC")
        event_list.append((f"* {event['home_team']} vs {event['away_team']}",time))
    if event_list == []:
        return [f'## No upcoming events found for {league}']
    limit = 10
    return [f'## Upcoming {league} matches: '] + [f"{event[0]}: {event[1]}" for event in event_list[:limit]]

def get_odds(inp:str):
    league_json = get_endpoint(f'{base_url}/sports', params = base_params)
    league_names = []
    league_keydict = {}
    for item in league_json:
        if not item['has_outrights']:
            league_names.append(item['title'])
            league_keydict[item['title']] = item['key']
    league = classify_league(inp, league_names)
    league_key = league_keydict[league]
    events_json = get_endpoint(f"{base_url}/sports/{league_key}/events",base_params)
    event_dict = {f"{event['home_team']} vs {event['away_team']}":event['id'] for event in events_json}
    teams = classify_teams(inp, list(event_dict.keys()))
    markets = ['h2h','spreads','totals'] + (player_props[league_key] if league_key in player_props else [])
    market = classify_market(inp, markets)
    id = event_dict[teams]
    odds_json = get_endpoint(f"{base_url}/sports/{league_key}/events/{id}/odds", base_params | {'regions':'us','markets':market, "oddsFormat":"american"})
    out = [f"## The odds for {market} on {teams} are: "]
    if not odds_json['bookmakers']:
        raise Exception("Sorry, no bets exist for that market on this sport. Please request a different market.")
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

def get_prediciton(inp:str):
    league_json = get_endpoint(f'{base_url}/sports', params = base_params)
    league_names = []
    league_keydict = {}
    for item in league_json:
        if not item['has_outrights']:
            league_names.append(item['title'])
            league_keydict[item['title']] = item['key']
    league = classify_league(inp, league_names)
    league_key = league_keydict[league]
    events_json = get_endpoint(f"{base_url}/sports/{league_key}/events",base_params)
    event_dict = {f"{event['home_team']} vs {event['away_team']}":event['id'] for event in events_json}
    teams = classify_teams(inp, list(event_dict.keys()))
    home_team,away_team = teams.split(' vs ')
    markets = ['h2h','spreads','totals'] + (player_props[league_key] if league_key in player_props else [])
    market = classify_market(inp, markets)
    id = event_dict[teams]
    odds_json = get_endpoint(f"{base_url}/sports/{league_key}/events/{id}/odds", base_params | {'regions':'us','markets':market, "oddsFormat":"decimal"})
    if not odds_json['bookmakers']:
        raise Exception("Sorry, no bets exist for that market on this sport. Please request a different market.")
    outcome_dict = defaultdict(lambda: (0,0))
    playerProp = None
    if market == 'h2h':
        keyfunc = lambda n,d,p:n
    elif market == 'spreads':
        keyfunc = lambda n,d,p:(n,p)
    elif market == 'totals':
        keyfunc = lambda n,d,p:f'{n} {p}'
    else:
        probe = odds_json[0]['bookmakers'][0]['markets'][0]['outcomes'][0]
        if 'point' in probe:
            #over/under player prop
            keyfunc = lambda n,d,p:(d,n,p) 
            playerProp = 1
        else:
            #non-over/under player prop
            keyfunc = lambda n,d,p:(d,n)
            playerProp = 0
    
    for bookmaker in odds_json['bookmakers']:
        outcomes = bookmaker['markets'][0]['outcomes']
        for outcome in outcomes:
            key = keyfunc(outcome.get('name'),outcome.get('description'),outcome.get('point'))
            outcome_dict[key] = add_tuples(outcome_dict[key],(100/outcome['price'],1))

    average_dict = {bet:round(total[0]/total[1]) for bet, total in outcome_dict.items()}
    if market in {'h2h','totals'}:     
        scale = 100/sum(average_dict.values())
        out = [f'* {bet}: {round(prob*scale,2)}%' for bet,prob in average_dict.items()]
    elif market == 'spreads':
        new_dict = {}
        out = []
        for bet,prob in average_dict.items():
            team,point = bet
            other_team = home_team if team == away_team else away_team
            if (other_team,-point) in new_dict:
                scale = 100/(prob+new_dict[(other_team,-point)])
                out.append(f'* {team} {point}: {round(prob*scale,2)}%')
                out.append(f'* {other_team} {-point}: {round(new_dict[(other_team,-point)]*scale,2)}%')
            else:
                new_dict[bet] = prob
    elif playerProp == 1:
        new_dict = {}
        out = []
        for bet,prob in average_dict.items():
            player,pos,point = bet
            other_pos = 'Over' if pos == 'Under' else 'Under'
            if (player,other_pos,point) in new_dict:
                scale = 100/(prob+new_dict[(player,other_pos,point)])
                out.append(f'* {pos} {point} - {player}: {round(prob*scale,2)}%')
                out.append(f'* {other_pos} {point} - {player}: {round(new_dict[(player,other_pos,point)]*scale,2)}%')
            else:
                new_dict[bet] = prob
    else:
        new_dict = defaultdict(dict)
        for bet,prob in average_dict.items():
            player,pos = bet
            new_dict[player][pos] = prob
        newnew_dict = dict()
        for player in new_dict:
            scale = 100/sum(new_dict[player].values())
            for pos in new_dict[player]:
                out.append(f'({player} - {pos}: {round(new_dict[player][pos]*scale,2)}%')
    return [f"# Here is my prediciton for {teams}, {market}: "] + out

def get_scores(inp:str):
    league_json = get_endpoint(f'{base_url}/sports', params = base_params|{'all':'true'})
    league_names = []
    league_keydict = {}
    for item in league_json:
        if not item['has_outrights']:
            league_names.append(item['title'])
            league_keydict[item['title']] = item['key']
    league = classify_league(inp, league_names)
    league_key = league_keydict[league]
    scores_json = get_endpoint(f"{base_url}/sports/{league_key}/scores", base_params)
    score_dict = {}
    for event in scores_json:
        if event['scores'] is not None:
            score_dict[f'{event["scores"][0]["name"]} vs {event["scores"][1]["name"]}'] = f"### {event['scores'][0]['name']}: {event['scores'][0]['score']}\n### {event['scores'][1]['name']}: {event['scores'][1]['score']}"
    if not score_dict:
        raise Exception("Sorry, no scores are available for that league right now.")
    teams = classify_teams(inp, list(score_dict.keys()))
    return [score_dict[teams]]

def get_markets(inp:str):
    league_json = get_endpoint(f'{base_url}/sports', params = base_params)
    league_names = []
    league_keydict = {}
    for item in league_json:
        if not item['has_outrights']:
            league_names.append(item['title'])
            league_keydict[item['title']] = item['key']
    league = classify_league(inp, league_names)
    league_key = league_keydict[league]
    markets = ['h2h','spreads','totals'] + (player_props[league_key] if league_key in player_props else [])
    return [f'## Here are the available markets for {league}: ']+[f"* {market}" for market in markets]

def get_best_odds(inp:str):
    league_json = get_endpoint(f'{base_url}/sports', params = base_params)
    league_names = []
    league_keydict = {}
    for item in league_json:
        if not item['has_outrights']:
            league_names.append(item['title'])
            league_keydict[item['title']] = item['key']
    league = classify_league(inp, league_names)
    league_key = league_keydict[league]
    events_json = get_endpoint(f"{base_url}/sports/{league_key}/events",base_params)
    event_dict = {f"{event['home_team']} vs {event['away_team']}":event['id'] for event in events_json}
    teams = classify_teams(inp, list(event_dict.keys()))
    markets = ['h2h','spreads','totals'] + (player_props[league_key] if league_key in player_props else [])
    market = classify_market(inp, markets)
    id = event_dict[teams]
    odds_json = get_endpoint(f"{base_url}/sports/{league_key}/events/{id}/odds", base_params | {'regions':'us','markets':market, "oddsFormat":"american"})
    if not odds_json['bookmakers']:
        raise Exception("Sorry, no bets exist for that market on this sport. Please request a different market.")
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

def get_arbitrages(inp:str):
    league_json = get_endpoint(f'{base_url}/sports', params = base_params)
    league_names = []
    league_keydict = {}
    for item in league_json:
        if not item['has_outrights']:
            league_names.append(item['title'])
            league_keydict[item['title']] = item['key']
    league = classify_league(inp, league_names)
    league_key = league_keydict[league]
    all_odds_json = get_endpoint(f"{base_url}/sports/{league_key}/odds", base_params | {'regions':'us', "oddsFormat":"decimal", "markets":"h2h,spreads,totals"})
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
            if market == 'h2h':
                if sum([1/price for price,_ in best.values()]) < 1:
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
                    sumdict[key] += 1/price
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
                    sumdict[point] += 1/price
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
                    american = f'+{round((price-1)*100)}' if price >= 2 else round(-100/(price-1))
                    out.append(f'* {title}: {price} ({bookmaker})')
        return out
                    
    else:
        return [f'## No arbitrages found. Try a different league or try again later.']

def get_advice(inp:str):
    league_json = get_endpoint(f'{base_url}/sports', params = base_params)
    league_names = []
    league_keydict = {}
    for item in league_json:
        if not item['has_outrights']:
            league_names.append(item['title'])
            league_keydict[item['title']] = item['key']
    league = classify_league(inp, league_names)
    league_key = league_keydict[league]
    markets = ['h2h','spreads','totals'] + (player_props[league_key] if league_key in player_props else [])
    market = classify_market(inp, markets)
    all_odds_json = get_endpoint(f"{base_url}/sports/{league_key}/odds", base_params | {'regions':'us', "oddsFormat":"decimal", "markets":market})
    data = defaultdict(lambda: defaultdict(list))
    if market == 'h2h':
        keyfunc = lambda n,d,p:n
    elif market == 'spreads':
        keyfunc = lambda n,d,p:f'{n} {p}'
    elif market == 'totals':
        keyfunc = lambda n,d,p:f'{n} {p}'
    else:
        probe = all_odds_json[0]['bookmakers'][0]['markets'][0]['outcomes'][0]
        if 'point' in probe:
            #over/under player prop
            keyfunc = lambda n,d,p:f'{d} - {n} {p}'   
        else:
            #non-over/under player prop
            keyfunc = lambda n,d,p:f'{d} - {n}'
    for event in all_odds_json:
        home_team,away_team = event['home_team'],event['away_team']
        for bookmaker in event['bookmakers']:
            outcomes = bookmaker['markets'][0]['outcomes']
            for outcome in outcomes:
                key = keyfunc(outcome.get('name'),outcome.get('description'),outcome.get('point'))
                data[(home_team,away_team)][key].append(1/outcome['price'])
    if not data:
        raise Exception("Sorry, no bets exist for that market on this sport. Please request a different market or sport.")
    maxvar = 0
    best = {}
    for event, outcomes in data.items():
        for outcome in outcomes:
            current = data[event][outcome]
            var = np.var(current)
            if var > maxvar:
                maxvar = var
                best['event'] = event
                best['outcome'] = outcome
                best['price'] = min(current)
    if not best:
        return [f'## No advice found. Try a different league or try again later.']
    ev = 'low' if maxvar < 0.001 else 'medium' if maxvar < 0.004 else 'high'
    for event in all_odds_json:
        if best['event'] == (event['home_team'],event['away_team']):
            for bookmaker in event['bookmakers']:
                outcomes = bookmaker['markets'][0]['outcomes']
                for outcome in outcomes:
                    if keyfunc(outcome.get('name'),outcome.get('description'),outcome.get('point')) == best['outcome'] and 1/outcome['price'] == best['price']:
                        american = f'+{round((outcome["price"]-1)*100)}' if outcome['price'] >= 2 else round(-100/(outcome['price']-1))
                        return [f'## Based on the current odds, my best advice is to bet on {outcome["name"]} at {american} at {bookmaker["title"]}. This is a {ev} expected value bet.']
            


func_dict = {
    'events': get_events,
    'odds': get_odds,
    'markets': get_markets,
    'best': get_best_odds,
    'scores': get_scores,
    'arb': get_arbitrages,
    'leagues': get_leagues,
    'predict': get_prediciton,
    'advice': get_advice
}