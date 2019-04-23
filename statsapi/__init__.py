from . import version
__version__ = version.VERSION
"""Installed version of MLB-StatsAPI"""

DEBUG = False
"""To enable debug: statsapi.DEBUG=True"""
DEBUG = True #TODO: Remove before committing

from . import endpoints
BASE_URL = endpoints.BASE_URL
ENDPOINTS = endpoints.ENDPOINTS

import requests
from datetime import datetime

def schedule(date=None, start_date=None, end_date=None, team='', opponent='', hydrate='', sportId=1):
    """ Get list of games for a given date/range or team/opponent.
    """
    if end_date and not start_date:
        date = end_date
        end_date = None
    if start_date and not end_date:
        date = start_date
        start_date = None

    params = {}

    if date: params.update({'date':date})
    elif start_date and end_date: params.update({'startDate':start_date, 'endDate':end_date})

    if hydrate != '': params.update({'hydrate':str(hydrate)})

    if team != '':
        params.update({'teamId':str(team)})

    if opponent != '':
        params.update({'opponentId':str(opponent)})

    params.update({'sportId':str(sportId)})

    r = get('schedule',params)

    games = []
    if r.get('totalItems') == 0:
        return games #TODO: ValueError('No games to parse from schedule object.') instead?
    else:
        for date in r.get('dates'):
            for game in date.get('games'):
                game_info = {
                                'game_datetime': game['gameDate'],
                                'game_type': game['gameType'],
                                'status': game['status']['detailedState'],
                                'away': game['teams']['away']['team']['name'],
                                'home': game['teams']['home']['team']['name'],
                                'away_id': game['teams']['away']['team']['id'],
                                'home_id': game['teams']['home']['team']['id'],
                                'doubleheader': game['doubleHeader'],
                                'game_num': game['gameNumber']
                            }
                if game_info['status'] == 'Final':
                    game_info.update({
                                        'away_score': game['teams']['away']['score'],
                                        'home_score': game['teams']['home']['score']
                                    })
                    if game['isTie']:
                        game_info.update({
                                            'away_score': game['teams']['away']['score'],
                                            'home_score': game['teams']['home']['score'],
                                            'winner': 'Tie'
                                        })
                    else:
                        game_info.update({
                                            'winner': game['teams']['away']['team']['name'] if game['teams']['away']['isWinner'] else game['teams']['home']['team']['name'],
                                            'loser': game['teams']['home']['team']['name'] if game['teams']['away']['isWinner'] else game['teams']['away']['team']['name'],
                                        })
                    summary = date['date'] + ' - ' + game['teams']['away']['team']['name'] + ' (' + str(game['teams']['away']['score']) + ') @ ' + game['teams']['home']['team']['name'] + ' (' + str(game['teams']['home']['score']) + ')'
                    game_info.update({'summary': summary})
                else:
                    summary = date['date'] + ' - ' + game['teams']['away']['team']['name'] + ' @ ' + game['teams']['home']['team']['name'] + ' (' + game['status']['detailedState'] + ')'
                    game_info.update({'summary': summary})
                        
                games.append(game_info)

        return games

def get(endpoint,params):
    """Call MLB StatsAPI and return JSON data.
    
    This function is for advanced querying of the MLB StatsAPI, 
    and is used by the functions in this library.
    
    endpoint is one of the keys in the ENDPOINT dict
    params is a dict of parameters, as defined in the ENDPOINT dict for each endpoint
    
    statsapi.get('team',{'teamId':143}) will call the team endpoint for teamId=143 (Phillies)
    """

    """Lookup endpoint from input parameter"""
    ep = ENDPOINTS.get(endpoint)
    if not ep: raise ValueError('Invalid endpoint ('+str(endpoint)+').')
    url = ep['url']
    if DEBUG: print("URL:",url) #debug

    path_params = {}
    query_params = {}

    """Parse parameters into path and query parameters, and discard invalid parameters"""
    for p,pv in params.items():
        if ep['path_params'].get(p):
            if DEBUG: print ("Found path param:",p) #debug
            if ep['path_params'][p].get('type') == 'bool':
                if str(pv).lower() == 'false':
                    path_params.update({p: ep['path_params'][p].get('False','')})
                elif str(pv).lower() == 'true':
                    path_params.update({p: ep['path_params'][p].get('True','')})
            else:
                path_params.update({p: str(pv)})
        elif p in ep['query_params']:
            if DEBUG: print ("Found query param:",p) #debug
            query_params.update({p: str(pv)})
        else:
            if DEBUG: print("Found invalid param:",p) #debug

    if DEBUG: print ("path_params:",path_params) #debug
    if DEBUG: print ("query_params:",query_params) #debug

    """Replace path parameters with their values"""
    for k,v in path_params.items():
        if DEBUG: print("Replacing {",k,"}",sep="") #debug
        url = url.replace('{'+k+'}',v)
        if DEBUG: print("URL:",url) #debug
    while url.find('{') != -1 and url.find('}') > url.find('{'):
        param = url[url.find('{')+1:url.find('}')]
        if ep.get('path_params',{}).get(param,{}).get('required'): 
            if ep['path_params'][param]['default'] and ep['path_params'][param]['default'] != '':
                if DEBUG: print("Replacing {",param,"} with default: ",ep['path_params'][param]['default'],sep="") #debug
                url = url.replace('{'+param+'}',ep['path_params'][param]['default'])
            else:
                raise ValueError('Missing required path parameter {'+str(param)+'}')
        else:
            if DEBUG: print("Removing optional param {",param,"}",sep="") #debug
            url = url.replace('{'+param+'}','')
        if DEBUG: print("URL:",url) #debug
    """Add query parameters to the URL"""
    if len(query_params) > 0:
        for k,v in query_params.items():
            if DEBUG: print("Adding query parameter ",k,"=",v,sep="")
            sep = '?' if url.find('?') == -1 else '&'
            url += sep + k + "=" + v
            if DEBUG: print("URL:",url) #debug

    """Make sure required parameters are present"""
    satisfied = False
    missing_params = []
    for x in ep.get('required_params',[]):
        if len(x) == 0: satisfied = True
        else:
            missing_params.extend([a for a in x if a not in query_params])
            if len(missing_params) == 0:
                satisfied = True
                break
    if not satisfied:
        if ep.get('note'):
            note = '\n--Endpoint note: ' + ep.get('note')
        else: note = ''
        raise ValueError("Missing required parameter(s): " + ', '.join(missing_params) + ".\n--Required parameters for the " + endpoint + " endpoint: " + str(ep.get('required_params',[])) + ". \n--Note: If there are multiple sets in the required parameter list, you can choose any of the sets."+note)

    """Make the request"""
    r = requests.get(url)
    if r.status_code not in [200,201]:
        raise ValueError('Request failed. Status Code: ' + str(r.status_code) + '.')
    else:
        return r.json()

    return None
