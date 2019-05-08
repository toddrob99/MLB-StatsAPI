# encoding=utf-8
"""# MLB-StatsAPI

Python wrapper for MLB Stats API

Created by Todd Roberts

https://pypi.org/project/MLB-StatsAPI/

https://github.com/toddrob99/MLB-StatsAPI

Documentation: https://toddrob99.github.io/MLB-StatsAPI/
"""
import sys
if sys.version_info.major < 3:
    reload(sys)
    sys.setdefaultencoding('utf8')
# Trying to support Python 2.7

from . import version
__version__ = version.VERSION
"""Installed version of MLB-StatsAPI"""

DEBUG = False
"""To enable debug: statsapi.DEBUG=True"""

from . import endpoints
BASE_URL = endpoints.BASE_URL
"""Base MLB Stats API URL"""
ENDPOINTS = endpoints.ENDPOINTS
"""MLB Stats API endpoint configuration"""

import requests
from datetime import datetime

def schedule(date=None, start_date=None, end_date=None, team='', opponent='', sportId=1, game_id=None):
    """Get list of games for a given date/range and/or team/opponent.

    Include a game_id to get data for that game.

    Output will be a list containing a dict for each game. Fields in the dict:

    'game_id': unique MLB game id (primary key, or gamePk)
    'game_datetime': date and timestamp in UTC (be careful if you truncate the time--the date may be the next day for a late game)
    'game_date': date of game (YYYY-MM-DD)
    'game_type': Preseason, Regular season, Postseason, etc. Look up possible values using the meta endpoint with type=gameTypes
    'status': Scheduled, Warmup, In Progress, Final, etc. Look up possible values using the meta endpoint with type=gameStatus
    'away_name': team name for the away team (e.g. Philadelphia Phillies)
    'home_name': team name for the home team (e.g. Philadelphia Phillies)
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
    'home_probable_pitcher': full name of the probable pitcher for the home team, if available
    'away_probable_pitcher': full name of the probable pitcher for the away team, if available
    'home_pitcher_note': pitching report for the home team probable pitcher, if available
    'away_pitcher_note': pitching report for the away team probable pitcher, if available
    'current_inning': current inning (applies best to in-progress games)
    'inning_state': state of current inning: top, middle, bottom, end (applies best to in-progress games)
    'summary':  if the game is final or in progress, the summary will include "<Date> - <Away Team Name> (<Away Score>) @ <Home Team Name> (<Home Score>) (<Game Status>)"
                if the game has not started yet, the summary will include "<Date> - <Away Team Name> @ <Home Team Name> (<Game Status>)"

    Example use:

    Games between Phillies and Mets in July 2018:

    games = statsapi.schedule(start_date='07/01/2018',end_date='07/31/2018',team=143,opponent=121)

    Print a list of those games with final score or game status:

    for x in games:
        print(x['summary'])

    Output:

    2018-07-09 - Philadelphia Phillies (3) @ New York Mets (4) (Final)
    2018-07-09 - Philadelphia Phillies (3) @ New York Mets (1) (Final)
    2018-07-10 - Philadelphia Phillies (7) @ New York Mets (3) (Final)
    2018-07-11 - Philadelphia Phillies (0) @ New York Mets (3) (Final)

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

    if game_id: params.update({'gamePks':game_id})

    params.update({'sportId':str(sportId), 'hydrate':'decisions,probablePitcher(note),linescore'})

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
                                'away_name': game['teams']['away']['team']['name'],
                                'home_name': game['teams']['home']['team']['name'],
                                'away_id': game['teams']['away']['team']['id'],
                                'home_id': game['teams']['home']['team']['id'],
                                'doubleheader': game['doubleHeader'],
                                'game_num': game['gameNumber'],
                                'home_probable_pitcher': game['teams']['home'].get('probablePitcher',{}).get('fullName',''),
                                'away_probable_pitcher': game['teams']['away'].get('probablePitcher',{}).get('fullName',''),
                                'home_pitcher_note': game['teams']['home'].get('probablePitcher',{}).get('note',''),
                                'away_pitcher_note': game['teams']['away'].get('probablePitcher',{}).get('note',''),
                                'away_score': game['teams']['away'].get('score','0'),
                                'home_score': game['teams']['home'].get('score','0'),
                                'current_inning': game['linescore'].get('currentInning',''),
                                'inning_state': game['linescore'].get('inningState','')
                            }
                if game_info['status'] in ['Final','Game Over']:
                    if game.get('isTie'):
                        game_info.update({
                                            'winning_team': 'Tie',
                                            'losing_Team': 'Tie'
                                        })
                    else:
                        game_info.update({
                                            'winning_team': game['teams']['away']['team']['name'] if game['teams']['away'].get('isWinner') else game['teams']['home']['team']['name'],
                                            'losing_team': game['teams']['home']['team']['name'] if game['teams']['away'].get('isWinner') else game['teams']['away']['team']['name'],
                                            'winning_pitcher': game['decisions'].get('winner',{}).get('fullName',''),
                                            'losing_pitcher': game['decisions'].get('loser',{}).get('fullName',''),
                                            'save_pitcher': game['decisions'].get('save',{}).get('fullName')
                                        })
                    summary = date['date'] + ' - ' + game['teams']['away']['team']['name'] + ' (' + str(game['teams']['away']['score']) + ') @ ' + game['teams']['home']['team']['name'] + ' (' + str(game['teams']['home']['score']) + ') (' + game['status']['detailedState'] + ')'
                    game_info.update({'summary': summary})
                elif game_info['status'] == 'In Progress':
                    game_info.update({
                                        'summary': date['date'] + ' - ' + game['teams']['away']['team']['name'] + ' (' + str(game['teams']['away']['score']) + ') @ ' + game['teams']['home']['team']['name'] + ' (' + str(game['teams']['home']['score']) + ') (' + game['linescore']['inningState'] + ' of the ' + game['linescore']['currentInningOrdinal'] + ')'
                                    })
                else:
                    summary = date['date'] + ' - ' + game['teams']['away']['team']['name'] + ' @ ' + game['teams']['home']['team']['name'] + ' (' + game['status']['detailedState'] + ')'
                    game_info.update({'summary': summary})
                        
                games.append(game_info)

        return games

def boxscore(gamePk,battingBox=True,battingInfo=True,fieldingInfo=True,pitchingBox=True,gameInfo=True,timecode=None):
    """Get a formatted boxscore for a given game.

    Note: This function uses the game endpoint instead of game_box,
    because game_box does not contain the players' names as they should be 
    displayed in the box score (e.g. Last name only or Last, F)

    It is possible to get the boxscore as it existed at a specific time by including the timestamp in the timecode parameter.
    The timecode should be in the format YYYYMMDD_HHMMSS, and in the UTC timezone
    For example, 4/24/19 10:32:40 EDT (-4) would be: 20190425_012240
    A list of timestamps for game events can be found through the game_timestamps endpoint:
    statsapi.get('game_timestamps',{'gamePk':565997})

    Example use:

    Print the full box score for Phillies @ Mets game on 4/24/2019 (gamePk=565997):

    print( statsapi.boxscore(565997) )

    Output:

    ------------------------------------------------------------------------------- | -------------------------------------------------------------------------------
    Phillies Batters                         AB   R   H  RBI BB   K  LOB AVG   OPS  | Mets Batters                             AB   R   H  RBI BB   K  LOB AVG   OPS
    ------------------------------------------------------------------------------- | -------------------------------------------------------------------------------
    1 McCutchen  LF                           5   0   1   0   0   1   3  .250 .830  | 1 McNeil  LF                              4   0   1   0   0   0   1  .363 .928
    2 Realmuto  C                             3   1   1   0   1   1   2  .282 .786  | 2 Conforto  RF                            3   0   0   0   1   1   1  .292 .986
    3 Harper  RF                              4   1   1   1   1   3   4  .261 .909  | 3 Canó  2B                                3   0   3   0   1   0   0  .272 .758
    4 Hoskins  1B                             4   2   2   2   1   1   3  .273 .982  | 4 Ramos, W  C                             4   0   0   0   0   3   6  .278 .687
    5 Franco  3B                              5   1   1   1   0   0   3  .271 .905  | 5 Smith, Do  1B                           2   0   0   0   1   1   2  .400 .996
    6 Hernández, C  2B                        5   1   1   0   0   1   2  .267 .730  |     c-Alonso, P  1B                       1   0   0   0   0   1   1  .306 1.086
    7 Rodríguez, S  SS                        4   0   1   0   0   1   1  .250 .750  | 6 Frazier, T  3B                          3   0   0   0   0   0   4  .182 .705
    8 Velasquez  P                            1   0   0   0   0   0   0  .167 .453  | 7 Rosario, A  SS                          4   0   1   0   0   0   1  .261 .676
        a-Williams, N  PH                     1   0   0   0   0   0   1  .150 .427  | 8 Lagares  CF                             2   0   0   0   0   1   1  .244 .653
        Neshek  P                             0   0   0   0   0   0   0  .000 .000  |     a-Nimmo  CF                           2   0   0   0   0   0   1  .203 .714
        Domínguez  P                          0   0   0   0   0   0   0  .000 .000  | 9 Vargas  P                               2   0   0   0   0   1   1  .000 .000
        b-Gosselin  PH                        1   0   1   1   0   0   0  .211 .474  |     Lugo, S  P                            0   0   0   0   0   0   0  .000 .000
        Morgan  P                             0   0   0   0   0   0   0  .000 .000  |     Zamora  P                             0   0   0   0   0   0   0  .000 .000
        c-Knapp  PH                           1   0   0   0   0   1   1  .222 .750  |     b-Guillorme  PH                       1   0   1   0   0   0   0  .167 .378
        Nicasio  P                            0   0   0   0   0   0   0  .000 .000  |     Gsellman  P                           0   0   0   0   0   0   0  .000 .000
    9 Quinn  CF                               4   0   1   1   0   1   1  .120 .305  |     Rhame  P                              0   0   0   0   0   0   0  .000 .000
        1-Altherr  CF                         0   0   0   0   0   0   0  .042 .163  |     d-Davis, J  PH                        1   0   0   0   0   1   0  .276 .865
    ------------------------------------------------------------------------------- | -------------------------------------------------------------------------------
    Totals                                   38   6  10   6   3  10  21             | Totals                                   32   0   6   0   3   9  19
    ------------------------------------------------------------------------------- | -------------------------------------------------------------------------------
    a-Popped out for Velasquez in the 6th.                                          | a-Flied out for Lagares in the 6th.
    b-Singled for Domínguez in the 8th.                                             | b-Singled for Zamora in the 7th.
    c-Struck out for Morgan in the 9th.                                             | c-Struck out for Smith, Do in the 8th.
    1-Ran for Quinn in the 8th.                                                     | d-Struck out for Rhame in the 9th.
                                                                                    |
    BATTING                                                                         | BATTING
    2B: Harper (7, Vargas); Rodríguez, S (1, Rhame); Realmuto (4, Vargas).          | TB: Canó 3; Guillorme; McNeil; Rosario, A.
    3B: Hoskins (1, Gsellman).                                                      | Runners left in scoring position, 2 out: Frazier, T 2; Vargas; Smith, Do 2.
    HR: Hoskins (7, 9th inning off Rhame, 1 on, 0 out).                             | GIDP: McNeil.
    TB: Franco; Gosselin; Harper 2; Hernández, C; Hoskins 7; McCutchen; Quinn;      | Team RISP: 0-for-6.
        Realmuto 2; Rodríguez, S 2.                                                 | Team LOB: 9.
    RBI: Franco (19); Gosselin (4); Harper (15); Hoskins 2 (20); Quinn (1).         |
    Runners left in scoring position, 2 out: Hoskins; Hernández, C; Knapp; Realmuto | FIELDING
        2; McCutchen.                                                               | E: Canó (3, fielding); Rosario, A 2 (7, throw, throw).
    SAC: Rodríguez, S; Velasquez.                                                   |
    Team RISP: 4-for-13.                                                            |
    Team LOB: 11.                                                                   |
                                                                                    |
    FIELDING                                                                        |
    DP: (Hernández, C-Rodríguez, S-Hoskins).                                        |
    ------------------------------------------------------------------------------- | -------------------------------------------------------------------------------
    ------------------------------------------------------------------------------- | -------------------------------------------------------------------------------
    Phillies Pitchers                            IP   H   R  ER  BB   K  HR   ERA   | Mets Pitchers                                IP   H   R  ER  BB   K  HR   ERA
    ------------------------------------------------------------------------------- | -------------------------------------------------------------------------------
    Velasquez  (W, 1-0)                         5.0   3   0   0   3   6   0   1.99  | Vargas  (L, 1-1)                            4.2   3   1   1   2   4   0   7.20
    Neshek  (H, 2)                              1.0   1   0   0   0   0   0   2.70  | Lugo, S                                     2.0   0   0   0   0   2   0   4.60
    Domínguez  (H, 3)                           1.0   1   0   0   0   0   0   4.32  | Zamora                                      0.1   0   0   0   0   1   0   0.00
    Morgan                                      1.0   1   0   0   0   2   0   0.00  | Gsellman                                    1.0   5   3   3   0   1   0   4.20
    Nicasio                                     1.0   0   0   0   0   1   0   5.84  | Rhame                                       1.0   2   2   2   1   2   1   8.10
    ------------------------------------------------------------------------------- | -------------------------------------------------------------------------------
    Totals                                      9.0   6   0   0   3   9   0         | Totals                                      9.0  10   6   6   3  10   1
    ------------------------------------------------------------------------------- | -------------------------------------------------------------------------------
    WP: Velasquez; Gsellman.
    HBP: Realmuto (by Vargas); Frazier, T (by Velasquez).
    Pitches-strikes: Velasquez 97-53; Neshek 13-8; Domínguez 9-6; Morgan 14-10; Nicasio 15-10; Vargas 89-53; Lugo, S 32-23; Zamora 5-3; Gsellman 25-17; Rhame 19-12.
    Groundouts-flyouts: Velasquez 6-3; Neshek 1-2; Domínguez 1-1; Morgan 1-0; Nicasio 2-0; Vargas 8-3; Lugo, S 3-2; Zamora 0-0; Gsellman 1-1; Rhame 0-0.
    Batters faced: Velasquez 22; Neshek 4; Domínguez 3; Morgan 4; Nicasio 3; Vargas 21; Lugo, S 8; Zamora; Gsellman 8; Rhame 6.
    Inherited runners-scored: Lugo, S 2-0; Zamora 1-0.
    Umpires: HP: Brian Gorman. 1B: Jansen Visconti. 2B: Mark Carlson. 3B: Scott Barry.
    Weather: 66 degrees, Clear.
    Wind: 12 mph, L To R.
    First pitch: 7:11 PM.
    T: 3:21.
    Att: 27,685.
    Venue: Citi Field.
    April 24, 2019
    -----------------------------------------------------------------------------------------------------------------------------------------------------------------

    Which sections are included can be customized using the battingBox, battingInfo, pitchingBox, and gameInfo parameters
    All default to True; set to False to exclude from the results
    For example, to retrieve only the batting box: statsapi.boxscore(565997,battingInfo=False,fieldingInfo=False,pitchingBox=False,gameInfo=False)
    """

    rowLen = 79
    """rowLen is the total width of each side of the box score, excluding the " | " separator"""
    fullRowLen = rowLen * 2 + 3
    """fullRowLen is the full table width"""
    boxscore = ''
    """boxscore will hold the string to be returned"""
    params = {'gamePk':gamePk,'fields':'gameData,teams,teamName,shortName,teamStats,batting,atBats,runs,hits,rbi,strikeOuts,baseOnBalls,leftOnBase,pitching,inningsPitched,earnedRuns,homeRuns,players,boxscoreName,liveData,boxscore,teams,players,id,fullName,allPositions,abbreviation,seasonStats,batting,avg,ops,era,battingOrder,info,title,fieldList,note,label,value'}
    if timecode: params.update({'timecode':timecode})
    r = get('game',params)

    teamInfo = r['gameData']['teams']
    playerInfo = r['gameData']['players']
    away = r['liveData']['boxscore']['teams']['away']
    home = r['liveData']['boxscore']['teams']['home']

    if battingBox:
        #Add away column headers
        awayBatters = [{'namefield':teamInfo['away']['teamName'] + ' Batters', 'ab':'AB', 'r':'R', 'h':'H', 'rbi':'RBI', 'bb':'BB', 'k':'K', 'lob':'LOB', 'avg':'AVG', 'ops':'OPS'}]
        for batterId_int in [x for x in away['batters'] if away['players']['ID'+str(x)].get('battingOrder')]:
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

        #Add home column headers
        homeBatters = [{'namefield':teamInfo['home']['teamName'] + ' Batters', 'ab':'AB', 'r':'R', 'h':'H', 'rbi':'RBI', 'bb':'BB', 'k':'K', 'lob':'LOB', 'avg':'AVG', 'ops':'OPS'}]
        for batterId_int in [x for x in home['batters'] if home['players']['ID'+str(x)].get('battingOrder')]:
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

        #Make sure the home and away batter lists are the same length
        while len(awayBatters) > len(homeBatters):
            homeBatters.append({'namefield':'','ab':'','r':'','h':'','rbi':'','bb':'','k':'','lob':'','avg':'','ops':''})
        while len(awayBatters) < len(homeBatters):
            awayBatters.append({'namefield':'','ab':'','r':'','h':'','rbi':'','bb':'','k':'','lob':'','avg':'','ops':''})

        #Add away team totals
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
                                'ops':''
                            })
        #Add home team totals
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
                                'ops':''
                            })

        #Build the batting box!
        for i in range(0,len(awayBatters)):
            if i==0 or i==len(awayBatters)-1:
                boxscore += '-'*rowLen + ' | ' + '-'*rowLen + '\n'
            boxscore += '{namefield:<40} {ab:^3} {r:^3} {h:^3} {rbi:^3} {bb:^3} {k:^3} {lob:^3} {avg:^4} {ops:^5} | '.format(**awayBatters[i])
            boxscore += '{namefield:<40} {ab:^3} {r:^3} {h:^3} {rbi:^3} {bb:^3} {k:^3} {lob:^3} {avg:^4} {ops:^5}\n'.format(**homeBatters[i])
            if i==0 or i==len(awayBatters)-1:
                boxscore += '-'*rowLen + ' | ' + '-'*rowLen + '\n'

        #Get batting notes
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

        boxscore += ' '*rowLen + ' | ' + ' '*rowLen + '\n'

    #Get batting and fielding info
    awayBoxInfo = {}
    homeBoxInfo = {}
    for infoType in ['BATTING','FIELDING']:
        if (infoType=='BATTING' and battingInfo) or (infoType=='FIELDING' and fieldingInfo):
            for z in (x for x in away['info'] if x.get('title')==infoType):
                awayBoxInfo.update({len(awayBoxInfo): z['title']})
                for x in z['fieldList']:
                    if len(x['label'] + ': ' + x.get('value','')) > rowLen:
                        words = iter((x['label'] + ': ' + x.get('value','')).split())
                        check = ''
                        lines = []
                        for word in words:
                            if len(check) + 1 + len(word) <= rowLen:
                                if check=='': check = word
                                else: check += ' ' + word
                            else:
                                lines.append(check)
                                check = '    ' + word
                        if len(check): lines.append(check)
                        for i in range(0,len(lines)):
                            awayBoxInfo.update({len(awayBoxInfo): lines[i] })
                            
                    else:
                        awayBoxInfo.update({len(awayBoxInfo): x['label'] + ': ' + x.get('value','') })

            for z in (x for x in home['info'] if x.get('title')==infoType):
                homeBoxInfo.update({len(homeBoxInfo): z['title']})
                for x in z['fieldList']:
                    if len(x['label'] + ': ' + x.get('value','')) > rowLen:
                        words = iter((x['label'] + ': ' + x.get('value','')).split())
                        check = ''
                        lines = []
                        for word in words:
                            if len(check) + 1 + len(word) <= rowLen:
                                if check=='': check = word
                                else: check += ' ' + word
                            else:
                                lines.append(check)
                                check = '    ' + word
                        if len(check): lines.append(check)
                        for i in range(0,len(lines)):
                            homeBoxInfo.update({len(homeBoxInfo): lines[i] })
                    else:
                        homeBoxInfo.update({len(homeBoxInfo): x['label'] + ': ' + x.get('value','') })

            if len(awayBoxInfo) and infoType == 'BATTING':
                awayBoxInfo.update({len(awayBoxInfo) : ' '})
            if len(homeBoxInfo) and infoType == 'BATTING':
                homeBoxInfo.update({len(homeBoxInfo) : ' '})

    if len(awayBoxInfo) > 0:
        while len(awayBoxInfo) > len(homeBoxInfo):
            homeBoxInfo.update({len(homeBoxInfo) : ''})
        while len(awayBoxInfo) < len(homeBoxInfo):
            awayBoxInfo.update({len(awayBoxInfo) : ''})

        #Build info box
        for i in range(0,len(awayBoxInfo)):
            boxscore += ('{:<%s} | '%rowLen).format(awayBoxInfo[i])
            boxscore += ('{:<%s}\n'%rowLen).format(homeBoxInfo[i])
            if i==len(awayBoxInfo)-1:
                boxscore += '-'*rowLen + ' | ' + '-'*rowLen + '\n'

    #Get pitching box
    if pitchingBox:
        #Add away column headers
        awayPitchers = [{'namefield':teamInfo['away']['teamName'] + ' Pitchers', 'ip':'IP', 'h':'H', 'r':'R', 'er':'ER', 'bb':'BB', 'k':'K', 'hr':'HR', 'era':'ERA'}]
        for pitcherId_int in away['pitchers']:
            pitcherId = str(pitcherId_int)
            namefield = playerInfo['ID'+pitcherId]['boxscoreName']
            namefield += '  ' + away['players']['ID'+pitcherId]['stats']['pitching'].get('note','') if away['players']['ID'+pitcherId]['stats']['pitching'].get('note') else ''
            pitcher =    {
                            'namefield':namefield,
                            'ip':str(away['players']['ID'+pitcherId]['stats']['pitching']['inningsPitched']),
                            'h':str(away['players']['ID'+pitcherId]['stats']['pitching']['hits']),
                            'r':str(away['players']['ID'+pitcherId]['stats']['pitching']['runs']),
                            'er':str(away['players']['ID'+pitcherId]['stats']['pitching']['earnedRuns']),
                            'bb':str(away['players']['ID'+pitcherId]['stats']['pitching']['baseOnBalls']),
                            'k':str(away['players']['ID'+pitcherId]['stats']['pitching']['strikeOuts']),
                            'hr':str(away['players']['ID'+pitcherId]['stats']['pitching']['homeRuns']),
                            'era':str(away['players']['ID'+pitcherId]['seasonStats']['pitching']['era'])
                        }
            awayPitchers.append(pitcher)

        #Add home column headers
        homePitchers = [{'namefield':teamInfo['home']['teamName'] + ' Pitchers', 'ip':'IP', 'h':'H', 'r':'R', 'er':'ER', 'bb':'BB', 'k':'K', 'hr':'HR', 'era':'ERA'}]
        for pitcherId_int in home['pitchers']:
            pitcherId = str(pitcherId_int)
            namefield = playerInfo['ID'+pitcherId]['boxscoreName']
            namefield += '  ' + home['players']['ID'+pitcherId]['stats']['pitching'].get('note','') if home['players']['ID'+pitcherId]['stats']['pitching'].get('note') else ''
            pitcher =    {
                            'namefield':namefield,
                            'ip':str(home['players']['ID'+pitcherId]['stats']['pitching']['inningsPitched']),
                            'h':str(home['players']['ID'+pitcherId]['stats']['pitching']['hits']),
                            'r':str(home['players']['ID'+pitcherId]['stats']['pitching']['runs']),
                            'er':str(home['players']['ID'+pitcherId]['stats']['pitching']['earnedRuns']),
                            'bb':str(home['players']['ID'+pitcherId]['stats']['pitching']['baseOnBalls']),
                            'k':str(home['players']['ID'+pitcherId]['stats']['pitching']['strikeOuts']),
                            'hr':str(home['players']['ID'+pitcherId]['stats']['pitching']['homeRuns']),
                            'era':str(home['players']['ID'+pitcherId]['seasonStats']['pitching']['era'])
                        }
            homePitchers.append(pitcher)

        #Make sure the home and away pitcher lists are the same length
        while len(awayPitchers) > len(homePitchers):
            homePitchers.append({'namefield':'','ip':'','h':'','r':'','er':'','bb':'','k':'','hr':'','era':''})
        while len(awayPitchers) < len(homePitchers):
            awayPitchers.append({'namefield':'','ip':'','h':'','r':'','er':'','bb':'','k':'','hr':'','era':''})

        #Get away team totals
        awayPitchers.append  ({
                                'namefield':'Totals',
                                'ip':str(away['teamStats']['pitching']['inningsPitched']),
                                'h':str(away['teamStats']['pitching']['hits']),
                                'r':str(away['teamStats']['pitching']['runs']),
                                'er':str(away['teamStats']['pitching']['earnedRuns']),
                                'bb':str(away['teamStats']['pitching']['baseOnBalls']),
                                'k':str(away['teamStats']['pitching']['strikeOuts']),
                                'hr':str(away['teamStats']['pitching']['homeRuns']),
                                'era':''
                            })

        #Get home team totals
        homePitchers.append  ({
                                'namefield':'Totals',
                                'ip':str(home['teamStats']['pitching']['inningsPitched']),
                                'h':str(home['teamStats']['pitching']['hits']),
                                'r':str(home['teamStats']['pitching']['runs']),
                                'er':str(home['teamStats']['pitching']['earnedRuns']),
                                'bb':str(home['teamStats']['pitching']['baseOnBalls']),
                                'k':str(home['teamStats']['pitching']['strikeOuts']),
                                'hr':str(home['teamStats']['pitching']['homeRuns']),
                                'era':''
                            })

        #Build the pitching box!
        for i in range(0,len(awayPitchers)):
            if i==0 or i==len(awayPitchers)-1:
                boxscore += '-'*rowLen + ' | ' + '-'*rowLen + '\n'
            boxscore += '{namefield:<43} {ip:^4} {h:^3} {r:^3} {er:^3} {bb:^3} {k:^3} {hr:^3} {era:^6} | '.format(**awayPitchers[i])
            boxscore += '{namefield:<43} {ip:^4} {h:^3} {r:^3} {er:^3} {bb:^3} {k:^3} {hr:^3} {era:^6}\n'.format(**homePitchers[i])
            if i==0 or i==len(awayPitchers)-1:
                boxscore += '-'*rowLen + ' | ' + '-'*rowLen + '\n'

    #Get game info
    if gameInfo:
        z = r['liveData']['boxscore'].get('info',[])
        gameBoxInfo = {}
        for x in z:
            if len(x['label'] + (': ' if x.get('value') else '') + x.get('value','')) > fullRowLen:
                words = iter((x['label'] + (': ' if x.get('value') else '') + x.get('value','')).split())
                check = ''
                lines = []
                for word in words:
                    if len(check) + 1 + len(word) <= fullRowLen:
                        if check=='': check = word
                        else: check += ' ' + word
                    else:
                        lines.append(check)
                        check = '    ' + word
                if len(check): lines.append(check)
                for i in range(0,len(lines)):
                    gameBoxInfo.update({len(gameBoxInfo): lines[i] })
                    
            else:
                gameBoxInfo.update({len(gameBoxInfo): x['label'] + (': ' if x.get('value') else '') + x.get('value','') })

        #Build the game info box
        for i in range(0,len(gameBoxInfo)):
            boxscore += ('{:<%s}'%fullRowLen + '\n').format(gameBoxInfo[i])
            if i==len(gameBoxInfo)-1:
                boxscore += '-'*fullRowLen + '\n'
    
    return boxscore

def linescore(gamePk,timecode=None):
    """Get formatted linescore for a given game.

    Note: This function uses the game endpoint instead of game_linescore,
    because game_linescore does not contain the team names or game status
    and it's better to make one call instead of two.

    It is possible to get the linescore as it existed at a specific time by including the timestamp in the timecode parameter.
    The timecode should be in the format YYYYMMDD_HHMMSS, and in the UTC timezone
    For example, 4/24/19 10:32:40 EDT (-4) would be: 20190425_012240
    A list of timestamps for game events can be found through the game_timestamps endpoint:
    statsapi.get('game_timestamps',{'gamePk':565997})

    Example use:

    Print the linescore for the Phillies/Mets game on 4/25:

    print( statsapi.linescore(565997) )

    Output:

    Final    1 2 3 4 5 6 7 8 9  R   H   E
    Phillies 1 0 0 0 0 0 0 3 2  6   10  0
    Mets     0 0 0 0 0 0 0 0 0  0   6   3

    """
    linescore = ''
    params = {'gamePk':gamePk,'fields':'gameData,teams,teamName,shortName,status,abstractGameState,liveData,linescore,innings,num,home,away,runs,hits,errors'}
    if timecode: params.update({'timecode':timecode})
    r = get('game',params)

    header_name = r['gameData']['status']['abstractGameState']
    away_name = r['gameData']['teams']['away']['teamName']
    home_name = r['gameData']['teams']['home']['teamName']
    header_row = []
    away = []
    home = []

    for x in r['liveData']['linescore']['innings']:
        header_row.append(str(x.get('num','')))
        away.append(str(x.get('away',{}).get('runs',0)))
        home.append(str(x.get('home',{}).get('runs',0)))

    if len(r['liveData']['linescore']['innings']) < 9:
        for i in range(len(r['liveData']['linescore']['innings']) + 1, 10):
            header_row.append(str(i))
            away.append(' ')
            home.append(' ')

    header_row.extend(['R','H','E'])
    away.extend([
                    str(r['liveData']['linescore'].get('teams',{}).get('away',{}).get('runs',0)),
                    str(r['liveData']['linescore'].get('teams',{}).get('away',{}).get('hits',0)),
                    str(r['liveData']['linescore'].get('teams',{}).get('away',{}).get('errors',0))
                ])
    home.extend([
                    str(r['liveData']['linescore'].get('teams',{}).get('home',{}).get('runs',0)),
                    str(r['liveData']['linescore'].get('teams',{}).get('home',{}).get('hits',0)),
                    str(r['liveData']['linescore'].get('teams',{}).get('home',{}).get('errors',0))
                ])

    #Build the linescore
    for k in [[header_name,header_row],[away_name,away],[home_name,home]]:
        linescore += ('{:<%s}' % str(len(max([header_name,away_name,home_name],key=len)) + 1)).format(k[0])
        linescore += ('{:^2}' * (len(k[1])-3)).format(*k[1])
        linescore += ('{:^4}' * 3).format(*k[1][-3:])
        linescore += '\n'
    if len(linescore)>1: linescore = linescore[:-1] #strip the extra line break

    return linescore

def last_game(teamId):
    """Get the gamePk for the given team's most recent game.
    Note: Sometimes Stats API will actually return the next game in the previousSchedule hydration
    """
    return get('team',{'teamId':teamId,'hydrate':'previousSchedule','fields':'teams,id,teamName,previousGameSchedule,dates,date,games,gamePk,season,gameDate,teams,away,home,team,name'})['teams'][0]['previousGameSchedule']['dates'][0]['games'][0]['gamePk']

def next_game(teamId):
    """Get the gamePk for the given team's next game.
    Note: Sometimes Stats API will actually return the next game in the previousSchedule hydration
    """
    return get('team',{'teamId':teamId,'hydrate':'nextSchedule','fields':'teams,id,teamName,nextGameSchedule,dates,date,games,gamePk,season,gameDate,teams,away,home,team,name'})['teams'][0]['nextGameSchedule']['dates'][0]['games'][0]['gamePk']

def game_scoring_plays(gamePk):
    """Get a list of scoring plays for a given game

    Example use:

    Print a list of scoring plays from the 4/28/2019 Marlins @ Phillies game

    print( statsapi.game_scoring_plays(567074) )

    Output (truncated to show only the first and last records):

    Rhys Hoskins doubles (6) on a sharp line drive to left fielder Isaac Galloway.   Bryce Harper scores.
    Bottom 1 - Miami Marlins: 0, Philadelphia Phillies: 1

    Rhys Hoskins walks.   Andrew McCutchen scores.    Jean Segura to 3rd.  Wild pitch by pitcher Tayron Guerrero.
    Bottom 8 - Miami Marlins: 1, Philadelphia Phillies: 5
    """
    r = get('schedule',{'sportId':1,'gamePk':gamePk,'hydrate':'scoringplays','fields':'dates,date,games,teams,away,team,name,scoringPlays,result,description,awayScore,homeScore,about,halfInning,inning,endTime'})
    if not len(r['dates'][0]['games'][0]['scoringPlays']): return ''

    items = r['dates'][0]['games'][0]['scoringPlays']
    home_team = r['dates'][0]['games'][0]['teams']['home']['team']['name']
    away_team = r['dates'][0]['games'][0]['teams']['away']['team']['name']

    scoring_plays = ''
    unorderedPlays = {}
    for v in items:
        unorderedPlays.update({v['about']['endTime'] : v})
    sortedPlays = []
    for x in sorted(unorderedPlays):
        sortedPlays.append(unorderedPlays[x])
    for a in sortedPlays:
        scoring_plays += '{}\n{} {} - {}: {}, {}: {}\n\n'.format(a['result']['description'], a['about']['halfInning'][0:1].upper() + a['about']['halfInning'][1:], a['about']['inning'], away_team, a['result']['awayScore'], home_team, a['result']['homeScore'])
    if len(scoring_plays)>1: scoring_plays = scoring_plays[:-2] #strip the extra line break

    return scoring_plays

def game_highlights(gamePk):
    """Get the highlight video links for a given game

    Example use:

    Print the highlight links for the most recent Phillies game

    print( statsapi.game_highlights( statsapi.last_game(143) ) )

    Output (truncated to only include the first two highlights):

    Hoskins' RBI double (00:00:16)
    Rhys Hoskins belts a double off the left-center-field wall to score Bryce Harper and give the Phillies a 1-0 lead in the bottom of the 1st
    https://cuts.diamond.mlb.com/FORGE/2019/2019-04/28/b1117503-3df11d8d-6df0dd65-csvm-diamondx64-asset_1280x720_59_4000K.mp4

    Phanatic has birthday party (00:01:15)
    Kids and fellow mascots were at Citizens Bank Park to celebrate the Phillie Phanatic's birthday before the game against the Marlins
    https://cuts.diamond.mlb.com/FORGE/2019/2019-04/28/7d978385-db13f22d-f68c304f-csvm-diamondx64-asset_1280x720_59_4000K.mp4
    """
    r = get('schedule',{'sportId':1,'gamePk':gamePk,'hydrate':'game(content(highlights(highlights)))','fields':'dates,date,games,gamePk,content,highlights,items,headline,type,value,title,description,duration,playbacks,name,url'})
    if not len(r['dates'][0]['games'][0]['content']['highlights']['highlights']['items']): return ''
    items = r['dates'][0]['games'][0]['content']['highlights']['highlights']['items']

    highlights = ''
    unorderedHighlights = {}
    for v in (x for x in items if isinstance(x,dict) and x['type']=='video'):
        unorderedHighlights.update({v['date'] : v})
    sortedHighlights = []
    for x in sorted(unorderedHighlights):
        sortedHighlights.append(unorderedHighlights[x])
    for a in sortedHighlights:
        #if sum(1 for t in a['keywordsAll'] if t['type']=='team_id') == 1:
        #    highlights += next(t['displayName'] for t in a['keywordsAll'] if t['type']=='team_id') + '\n'
        highlights += '{} ({})\n{}\n{}\n\n'.format(a.get('title',a.get('headline','')), a['duration'], a.get('description',''), next(s['url'] for s in a['playbacks'] if s['name']=='mp4Avc'))

    return highlights

def game_pace(season=datetime.now().year,sportId=1):
    """Get information about pace of game for a given season (back to 1999).

    Example use:

    Print the pace of game stats for 2008, in order to determine the number and average time of extra inning games

    print(statsapi.game_pace(2008))

    Output:

    2008 Game Pace Stats
    hitsPer9Inn: 18.26
    runsPer9Inn: 9.38
    pitchesPer9Inn: 297.72
    plateAppearancesPer9Inn: 77.89
    hitsPerGame: 18.11
    runsPerGame: 9.3
    inningsPlayedPerGame: 8.96
    pitchesPerGame: 295.36
    pitchersPerGame: 7.83
    plateAppearancesPerGame: 77.28
    totalGameTime: 7086:06:00
    totalInningsPlayed: 21748.0
    totalHits: 43972
    totalRuns: 22585
    totalPlateAppearances: 187630
    totalPitchers: 19012
    totalPitches: 717131
    totalGames: 2428
    total9InnGames: 2428
    totalExtraInnGames: 208
    timePerGame: 02:55:07
    timePerPitch: 00:00:36
    timePerHit: 00:09:40
    timePerRun: 00:18:50
    timePerPlateAppearance: 00:02:16
    timePer9Inn: 02:56:30
    timePer77PlateAppearances: 02:54:29
    totalExtraInnTime: 775:10:00
    timePer7InnGameWithoutExtraInn: 00:00:00
    total9InnGamesCompletedEarly: 3
    total9InnGamesWithoutExtraInn: 2217
    total9InnGamesScheduled: 2428
    hitsPerRun: 1.947
    pitchesPerPitcher: 37.72
    total7InnGames: 3
    total9InnGames: 2217
    totalExtraInnGames: 208
    timePer7InnGame: 01:54:40
    timePer9InnGame: 02:50:38
    timePerExtraInnGame: 03:43:36
    """
    params = {}
    if season: params.update({'season':season})
    if sportId: params.update({'sportId':sportId})

    r = get('gamePace',params)

    if not len(r['sports']):
        raise ValueError('No game pace info found for the {} season. Game pace data appears to begin in 1999.'.format(season))

    pace = ''

    pace += '{} Game Pace Stats\n'.format(season)
    for s in r['sports']:
        for k in s.keys():
            if k in ['season','sport']: continue
            if k == 'prPortalCalculatedFields':
                for x in s[k].keys():
                    pace += '{}: {}\n'.format(x,s[k][x])
            else: pace += '{}: {}\n'.format(k,s[k])

    return pace

def player_stats(personId,group='[hitting,pitching,fielding]',type='season'):
    """Get current season or career stats for a given player.

    For group use 'hitting', 'pitching', or 'fielding'.
    Include multiple groups in the following format (this is a string, not actually a list):
    group='[hitting,pitching]'

    For type use 'career' or 'season'.
    Include multiple types in the following format (this is a string, not actually a list):
    group='[career,season]'

    Example use:

    Print Chase Utley's career hitting stats (using sports_players endpoint to look up person id)

    print( statsapi.player_stats(next(x['id'] for x in statsapi.get('sports_players',{'season':2008,'gameType':'W'})['people'] if x['fullName']=='Chase Utley'), 'hitting', 'career') )

    Output:

    Chase "Silver Fox" Utley, 2B (2003-2018)

    Career Hitting
    gamesPlayed: 1937
    groundOuts: 1792
    runs: 1103
    doubles: 411
    triples: 58
    homeRuns: 259
    strikeOuts: 1193
    baseOnBalls: 724
    intentionalWalks: 62
    hits: 1885
    hitByPitch: 204
    avg: .275
    atBats: 6857
    obp: .358
    slg: .465
    ops: .823
    caughtStealing: 22
    stolenBases: 154
    groundIntoDoublePlay: 93
    numberOfPitches: 31043
    plateAppearances: 7863
    totalBases: 3189
    rbi: 1025
    leftOnBase: 2780
    sacBunts: 6
    sacFlies: 72
    babip: .297
    groundOutsToAirouts: 0.84
    """
    params = {'personId':personId,'hydrate':'stats(group='+group+',type='+type+'),currentTeam'}
    r = get('person',params)

    stats = ''
    stat_groups = []

    bio =   {
                'id' : r['people'][0]['id'],
                'first_name' : r['people'][0]['useName'],
                'last_name' : r['people'][0]['lastName'],
                'active' : r['people'][0]['active'],
                'current_team' : r['people'][0]['currentTeam']['name'],
                'position' : r['people'][0]['primaryPosition']['abbreviation'],
                'nickname' : r['people'][0].get('nickName'),
                'active' : r['people'][0]['active'],
                'last_played' : r['people'][0].get('lastPlayedDate'),
                'mlb_debut' : r['people'][0]['mlbDebutDate'],
                'bat_side' : r['people'][0]['batSide']['description'],
                'pitch_hand' : r['people'][0]['pitchHand']['description']
            }

    for s in r['people'][0].get('stats',[]):
        for i in range(0,len(s['splits'])):
            stat_group =    {
                                'type' : s['type']['displayName'],
                                'group' : s['group']['displayName'],
                                'stats' : s['splits'][i]['stat']
                            }
            stat_groups.append(stat_group)

    if len(stat_groups)==0:
        raise ValueError('No stats found for given player, type, and group.')

    stats += bio['first_name']
    if bio['nickname']: stats += ' "{nickname}"'.format(**bio)
    stats += ' {last_name}, {position} ({mlb_debut:.4}-'.format(**bio)
    if not bio['active']: stats += '{last_played:.4}'.format(**bio)
    stats += ')\n\n'

    for x in stat_groups:
        stats += x['type'][0:1].upper() + x['type'][1:] + ' ' + x['group'][0:1].upper() + x['group'][1:]
        if x['stats'].get('position'): stats += ' ({})'.format(x['stats']['position']['abbreviation'])
        stats += '\n'
        for y in x['stats'].keys():
            if y=='position': continue
            stats += '{}: {}\n'.format(y,x['stats'][y])
        stats += '\n'

    return stats

def lookup_player(lookup_value,gameType='R',season=datetime.now().year,sportId=1):
    """Get data about players based on first, last, or full name.

    Example use:

    Look up player id for Aaron Nola
    Note: if using a full last name as the lookup_value and that last name could be part of another player's lastname,
    e.g. 'Nola' is part of 'Nolan', include a comma on the end of the last name in order to match on the 'initLastName'
    field which looks like 'Nola, A'

    player = statsapi.lookup_player('nola,')
    print(player[0]['id']) #assume only 1 record returned for demo purposes

    Output:

    605400


    Print full name and position for all players named Harper

    for player in statsapi.lookup_player('Harper'):
        print('Full name: {}, Position: {}'.format(player['fullName'], player['primaryPosition']['abbreviation']))

    Output:

    Full name: Bryce Harper, Position: RF
    Full name: Ryne Harper, Position: P
    """
    params = {'gameType':gameType, 'season':season, 'sportId':sportId, 'fields':'people,id,fullName,firstName,lastName,primaryNumber,currentTeam,id,primaryPosition,code,abbreviation,useName,boxscoreName,nickName,mlbDebutDate,nameFirstLast,firstLastName,lastFirstName,lastInitName,initLastName,fullFMLName,fullLFMName'}
    r = get('sports_players',params)

    players = []
    for player in r['people']:
        for v in player.values():
            if str(lookup_value).lower() in str(v).lower():
                players.append(player)
                break

    return players

def lookup_team(lookup_value,activeStatus='Y',season=datetime.now().year,sportIds=1):
    """Get a info about a team based on the team name, city, abbreviation, or file code.

    Values for activeStatus: Y, N, B (Both)

    Return value will be a list of teams matching the lookup_value. 
    If no matches are found, an empty list will be returned.

    Example use:

    Get teamId for team with code cwa

    team = statsapi.lookup_team('chn')
    print(team[0]['id']) #assume only 1 record returned for demo purposes

    Output:

    112


    Get info about all teams from NY

    for team in statsapi.lookup_team('ny'):
        print(team)

    Output:

    {'id': 147, 'name': 'New York Yankees', 'teamCode': 'nya', 'fileCode': 'nyy', 'teamName': 'Yankees', 'locationName': 'Bronx', 'shortName': 'NY Yankees'}
    {'id': 121, 'name': 'New York Mets', 'teamCode': 'nyn', 'fileCode': 'nym', 'teamName': 'Mets', 'locationName': 'New York', 'shortName': 'NY Mets'}
    """
    params = {'activeStatus':activeStatus, 'season':season, 'sportIds':sportIds, 'fields':'teams,id,name,teamCode,fileCode,teamName,locationName,shortName'}
    r = get('teams',params)

    teams = []
    for team in r['teams']:
        for v in team.values():
            if str(lookup_value).lower() in str(v).lower():
                teams.append(team)
                break
    return teams

def team_leaders(teamId,leaderCategories,season=datetime.now().year,leaderGameTypes='R',limit=10):
    """Get stat leaders for a given team.

    Get a list of available leaderCategories by calling the meta endpoint with type=leagueLeaderTypes

    Example use:

    Print the top 5 team leaders in walks for the 2008 Phillies

    print(statsapi.team_leaders(143,'walks',limit=5,season=2008))

    Output:

    Rank Name                 Value
     1   Pat Burrell           102
     2   Ryan Howard           81
     3   Chase Utley           64
     4   Jimmy Rollins         58
     5   Jayson Werth          57
    """
    params = {'leaderCategories':leaderCategories,'season':season,'teamId':teamId,'leaderGameTypes':leaderGameTypes,'limit':limit}
    params.update({'fields' : 'teamLeaders,leaders,rank,value,person,fullName'})

    r = get('team_leaders',params)

    leaders = ''
    lines = []
    for player in [x for x in r['teamLeaders'][0]['leaders']]:
        lines.append([player['rank'],player['person']['fullName'],player['value']])

    leaders += '{:<4} {:<20} {:<5}\n'.format(*['Rank','Name','Value'])
    for a in lines:
        leaders += '{:^4} {:<20} {:^5}\n'.format(*a)

    return leaders

def league_leaders(leaderCategories,season=None,limit=10,statGroup=None,leagueId=None,gameTypes=None,playerPool=None,sportId=1):
    """Get stat leaders overall or for a given league (103=AL, 104=NL).

    Get a list of available leaderCategories by calling the meta endpoint with type=leagueLeaderTypes

    Get a list of available statGroups by calling the meta endpoint with type=statGroups
    Note that excluding statGroup may return unexpected results. For example leaderCategories='earnedRunAverage'
    will return different results with statGroup='pitching' and statGroup='catching'.

    Get a list of available gameTypes by calling the meta endpoint with type=gameTypes

    Available playerPool values: ['all','qualified','rookies'] (default is qualified)

    Example use:

    Print a list of the top 10 pitchers by earned run average

    print( statsapi.league_leaders('earnedRunAverage',statGroup='pitching',limit=10) )

    Output:

    Rank Name                 Team                   Value
     1   Luis Castillo        Cincinnati Reds        1.23
     2   Marcus Stroman       Toronto Blue Jays      1.43
     3   Matt Shoemaker       Toronto Blue Jays      1.57
     4   Chris Paddack        San Diego Padres       1.67
     5   Tyler Glasnow        Tampa Bay Rays         1.75
     6   Trevor Bauer         Cleveland Indians      1.99
     7   Joe Musgrove         Pittsburgh Pirates     2.06
     8   Caleb Smith          Miami Marlins          2.17
     9   Max Fried            Atlanta Braves         2.30
     10  Aaron Sanchez        Toronto Blue Jays      2.32


    Print a list of the top 5 batters by OPS

    print( statsapi.league_leaders('onBasePlusSlugging',statGroup='hitting',limit=5) )

    Output:

    Rank Name                 Team                   Value
     1   Cody Bellinger       Los Angeles Dodgers    1.390
     2   Christian Yelich     Milwaukee Brewers      1.264
     3   Anthony Rendon       Washington Nationals   1.182
     4   Hunter Dozier        Kansas City Royals     1.143
     5   Pete Alonso          New York Mets          1.082


    Print a list of the 10 American League players with the most errors in 2017

    print( statsapi.league_leaders('errors',statGroup='fielding',limit=10,season=2017,leagueId=103) )

    Output:

    Rank Name                 Team                   Value
     1   Tim Anderson         Chicago White Sox       28
     2   Rougned Odor         Texas Rangers           19
     3   Tim Beckham          Baltimore Orioles       18
     3   Nicholas Castellanos Detroit Tigers          18
     3   Jorge Polanco        Minnesota Twins         18
     6   Elvis Andrus         Texas Rangers           17
     6   Xander Bogaerts      Boston Red Sox          17
     6   Jean Segura          Seattle Mariners        17
     9   Alcides Escobar      Kansas City Royals      15
     9   Jonathan Schoop      Baltimore Orioles       15


    Print a list of top 10 all time single season leader in triples

    print( statsapi.league_leaders('triples',statGroup='hitting',limit=10,sportId=1) )

    Rank Name                 Team                    Value
     1   Chief Wilson         Pittsburgh Pirates       36
     2   Jimmy Williams       Pittsburgh Pirates       27
     3   Sam Crawford         Detroit Tigers           26
     3   Kiki Cuyler          Pittsburgh Pirates       26
     3   Joe Jackson          Cleveland Naps           26
     6   Sam Crawford         Detroit Tigers           25
     6   Larry Doyle          New York Giants          25
     6   Buck Freeman         Washington Senators      25
     6   Tom Long             St. Louis Cardinals      25
     10  Ty Cobb              Detroit Tigers           24
     10  Ty Cobb              Detroit Tigers           24
    """
    params = {'leaderCategories':leaderCategories,'sportId':sportId,'limit':limit}
    if season: params.update({'season':season})
    else: params.update({'statType':'statsSingleSeason'}) #won't get any results for all-time leaders unless type is single season
    if statGroup:
        if statGroup == 'batting': statGroup = 'hitting'
        params.update({'statGroup':statGroup})
    if gameTypes: params.update({'leaderGameTypes':gameTypes})
    if leagueId: params.update({'leagueId':leagueId})
    if playerPool: params.update({'playerPool':playerPool})
    params.update({'fields' : 'leagueLeaders,leaders,rank,value,team,name,league,name,person,fullName'})

    r = get('stats_leaders',params)

    leaders = ''
    lines = []
    for player in [x for x in r['leagueLeaders'][0]['leaders']]:
        lines.append([player['rank'],player['person']['fullName'],player['team'].get('name',''),player['value']])

    leaders += '{:<4} {:<20} {:<23} {:<5}\n'.format(*['Rank','Name','Team','Value'])
    for a in lines:
        leaders += '{:^4} {:<20} {:<23} {:^5}\n'.format(*a)

    return leaders

def standings(leagueId='103,104',division='all',include_wildcard=True,season=None,standingsTypes=None,date=None):
    """Get formatted standings for a given league/division and season.

    Using both leagueId and divisionId is fine, as long as the division belongs to the specified league

    Return value will be a formatted table including division and wildcard standings, unless include_wildcard=False
    
    Format for date = 'MM/DD/YYYY', e.g. '04/24/2019'

    Example use:

    Print National League standings from 09/27/2008
    
    print( statsapi.standings(leagueId=104,date='09/27/2008') )

    Output:

    National League Central
    Rank Team                   W   L   GB  (E#) WC Rank WC GB (E#)
     1   Chicago Cubs          97  63   -    -      -      -    -
     2   Milwaukee Brewers     89  72  8.5   E      1      -    -
     3   Houston Astros        85  75  12.0  E      3     3.5   E
     4   St. Louis Cardinals   85  76  12.5  E      4     4.0   E
     5   Cincinnati Reds       74  87  23.5  E      7    15.0   E
     6   Pittsburgh Pirates    66  95  31.5  E     11    23.0   E

    National League West
    Rank Team                   W   L   GB  (E#) WC Rank WC GB (E#)
     1   Los Angeles Dodgers   84  77   -    -      -      -    -
     2   Arizona Diamondbacks  81  80  3.0   E      6     8.0   E
     3   Colorado Rockies      74  87  10.0  E      8    15.0   E
     4   San Francisco Giants  71  90  13.0  E     10    18.0   E
     5   San Diego Padres      63  98  21.0  E     12    26.0   E

    National League East
    Rank Team                   W   L   GB  (E#) WC Rank WC GB (E#)
     1   Philadelphia Phillies 91  70   -    -      -      -    -
     2   New York Mets         89  72  2.0   E      2      -    -
     3   Florida Marlins       83  77  7.5   E      5     5.5   E
     4   Atlanta Braves        72  89  19.0  E      9    17.0   E
     5   Washington Nationals  59  101 31.5  E     13    29.5   E
    
    """
    params = {'leagueId':leagueId}
    if date: params.update({'date':date})
    if not season:
        if date:
            season = date[-4:]
        else:
            season = datetime.now().year
    if not standingsTypes: standingsTypes = 'regularSeason'
    params.update({'season':season,'standingsTypes':standingsTypes})
    params.update({'hydrate':'team(division)','fields':'records,standingsType,teamRecords,team,name,division,id,nameShort,abbreviation,divisionRank,gamesBack,wildCardRank,wildCardGamesBack,wildCardEliminationNumber,divisionGamesBack,clinched,eliminationNumber,winningPercentage,type,wins,losses'})

    r = get('standings',params)

    standings = ''
    divisions = {}

    for y in r['records']:
        for x in (x for x in y['teamRecords'] if division.lower()=='all' or division.lower()==x['team']['division']['abbreviation'].lower()):
            if x['team']['division']['id'] not in divisions.keys():
                divisions.update({x['team']['division']['id']:{'div_name':x['team']['division']['name'],'teams':[]}})
            team =  {
                        'name' : x['team']['name'],
                        'div_rank' : x['divisionRank'],
                        'w' : x['wins'],
                        'l' : x['losses'],
                        'gb' : x['gamesBack'],
                        'wc_rank' : x.get('wildCardRank','-'),
                        'wc_gb' : x.get('wildCardGamesBack','-'),
                        'wc_elim_num' : x.get('wildCardEliminationNumber','-'),
                        'elim_num' : x['eliminationNumber']
                    }
            divisions[x['team']['division']['id']]['teams'].append(team)

    for div_id,div in divisions.items():
        standings += div['div_name'] + '\n'
        if include_wildcard:
            standings += '{:^4} {:<21} {:^3} {:^3} {:^4} {:^4} {:^7} {:^5} {:^4}\n'.format(*['Rank','Team','W','L','GB','(E#)','WC Rank','WC GB','(E#)'])
            for t in div['teams']:
                standings += '{div_rank:^4} {name:<21} {w:^3} {l:^3} {gb:^4} {elim_num:^4} {wc_rank:^7} {wc_gb:^5} {wc_elim_num:^4}\n'.format(**t)
        else:
            standings += '{:^4} {:<21} {:^3} {:^3} {:^4} {:^4}\n'.format(*['Rank','Team','W','L','GB','(E#)'])
            for t in div['teams']:
                standings += '{div_rank:^4} {name:<21} {w:^3} {l:^3} {gb:^4} {elim_num:^4}\n'.format(**t)
        standings += '\n'

    return standings

def roster(teamId,rosterType=None,season=datetime.now().year,date=None):
    """Get the roster for a given team.
    Get a list of available rosterTypes by calling the meta endpoint with type=rosterTypes.
    Default rosterType=active
    Format for date = 'MM/DD/YYYY', e.g. '04/24/2019'

    Example use:
    
    Print the current Phillies active roster:

    print( statsapi.roster(143) )

    Output:

    #23  CF  Aaron Altherr
    #27  P   Aaron Nola
    #46  P   Adam Morgan
    #15  C   Andrew Knapp
    #22  RF  Andrew McCutchen
    #3   RF  Bryce Harper
    #16  2B  Cesar Hernandez
    #25  RF  Dylan Cozens
    #61  P   Edubray Ramos
    #51  P   Enyel De Los Santos
    #50  P   Hector Neris
    #10  C   J.T. Realmuto
    #49  P   Jake Arrieta
    #48  P   Jerad Eickhoff
    #52  P   Jose Alvarez
    #12  P   Juan Nicasio
    #7   3B  Maikel Franco
    #5   RF  Nick Williams
    #93  P   Pat Neshek
    #9   2B  Phil Gosselin
    #17  1B  Rhys Hoskins
    #13  2B  Sean Rodriguez
    #58  P   Seranthony Dominguez
    #21  P   Vince Velasquez
    #56  P   Zach Eflin
    """
    if not rosterType: rosterType='active'
    params = {'rosterType':rosterType,'season':season,'teamId':teamId}
    if date: params.update({'date':date})

    r = get('team_roster',params)

    roster = ''
    players = []
    for x in r['roster']:
        players.append([x['jerseyNumber'],x['position']['abbreviation'],x['person']['fullName']])

    for i in range(0,len(players)):
        roster += ('#{:<3} {:<3} {}\n').format(*players[i])

    return roster

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

def get(endpoint,params,force=False):
    """Call MLB StatsAPI and return JSON data.

    This function is for advanced querying of the MLB StatsAPI, 
    and is used by the functions in this library.

    endpoint is one of the keys in the ENDPOINT dict
    params is a dict of parameters, as defined in the ENDPOINT dict for each endpoint

    force=True will force unrecognized parameters into the query string, and ignore parameter requirements
    Please note results from Stats API may not be as expected when forcing.

    statsapi.get('team',{'teamId':143}) will call the team endpoint for teamId=143 (Phillies)

    return value will be the raw response from MLB Stats API in json format
    """

    #Lookup endpoint from input parameter
    ep = ENDPOINTS.get(endpoint)
    if not ep: raise ValueError('Invalid endpoint ('+str(endpoint)+').')
    url = ep['url']
    if DEBUG: print("URL:",url) #debug

    path_params = {}
    query_params = {}

    #Parse parameters into path and query parameters, and discard invalid parameters
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
            if force:
                if DEBUG: print("Found invalid param, forcing into query parameters per force flag:",p) #debug
                query_params.update({p: str(pv)})
            else:
                if DEBUG: print("Found invalid param, ignoring:",p) #debug

    if DEBUG: print ("path_params:",path_params) #debug
    if DEBUG: print ("query_params:",query_params) #debug

    #Replace path parameters with their values
    for k,v in path_params.items():
        if DEBUG: print("Replacing {%s}" % k) #debug
        url = url.replace('{'+k+'}',v)
        if DEBUG: print("URL:",url) #debug
    while url.find('{') != -1 and url.find('}') > url.find('{'):
        param = url[url.find('{')+1:url.find('}')]
        if ep.get('path_params',{}).get(param,{}).get('required'): 
            if ep['path_params'][param]['default'] and ep['path_params'][param]['default'] != '':
                if DEBUG: print("Replacing {%s} with default: %s." % (param, ep['path_params'][param]['default'])) #debug
                url = url.replace('{'+param+'}',ep['path_params'][param]['default'])
            else:
                if force:
                    if DEBUG: print('Missing required path parameter {'+str(param)+'}, proceeding anyway per force flag...')
                else:
                    raise ValueError('Missing required path parameter {'+str(param)+'}')
        else:
            if DEBUG: print("Removing optional param {%s}" % param) #debug
            url = url.replace('{'+param+'}','')
        if DEBUG: print("URL:",url) #debug
    #Add query parameters to the URL
    if len(query_params) > 0:
        for k,v in query_params.items():
            if DEBUG: print("Adding query parameter %s=%s" % (k,v))
            sep = '?' if url.find('?') == -1 else '&'
            url += sep + k + "=" + v
            if DEBUG: print("URL:",url) #debug

    #Make sure required parameters are present
    satisfied = False
    missing_params = []
    for x in ep.get('required_params',[]):
        if len(x) == 0: satisfied = True
        else:
            missing_params.extend([a for a in x if a not in query_params])
            if len(missing_params) == 0:
                satisfied = True
                break
    if not satisfied and not force:
        if ep.get('note'):
            note = '\n--Endpoint note: ' + ep.get('note')
        else: note = ''
        raise ValueError("Missing required parameter(s): " + ', '.join(missing_params) + ".\n--Required parameters for the " + endpoint + " endpoint: " + str(ep.get('required_params',[])) + ". \n--Note: If there are multiple sets in the required parameter list, you can choose any of the sets."+note)

    #Make the request
    r = requests.get(url)
    if r.status_code not in [200,201]:
        raise ValueError('Request failed. Status Code: ' + str(r.status_code) + '.')
    else:
        return r.json()

    return None
