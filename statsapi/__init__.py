from . import version
__version__ = version.VERSION
"""Installed version of MLB-StatsAPI"""

DEBUG = False
"""To enable debug: statsapi.DEBUG=True"""

from . import endpoints
BASE_URL = endpoints.BASE_URL
ENDPOINTS = endpoints.ENDPOINTS

import requests
from datetime import datetime

def schedule(date=None, start_date=None, end_date=None, team='', opponent='', sportId=1):
    """Get list of games for a given date/range and/or team/opponent.

    Output will be a list containing a dict for each game. Fields in the dict:

    'game_id': unique MLB game id (primary key, or gamePk)
    'game_datetime': date and timestamp in UTC (be careful if you truncate the time--the date may be the next day for a late game)
    'game_date': date of game (YYYY-MM-DD)
    'game_type': Preseason, Regular season, Postseason, etc. Look up possible values using the meta endpoint with type=gameTypes
    'status': Scheduled, Warmup, In Progress, Final, etc. Look up possible values using the meta endpoint with type=gameStatus
    'away': team name for the away team (e.g. Philadelphia Phillies)
    'home': team name for the home team (e.g. Philadelphia Phillies)
    'away_id': team id for the away team, e.g. 143. Use this to look up other info about a team using the team endpoint with teamId=143
    'home_id': team id for the home team, e.g. 143. Use this to look up other info about a team using the team endpoint with teamId=143
    'doubleheader': indicates if the game is part of a straight doubleheader (Y), a split doubleheader (S), or not part of a doubleheader
    'game_num': game sequence (1, 2) if part of a doubleheader (will be 1 when not part of a doubleheader)
    'away_score': runs scored by the away team (even when game is in progress)
    'home_score': runs scored by the home team (even when game is in progress)
    'winning_team': team name for the winning team, if the game is final (e.g. Philadelphia Phillies)
    'losing_team': team name for the losing team, if the game is final (e.g. Philadelphia Phillies)
    'winning_pitcher': full name of the winning pitcher, if the game is final and has a winner (not postponed/tied)
    'losing_pitcher': full name of the losing pitcher, if the game is final and has a winner (not postponed/tied)
    'save_pitcher': full name of the pitcher credited with a save, if the game is final and has a winner (not postponed/tied)
    'summary':  if the game is final, the summary will include "<Date> - <Away Team Name> (<Away Score>) @ <Home Team Name> (<Home Score>)"
                if the game is not final, the summary will include "<Date> - <Away Team Name> @ <Home Team Name> (<Game Status>)"

    Example use:

    Games between Phillies and Mets in July 2018):

    games = statsapi.schedule(start_date='07/01/2018',end_date='07/31/2018',team=143,opponent=121)

    Print a list of those games with final score or game status:

    for x in games:
        print(x['summary'])

    Output:

    2018-07-09 - Philadelphia Phillies (3) @ New York Mets (4)
    2018-07-09 - Philadelphia Phillies (3) @ New York Mets (1)
    2018-07-10 - Philadelphia Phillies (7) @ New York Mets (3)
    2018-07-11 - Philadelphia Phillies (0) @ New York Mets (3)

    Print a list of decisions for those games:

    for x in games:
        print("%s Game %s - WP: %s, LP: %s" % (x['game_date'],x['game_num'],x['winning_pitcher'],x['losing_pitcher']))

    Output:

    2018-07-09 Game 1 - WP: Tim Peterson, LP: Victor Arano
    2018-07-09 Game 2 - WP: Aaron Nola, LP: Corey Oswalt
    2018-07-10 Game 1 - WP: Enyel De Los Santos, LP: Drew Gagnon
    2018-07-11 Game 1 - WP: Robert Gsellman, LP: Mark Leiter Jr.
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

    if team != '':
        params.update({'teamId':str(team)})

    if opponent != '':
        params.update({'opponentId':str(opponent)})

    params.update({'sportId':str(sportId), 'hydrate':'decisions'})

    r = get('schedule',params)

    games = []
    if r.get('totalItems') == 0:
        return games #TODO: ValueError('No games to parse from schedule object.') instead?
    else:
        for date in r.get('dates'):
            for game in date.get('games'):
                game_info = {
                                'game_id': game['gamePk'],
                                'game_datetime': game['gameDate'],
                                'game_date': date['date'],
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
                                            'winning_team': 'Tie',
                                            'losing_Team': 'Tie'
                                        })
                    else:
                        game_info.update({
                                            'winning_team': game['teams']['away']['team']['name'] if game['teams']['away']['isWinner'] else game['teams']['home']['team']['name'],
                                            'losing_team': game['teams']['home']['team']['name'] if game['teams']['away']['isWinner'] else game['teams']['away']['team']['name'],
                                            'winning_pitcher': game['decisions']['winner']['fullName'],
                                            'losing_pitcher': game['decisions']['loser']['fullName'],
                                            'save_pitcher': game['decisions'].get('save',{}).get('fullName')
                                        })
                    summary = date['date'] + ' - ' + game['teams']['away']['team']['name'] + ' (' + str(game['teams']['away']['score']) + ') @ ' + game['teams']['home']['team']['name'] + ' (' + str(game['teams']['home']['score']) + ')'
                    game_info.update({'summary': summary})
                else:
                    summary = date['date'] + ' - ' + game['teams']['away']['team']['name'] + ' @ ' + game['teams']['home']['team']['name'] + ' (' + game['status']['detailedState'] + ')'
                    game_info.update({'summary': summary})
                        
                games.append(game_info)

        return games

def boxscore(gamePk,battingBox=True,battingInfo=True,fieldingInfo=True,pitchingBox=True,pitchingInfo=True,gameInfo=True,timeCode=None):
    """Get boxscore for a given game.

    Note: This function uses the game endpoint instead of game_box,
    because game_box does not contain the players' names as they should be 
    displayed in the box score (e.g. Last name only or Last, F)
    """
    rowlen = 79
    boxscore = ''
    params = {'gamePk':gamePk,'fields':'gameData,teams,teamName,shortName,teamStats,batting,atBats,runs,hits,rbi,strikeOuts,baseOnBalls,leftOnBase,pitching,inningsPitched,earnedRuns,homeRuns,players,boxscoreName,liveData,boxscore,teams,players,id,fullName,allPositions,abbreviation,seasonStats,batting,avg,ops,battingOrder,info,title,fieldList,note,label,value'}
    if timeCode: params.update({'timeCode':timeCode})
    r = get('game',params)
    if DEBUG: print(r) #debug

    teamInfo = r['gameData']['teams']
    playerInfo = r['gameData']['players']
    away = r['liveData']['boxscore']['teams']['away']
    home = r['liveData']['boxscore']['teams']['home']

    if battingBox:
        awayBatters = [{'namefield':teamInfo['away']['teamName'] + ' Batters', 'ab':'AB', 'r':'R', 'h':'H', 'rbi':'RBI', 'bb':'BB', 'k':'K', 'lob':'LOB', 'avg':'AVG', 'ops':'OPS'}]
        for batterId_int in away['batters']:
            batterId = str(batterId_int)
            namefield = str(away['players']['ID'+batterId]['battingOrder'])[0] if str(away['players']['ID'+batterId]['battingOrder'])[-1] == '0' else "   "
            namefield += " " + away['players']['ID'+batterId]['stats']['batting'].get('note','')
            namefield += playerInfo['ID'+batterId]['boxscoreName'] + "  " + away['players']['ID'+batterId]['position']['abbreviation']
            batter =    {
                            'namefield':namefield,
                            'ab':str(away['players']['ID'+batterId]['stats']['batting']['atBats']),
                            'r':str(away['players']['ID'+batterId]['stats']['batting']['runs']),
                            'h':str(away['players']['ID'+batterId]['stats']['batting']['hits']),
                            'rbi':str(away['players']['ID'+batterId]['stats']['batting']['rbi']),
                            'bb':str(away['players']['ID'+batterId]['stats']['batting']['baseOnBalls']),
                            'k':str(away['players']['ID'+batterId]['stats']['batting']['strikeOuts']),
                            'lob':str(away['players']['ID'+batterId]['stats']['batting']['leftOnBase']),
                            'avg':str(away['players']['ID'+batterId]['seasonStats']['batting']['avg']),
                            'ops':str(away['players']['ID'+batterId]['seasonStats']['batting']['ops'])
                        }
            awayBatters.append(batter)

        """get away team totals"""
        awayBatters.append  ({
                                'namefield':'Totals',
                                'ab':str(away['teamStats']['batting']['atBats']),
                                'r':str(away['teamStats']['batting']['runs']),
                                'h':str(away['teamStats']['batting']['hits']),
                                'rbi':str(away['teamStats']['batting']['rbi']),
                                'bb':str(away['teamStats']['batting']['baseOnBalls']),
                                'k':str(away['teamStats']['batting']['strikeOuts']),
                                'lob':str(away['teamStats']['batting']['leftOnBase']),
                                'avg':'',
                                'ops':'',
                            })

        homeBatters = [{'namefield':teamInfo['home']['teamName'] + ' Batters', 'ab':'AB', 'r':'R', 'h':'H', 'rbi':'RBI', 'bb':'BB', 'k':'K', 'lob':'LOB', 'avg':'AVG', 'ops':'OPS'}]
        for batterId_int in home['batters']:
            batterId = str(batterId_int)
            namefield = str(home['players']['ID'+batterId]['battingOrder'])[0] if str(home['players']['ID'+batterId]['battingOrder'])[-1] == '0' else "   "
            namefield += " " + home['players']['ID'+batterId]['stats']['batting'].get('note','')
            namefield += playerInfo['ID'+batterId]['boxscoreName'] + "  " + home['players']['ID'+batterId]['position']['abbreviation']
            batter =    {
                            'namefield':namefield,
                            'ab':str(home['players']['ID'+batterId]['stats']['batting']['atBats']),
                            'r':str(home['players']['ID'+batterId]['stats']['batting']['runs']),
                            'h':str(home['players']['ID'+batterId]['stats']['batting']['hits']),
                            'rbi':str(home['players']['ID'+batterId]['stats']['batting']['rbi']),
                            'bb':str(home['players']['ID'+batterId]['stats']['batting']['baseOnBalls']),
                            'k':str(home['players']['ID'+batterId]['stats']['batting']['strikeOuts']),
                            'lob':str(home['players']['ID'+batterId]['stats']['batting']['leftOnBase']),
                            'avg':str(home['players']['ID'+batterId]['seasonStats']['batting']['avg']),
                            'ops':str(home['players']['ID'+batterId]['seasonStats']['batting']['ops'])
                        }
            homeBatters.append(batter)

        homeBatters.append  ({
                                'namefield':'Totals',
                                'ab':str(home['teamStats']['batting']['atBats']),
                                'r':str(home['teamStats']['batting']['runs']),
                                'h':str(home['teamStats']['batting']['hits']),
                                'rbi':str(home['teamStats']['batting']['rbi']),
                                'bb':str(home['teamStats']['batting']['baseOnBalls']),
                                'k':str(home['teamStats']['batting']['strikeOuts']),
                                'lob':str(home['teamStats']['batting']['leftOnBase']),
                                'avg':'',
                                'ops':'',
                            })

        """Make sure the home and away batter lists are the same length"""
        while len(awayBatters) > len(homeBatters):
            homeBatters.append(['','','','','','','','','',''])
        while len(awayBatters) < len(homeBatters):
            awayBatters.append(['','','','','','','','','',''])

        """Build the batting box!"""
        for i in range(0,len(awayBatters)):
            if i==0 or i==len(awayBatters)-1:
                boxscore += '-'*rowlen + ' | ' + '-'*rowlen + '\n'
            boxscore += '{namefield:<40} {ab:^3} {r:^3} {h:^3} {rbi:^3} {bb:^3} {k:^3} {lob:^3} {avg:^4} {ops:^5} | '.format(**awayBatters[i])
            boxscore += '{namefield:<40} {ab:^3} {r:^3} {h:^3} {rbi:^3} {bb:^3} {k:^3} {lob:^3} {avg:^4} {ops:^5}\n'.format(**homeBatters[i])
            if i==0 or i==len(awayBatters)-1:
                boxscore += '-'*rowlen + ' | ' + '-'*rowlen + '\n'

        """Get batting notes"""
        awayBattingNotes = {}
        for n in away['note']:
            awayBattingNotes.update({len(awayBattingNotes) : n['label'] + '-' + n['value']})
        homeBattingNotes = {}
        for n in home['note']:
            homeBattingNotes.update({len(homeBattingNotes) : n['label'] + '-' + n['value']})

        while len(awayBattingNotes) > len(homeBattingNotes):
            homeBattingNotes.update({len(homeBattingNotes) : ''})
        while len(awayBattingNotes) < len(homeBattingNotes):
            awayBattingNotes.update({len(awayBattingNotes) : ''})

        for i in range(0,len(awayBattingNotes)):
            boxscore += '{:<79} | '.format(awayBattingNotes[i])
            boxscore += '{:<79}\n'.format(homeBattingNotes[i])
            #if i==len(awayBattingNotes)-1:
            #    boxscore += '-'*rowlen + ' | ' + '-'*rowlen + '\n'

        boxscore += ' '*rowlen + ' | ' + ' '*rowlen + '\n'

    """Get batting and fielding info"""
    awayBoxInfo = {}
    homeBoxInfo = {}
    for infoType in ['BATTING','FIELDING']:
        if (infoType=='BATTING' and battingInfo) or (infoType=='FIELDING' and fieldingInfo):
            for z in (x for x in away['info'] if x.get('title')==infoType):
                awayBoxInfo.update({len(awayBoxInfo): z['title']})
                for x in z['fieldList']:
                    if len(x['label'] + ': ' + x['value']) > rowlen:
                        words = iter((x['label'] + ': ' + x['value']).split())
                        check = ''
                        lines = []
                        for word in words:
                            if len(check) + 1 + len(word) <= rowlen:
                                if check=='': check = word
                                else: check += ' ' + word
                            else:
                                lines.append(check)
                                check = '    ' + word
                        if len(check): lines.append(check)
                        for i in range(0,len(lines)):
                            awayBoxInfo.update({len(awayBoxInfo): lines[i] })
                            
                    else:
                        awayBoxInfo.update({len(awayBoxInfo): x['label'] + ': ' + x['value'] })

            for z in (x for x in home['info'] if x.get('title')==infoType):
                homeBoxInfo.update({len(homeBoxInfo): z['title']})
                for x in z['fieldList']:
                    if len(x['label'] + ': ' + x['value']) > rowlen:
                        words = iter((x['label'] + ': ' + x['value']).split())
                        check = ''
                        lines = []
                        for word in words:
                            if len(check) + 1 + len(word) <= rowlen:
                                if check=='': check = word
                                else: check += ' ' + word
                            else:
                                lines.append(check)
                                check = '    ' + word
                        if len(check): lines.append(check)
                        for i in range(0,len(lines)):
                            homeBoxInfo.update({len(homeBoxInfo): lines[i] })
                    else:
                        homeBoxInfo.update({len(homeBoxInfo): x['label'] + ': ' + x['value'] })

            if len(awayBoxInfo) and infoType == 'BATTING':
                awayBoxInfo.update({len(awayBoxInfo) : ' '})
            if len(homeBoxInfo) and infoType == 'BATTING':
                homeBoxInfo.update({len(homeBoxInfo) : ' '})

    if len(awayBoxInfo) > 0:
        while len(awayBoxInfo) > len(homeBoxInfo):
            homeBoxInfo.update({len(homeBoxInfo) : ''})
        while len(awayBoxInfo) < len(homeBoxInfo):
            awayBoxInfo.update({len(awayBoxInfo) : ''})

        for i in range(0,len(awayBoxInfo)):
            boxscore += '{:<79} | '.format(awayBoxInfo[i])
            boxscore += '{:<79}\n'.format(homeBoxInfo[i])
            if i==len(awayBoxInfo)-1:
                boxscore += '-'*rowlen + ' | ' + '-'*rowlen + '\n'

    """Get pitching box"""
    

    if DEBUG: print(boxscore) #debug
    return boxscore

def linescore(gamePk):
    """Get linescore for a given game.
    """
    line = get('game_linescore',{'gamePk':gamePk})

    

    return

def player_stats(personId):
    """Get stats for a given player.
    """
    player = get('person',{'personId':personId})

    

    return

def team_leaders(leaderCategories,teamId=None,season=None):
    """Get stat leaders for a given team.
    Get a list of available leaderCategories by calling the meta endpoint with type=leagueLeaderTypes
    """
    if not season: season = datetime.now().year
    params = {'leaderCategories':leaderCategories,'season': season}
    if teamId: params.update({'teamId':teamId})

    leaders = get('team_leaders',params)

    

    return

def league_leaders(leaderCategories,leagueId=None,season=None):
    """Get stat leaders for a given team.
    Get a list of available leaderCategories by calling the meta endpoint with type=leagueLeaderTypes
    """
    if not season: season = datetime.now().year
    params = {'leaderCategories':leaderCategories,'season':season}
    if leagueId: params.update({'leagueId':leagueId})

    leaders = get('stats_leaders',params)

    

    return

def meta(type,fields=None):
    """Get available values from StatsAPI for use in other queries,
    or look up descriptions for values found in API results.

    For example, to get a list of leader categories to use when calling team_leaders():
    statsapi.meta('leagueLeaderTypes')
    """
    types = ['awards', 'baseballStats', 'eventTypes', 'gameStatus', 'gameTypes', 'hitTrajectories', 'jobTypes', 'languages', 'leagueLeaderTypes', 'logicalEvents', 'metrics', 'pitchCodes', 'pitchTypes', 'platforms', 'positions', 'reviewReasons', 'rosterTypes', 'scheduleEventTypes', 'situationCodes', 'sky', 'standingsTypes', 'statGroups', 'statTypes', 'windDirection']
    if type not in types:
        raise ValueError("Invalid meta type. Available meta types: %s." % types)

    return get('meta',{'type':type})

def notes(endpoint):
    """Get notes for a given endpoint. 
    Will include a list of required parameters, as well as hints for some endpoints.
    If the specified endpoint has more than one distinct parameter requirement, 
    for example one of teamId, leagueId, or leagueListId must be included for the attendance endpoint, 
    the required query parameters list will contain separate sublists for each independent set of requirements:
    'required_params': [['teamId'],['leagueId'],['leagueListid']]

    Path parameters are part of the URL itself, for example the teamId parameter in the team endpoint (143 in the example):
    https://statsapi.mlb.com/api/v1/teams/143

    Query parameters are appended on to the URL after the question mark (hydrate in the example):
    https://statsapi.mlb.com/api/v1/teams/143?hydrate=league

    There is no difference in the way path and query parameters are passed into statsapi.get().
    """
    msg = ""
    if not endpoint: msg = 'No endpoint specified.'
    else:
        if not ENDPOINTS.get(endpoint): msg = 'Invalid endpoint specified.'
        else:
            msg += "Endpoint: " + endpoint + " \n"
            path_params = [k for k,v in ENDPOINTS[endpoint]['path_params'].items()]
            required_path_params = [k for k,v in ENDPOINTS[endpoint]['path_params'].items() if v['required']]
            if required_path_params == []: required_path_params = "None"
            
            query_params = ENDPOINTS[endpoint]['query_params']
            required_query_params = ENDPOINTS[endpoint]['required_params']
            if required_query_params == [[]]: required_query_params = "None"
            msg += "All path parameters: %s. \n" % path_params
            msg += "Required path parameters (note: ver will be included by default): %s. \n" % required_path_params
            msg += "All query parameters: %s. \n" % query_params
            msg += "Required query parameters: %s. \n" % required_query_params
            if 'hydrate' in query_params: msg += "The hydrate function is supported by this endpoint. Call the endpoint with {'hydrate':'hydrations'} in the parameters to return a list of available hydrations. For example, statsapi.get('schedule',{'sportId':1,'hydrate':'hydrations','fields':'hydrations'})\n"
            if ENDPOINTS[endpoint].get('note'): msg += "Developer notes: %s" % ENDPOINTS[endpoint].get('note')

    return msg

def get(endpoint,params):
    """Call MLB StatsAPI and return JSON data.

    This function is for advanced querying of the MLB StatsAPI, 
    and is used by the functions in this library.

    endpoint is one of the keys in the ENDPOINT dict
    params is a dict of parameters, as defined in the ENDPOINT dict for each endpoint

    statsapi.get('team',{'teamId':143}) will call the team endpoint for teamId=143 (Phillies)

    return value will be the raw response from MLB Stats API in json format
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
