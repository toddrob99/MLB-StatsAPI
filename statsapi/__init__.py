from . import version
__version__ = version.VERSION

import requests

BASE_URL = 'https://statsapi.mlb.com/api/'
ENDPOINTS = {
                'attendance':                   {
                                                    'url': BASE_URL + '{ver}/attendance',
                                                    'path_params':  {
                                                                        'ver':  {
                                                                                    'type': 'str',
                                                                                    'default': 'v1',
                                                                                    'leading_slash': False,
                                                                                    'trailing_slash': False,
                                                                                    'required': True
                                                                                }
                                                                    },
                                                    'query_params': ['teamId','leagueId','season','date','leagueListId','gameType','fields']
                                                },
                'awards':                       {
                                                    'url': BASE_URL + '{ver}/awards{awardId}{recipients}',
                                                    'path_params':  {
                                                                        'ver':  {
                                                                                    'type': 'str',
                                                                                    'default': 'v1',
                                                                                    'leading_slash': False,
                                                                                    'trailing_slash': False,
                                                                                    'required': True
                                                                                },
                                                                        'awardId':  {
                                                                                    'type': 'str',
                                                                                    'default': None,
                                                                                    'leading_slash': True,
                                                                                    'trailing_slash': False,
                                                                                    'required': False
                                                                                },
                                                                        'recipients':  {
                                                                                    'type': 'bool',
                                                                                    'default': True,
                                                                                    'True': '/recipients',
                                                                                    'False': '',
                                                                                    'leading_slash': False,
                                                                                    'trailing_slash': False,
                                                                                    'required': False
                                                                                }
                                                                    },
                                                    'query_params': ['sportId','leagueId','season','hydrate','fields']
                                                },
                'conference':                   {
                                                    'url': BASE_URL + '{ver}/conferences',
                                                    'path_params':  {
                                                                        'ver':  {
                                                                                    'type': 'str',
                                                                                    'default': 'v1',
                                                                                    'leading_slash': False,
                                                                                    'trailing_slash': False,
                                                                                    'required': True
                                                                                }
                                                                    },
                                                    'query_params': ['conferenceId','season','fields']
                                                },
                'division':                     {
                                                    'url': BASE_URL + '{ver}/divisions',
                                                    'path_params':  {
                                                                        'ver':  {
                                                                                    'type': 'str',
                                                                                    'default': 'v1',
                                                                                    'leading_slash': False,
                                                                                    'trailing_slash': False,
                                                                                    'required': True
                                                                                }
                                                                    },
                                                    'query_params': ['divisionId','leagueId','sportId']
                                                },
                'draft':                        {
                                                    'url': BASE_URL + '{ver}/draft{prospects}{year}{latest}',
                                                    'path_params':  {
                                                                        'ver':  {
                                                                                    'type': 'str',
                                                                                    'default': 'v1',
                                                                                    'leading_slash': False,
                                                                                    'trailing_slash': False,
                                                                                    'required': True
                                                                                },
                                                                        'prospects':    {
                                                                                    'type': 'bool',
                                                                                    'default': False,
                                                                                    'True': '/prospects',
                                                                                    'False': '',
                                                                                    'leading_slash': False,
                                                                                    'trailing_slash': False,
                                                                                    'required': False
                                                                                },
                                                                        'year':    {
                                                                                    'type': 'str',
                                                                                    'default': '2019', #TODO: current year or most recent draft year
                                                                                    'leading_slash': True,
                                                                                    'trailing_slash': False,
                                                                                    'required': True
                                                                                },
                                                                        'latest':    {
                                                                                    'type': 'bool',
                                                                                    'default': False,
                                                                                    'True': '/latest',
                                                                                    'False': '',
                                                                                    'leading_slash': False,
                                                                                    'trailing_slash': False,
                                                                                    'required': False
                                                                                },
                                                                    },
                                                    'query_params': ['limit','fields','round','name','school','state','country','position','teamId','playerId','bisPlayerId'],
                                                    'note': 'No query parameters are honored when "latest" endpoint is queried. Prospects and Latest cannot be used together.'
                                                },
                'game':                         {
                                                    'url': BASE_URL + '{ver}/game/{gamePk}/feed/live',
                                                    'path_params':  {
                                                                        'ver':  {
                                                                                    'type': 'str',
                                                                                    'default': 'v1.1',
                                                                                    'leading_slash': False,
                                                                                    'trailing_slash': False,
                                                                                    'required': True
                                                                                },
                                                                        'gamePk': {
                                                                                    'type': 'str',
                                                                                    'default': '',
                                                                                    'leading_slash': False,
                                                                                    'trailing_slash': False,
                                                                                    'required': True
                                                                                }
                                                                    },
                                                    'query_params': ['timecode','hydrate','fields']
                                                },
                'game_diff':                    {
                                                    'url': BASE_URL + '{ver}/game/{gamePk}/feed/live/diffPatch',
                                                    'path_params':  {
                                                                        'ver':  {
                                                                                    'type': 'str',
                                                                                    'default': 'v1.1',
                                                                                    'leading_slash': False,
                                                                                    'trailing_slash': False,
                                                                                    'required': True
                                                                                },
                                                                        'gamePk': {
                                                                                    'type': 'str',
                                                                                    'default': '',
                                                                                    'leading_slash': False,
                                                                                    'trailing_slash': False,
                                                                                    'required': True
                                                                                }
                                                                    },
                                                    'query_params': ['startTimecode','endTimecode']
                                                },
                'game_timestamps':              {
                                                    'url': BASE_URL + '{ver}/game/{gamePk}/feed/live/timestamps',
                                                    'path_params':  {
                                                                        'ver':  {
                                                                                    'type': 'str',
                                                                                    'default': 'v1.1',
                                                                                    'leading_slash': False,
                                                                                    'trailing_slash': False,
                                                                                    'required': True
                                                                                },
                                                                        'gamePk': {
                                                                                    'type': 'str',
                                                                                    'default': '',
                                                                                    'leading_slash': False,
                                                                                    'trailing_slash': False,
                                                                                    'required': True
                                                                                }
                                                                    },
                                                    'query_params': []
                                                },
                'game_changes':                 {
                                                    'url': BASE_URL + '{ver}/game/changes',
                                                    'path_params':  {
                                                                        'ver':  {
                                                                                    'type': 'str',
                                                                                    'default': 'v1',
                                                                                    'leading_slash': False,
                                                                                    'trailing_slash': False,
                                                                                    'required': True
                                                                                }
                                                                    },
                                                    'query_params': ['updatedSince','sportId','gameType','season','fields']
                                                },
                'game_contextMetrics':          {
                                                    'url': BASE_URL + '{ver}/game/{gamePk}/contextMetrics',
                                                    'path_params':  {
                                                                        'ver':  {
                                                                                    'type': 'str',
                                                                                    'default': 'v1',
                                                                                    'leading_slash': False,
                                                                                    'trailing_slash': False,
                                                                                    'required': True
                                                                                },
                                                                        'gamePk': {
                                                                                    'type': 'str',
                                                                                    'default': '',
                                                                                    'leading_slash': False,
                                                                                    'trailing_slash': False,
                                                                                    'required': True
                                                                                }
                                                                    },
                                                    'query_params': ['timecode','fields']
                                                },
                'game_winProbability':          {
                                                    'url': BASE_URL + '{ver}/game/{gamePk}/winProbability',
                                                    'path_params':  {
                                                                        'ver':  {
                                                                                    'type': 'str',
                                                                                    'default': 'v1',
                                                                                    'leading_slash': False,
                                                                                    'trailing_slash': False,
                                                                                    'required': True
                                                                                },
                                                                        'gamePk': {
                                                                                    'type': 'str',
                                                                                    'default': '',
                                                                                    'leading_slash': False,
                                                                                    'trailing_slash': False,
                                                                                    'required': True
                                                                                }
                                                                    },
                                                    'query_params': ['timecode','fields']
                                                },
                'game_boxscore':                {
                                                    'url': BASE_URL + '{ver}/game/{gamePk}/boxscore',
                                                    'path_params':  {
                                                                        'ver':  {
                                                                                    'type': 'str',
                                                                                    'default': 'v1',
                                                                                    'leading_slash': False,
                                                                                    'trailing_slash': False,
                                                                                    'required': True
                                                                                },
                                                                        'gamePk': {
                                                                                    'type': 'str',
                                                                                    'default': '',
                                                                                    'leading_slash': False,
                                                                                    'trailing_slash': False,
                                                                                    'required': True
                                                                                }
                                                                    },
                                                    'query_params': ['timecode','fields']
                                                },
                'game_content':                 {
                                                    'url': BASE_URL + '{ver}/game/{gamePk}/content',
                                                    'path_params':  {
                                                                        'ver':  {
                                                                                    'type': 'str',
                                                                                    'default': 'v1',
                                                                                    'leading_slash': False,
                                                                                    'trailing_slash': False,
                                                                                    'required': True
                                                                                },
                                                                        'gamePk': {
                                                                                    'type': 'str',
                                                                                    'default': '',
                                                                                    'leading_slash': False,
                                                                                    'trailing_slash': False,
                                                                                    'required': True
                                                                                }
                                                                    },
                                                    'query_params': ['highlightLimit']
                                                },
                'game_color':                   {
                                                    'url': BASE_URL + '{ver}/game/{gamePk}/feed/color',
                                                    'path_params':  {
                                                                        'ver':  {
                                                                                    'type': 'str',
                                                                                    'default': 'v1',
                                                                                    'leading_slash': False,
                                                                                    'trailing_slash': False,
                                                                                    'required': True
                                                                                },
                                                                        'gamePk': {
                                                                                    'type': 'str',
                                                                                    'default': '',
                                                                                    'leading_slash': False,
                                                                                    'trailing_slash': False,
                                                                                    'required': True
                                                                                }
                                                                    },
                                                    'query_params': ['timecode','fields']
                                                },
                'game_color_diff':              {
                                                    'url': BASE_URL + '{ver}/game/{gamePk}/feed/color/diffPatch',
                                                    'path_params':  {
                                                                        'ver':  {
                                                                                    'type': 'str',
                                                                                    'default': 'v1',
                                                                                    'leading_slash': False,
                                                                                    'trailing_slash': False,
                                                                                    'required': True
                                                                                },
                                                                        'gamePk': {
                                                                                    'type': 'str',
                                                                                    'default': '',
                                                                                    'leading_slash': False,
                                                                                    'trailing_slash': False,
                                                                                    'required': True
                                                                                }
                                                                    },
                                                    'query_params': ['startTimecode','endTimecode']
                                                },
                'game_color_timestamps':        {
                                                    'url': BASE_URL + '{ver}/game/{gamePk}/feed/color/timestamps',
                                                    'path_params':  {
                                                                        'ver':  {
                                                                                    'type': 'str',
                                                                                    'default': 'v1',
                                                                                    'leading_slash': False,
                                                                                    'trailing_slash': False,
                                                                                    'required': True
                                                                                },
                                                                        'gamePk': {
                                                                                    'type': 'str',
                                                                                    'default': '',
                                                                                    'leading_slash': False,
                                                                                    'trailing_slash': False,
                                                                                    'required': True
                                                                                }
                                                                    },
                                                    'query_params': []
                                                },
                'game_linescore':               {
                                                    'url': BASE_URL + '{ver}/game/{gamePk}/linescore',
                                                    'path_params':  {
                                                                        'ver':  {
                                                                                    'type': 'str',
                                                                                    'default': 'v1',
                                                                                    'leading_slash': False,
                                                                                    'trailing_slash': False,
                                                                                    'required': True
                                                                                },
                                                                        'gamePk': {
                                                                                    'type': 'str',
                                                                                    'default': '',
                                                                                    'leading_slash': False,
                                                                                    'trailing_slash': False,
                                                                                    'required': True
                                                                                }
                                                                    },
                                                    'query_params': ['timecode','fields']
                                                },
                'game_playByPlay':              {
                                                    'url': BASE_URL + '{ver}/game/{gamePk}/playByPlay',
                                                    'path_params':  {
                                                                        'ver':  {
                                                                                    'type': 'str',
                                                                                    'default': 'v1',
                                                                                    'leading_slash': False,
                                                                                    'trailing_slash': False,
                                                                                    'required': True
                                                                                },
                                                                        'gamePk': {
                                                                                    'type': 'str',
                                                                                    'default': '',
                                                                                    'leading_slash': False,
                                                                                    'trailing_slash': False,
                                                                                    'required': True
                                                                                }
                                                                    },
                                                    'query_params': ['timecode','fields']
                                                },
                'gamePace':                     {
                                                    'url': BASE_URL + '{ver}/gamePace',
                                                    'path_params':  {
                                                                        'ver':  {
                                                                                    'type': 'str',
                                                                                    'default': 'v1',
                                                                                    'leading_slash': False,
                                                                                    'trailing_slash': False,
                                                                                    'required': True
                                                                                }
                                                                    },
                                                    'query_params': ['season','teamIds','leagueIds','leagueListId','sportId','gameType','startDate','endDate','venueIds','orgType','includeChildren','fields']
                                                },
                'highLow':                      {
                                                    'url': BASE_URL + '{ver}/highLow/{orgType}',
                                                    'path_params':  {
                                                                        'ver':  {
                                                                                    'type': 'str',
                                                                                    'default': 'v1',
                                                                                    'leading_slash': False,
                                                                                    'trailing_slash': False,
                                                                                    'required': True
                                                                                },
                                                                        'orgType':  {
                                                                                    'type': 'str',
                                                                                    'default': '',
                                                                                    'leading_slash': False,
                                                                                    'trailing_slash': False,
                                                                                    'required': True
                                                                                }
                                                                    },
                                                    'query_params': ['statGroup','sortStat','season','gameType','teamId','leagueId','sportIds','limit','fields']
                                                },
                'homeRunDerby':                 {
                                                    'url': BASE_URL + '{ver}/honeRunDerby/{gamePk}{bracket}{pool}',
                                                    'path_params':  {
                                                                        'ver':      {
                                                                                        'type': 'str',
                                                                                        'default': 'v1',
                                                                                        'leading_slash': False,
                                                                                        'trailing_slash': False,
                                                                                        'required': True
                                                                                    },
                                                                        'gamePk':   {
                                                                                        'type': 'str',
                                                                                        'default': '',
                                                                                        'leading_slash': False,
                                                                                        'trailing_slash': False,
                                                                                        'required': True
                                                                                    },
                                                                        'bracket':  {
                                                                                        'type': 'bool',
                                                                                        'default': False,
                                                                                        'True': '/bracket',
                                                                                        'False': '',
                                                                                        'leading_slash': False,
                                                                                        'trailing_slash': False,
                                                                                        'required': False
                                                                                    },
                                                                        'pool':     {
                                                                                        'type': 'bool',
                                                                                        'default': False,
                                                                                        'True': '/pool',
                                                                                        'False': '',
                                                                                        'leading_slash': False,
                                                                                        'trailing_slash': False,
                                                                                        'required': False
                                                                                    }
                                                                    },
                                                    'query_params': ['fields']
                                                },
                'league':                       {
                                                    'url': BASE_URL + '{ver}/league',
                                                    'path_params':  {
                                                                        'ver':  {
                                                                                    'type': 'str',
                                                                                    'default': 'v1',
                                                                                    'leading_slash': False,
                                                                                    'trailing_slash': False,
                                                                                    'required': True
                                                                                }
                                                                    },
                                                    'query_params': ['sportId','leagueIds','seasons','fields']
                                                },
                'league_allStarBallot':         {
                                                    'url': BASE_URL + '{ver}/league/{leagueId}/allStarBallot',
                                                    'path_params':  {
                                                                        'ver':      {
                                                                                        'type': 'str',
                                                                                        'default': 'v1',
                                                                                        'leading_slash': False,
                                                                                        'trailing_slash': False,
                                                                                        'required': True
                                                                                    },
                                                                        'leagueId': {
                                                                                        'type': 'str',
                                                                                        'default': '',
                                                                                        'leading_slash': False,
                                                                                        'trailing_slash': False,
                                                                                        'required': True
                                                                                    }
                                                                    },
                                                    'query_params': ['season','fields']
                                                },
                'league_allStarWriteIns':       {
                                                    'url': BASE_URL + '{ver}/league/{leagueId}/allStarWriteIns',
                                                    'path_params':  {
                                                                        'ver':      {
                                                                                        'type': 'str',
                                                                                        'default': 'v1',
                                                                                        'leading_slash': False,
                                                                                        'trailing_slash': False,
                                                                                        'required': True
                                                                                    },
                                                                        'leagueId': {
                                                                                        'type': 'str',
                                                                                        'default': '',
                                                                                        'leading_slash': False,
                                                                                        'trailing_slash': False,
                                                                                        'required': True
                                                                                    }
                                                                    },
                                                    'query_params': ['season','fields']
                                                },
                'league_allStarFinalVote':      {
                                                    'url': BASE_URL + '{ver}/league/{leagueId}/allStarFinalVote',
                                                    'path_params':  {
                                                                        'ver':      {
                                                                                        'type': 'str',
                                                                                        'default': 'v1',
                                                                                        'leading_slash': False,
                                                                                        'trailing_slash': False,
                                                                                        'required': True
                                                                                    },
                                                                        'leagueId': {
                                                                                        'type': 'str',
                                                                                        'default': '',
                                                                                        'leading_slash': False,
                                                                                        'trailing_slash': False,
                                                                                        'required': True
                                                                                    }
                                                                    },
                                                    'query_params': ['season','fields']
                                                },
                'people':                       {
                                                    'url': BASE_URL + '{ver}/people',
                                                    'path_params':  {
                                                                        'ver':      {
                                                                                        'type': 'str',
                                                                                        'default': 'v1',
                                                                                        'leading_slash': False,
                                                                                        'trailing_slash': False,
                                                                                        'required': True
                                                                                    }
                                                                    },
                                                    'query_params': ['personIds','hydrate','fields']
                                                },
                'people_changes':               {
                                                    'url': BASE_URL + '{ver}/people/changes',
                                                    'path_params':  {
                                                                        'ver':      {
                                                                                        'type': 'str',
                                                                                        'default': 'v1',
                                                                                        'leading_slash': False,
                                                                                        'trailing_slash': False,
                                                                                        'required': True
                                                                                    }
                                                                    },
                                                    'query_params': ['updatedSince','fields']
                                                },
                'people_freeAgents':            {
                                                    'url': BASE_URL + '{ver}/people/freeAgents',
                                                    'path_params':  {
                                                                        'ver':      {
                                                                                        'type': 'str',
                                                                                        'default': 'v1',
                                                                                        'leading_slash': False,
                                                                                        'trailing_slash': False,
                                                                                        'required': True
                                                                                    },
                                                                        'leagueId': {
                                                                                        'type': 'str',
                                                                                        'default': '',
                                                                                        'leading_slash': False,
                                                                                        'trailing_slash': False,
                                                                                        'required': True
                                                                                    }
                                                                    },
                                                    'query_params': ['order','hydrate','fields']
                                                },
                'person':                       {
                                                    'url': BASE_URL + '{ver}/people/{personId}',
                                                    'path_params':  {
                                                                        'ver':      {
                                                                                        'type': 'str',
                                                                                        'default': 'v1',
                                                                                        'leading_slash': False,
                                                                                        'trailing_slash': False,
                                                                                        'required': True
                                                                                    },
                                                                        'personId': {
                                                                                        'type': 'str',
                                                                                        'default': None,
                                                                                        'leading_slash': False,
                                                                                        'trailing_slash': False,
                                                                                        'required': True
                                                                                    }
                                                                    },
                                                    'query_params': ['hydrate','fields']
                                                },
                'person_stats':                 {
                                                    'url': BASE_URL + '{ver}/people/{personId}/stats/game/{gamePk}',
                                                    'path_params':  {
                                                                        'ver':      {
                                                                                        'type': 'str',
                                                                                        'default': 'v1',
                                                                                        'leading_slash': False,
                                                                                        'trailing_slash': False,
                                                                                        'required': True
                                                                                    },
                                                                        'personId': {
                                                                                        'type': 'str',
                                                                                        'default': None,
                                                                                        'leading_slash': False,
                                                                                        'trailing_slash': False,
                                                                                        'required': True
                                                                                    },
                                                                        'gamePk': {
                                                                                        'type': 'str',
                                                                                        'default': None,
                                                                                        'leading_slash': False,
                                                                                        'trailing_slash': False,
                                                                                        'required': True
                                                                                    }
                                                                    },
                                                    'query_params': ['fields'],
                                                    'note': 'Specify "current" instead of a gamePk for a player\'s current game stats.'
                                                },
                'jobs':                         {
                                                    'url': BASE_URL + '{ver}/jobs',
                                                    'path_params':  {
                                                                        'ver':      {
                                                                                        'type': 'str',
                                                                                        'default': 'v1',
                                                                                        'leading_slash': False,
                                                                                        'trailing_slash': False,
                                                                                        'required': True
                                                                                    }
                                                                    },
                                                    'query_params': ['jobType','sportId','date','fields']
                                                },
                'jobs_umpires':                 {
                                                    'url': BASE_URL + '{ver}/jobs/umpires',
                                                    'path_params':  {
                                                                        'ver':      {
                                                                                        'type': 'str',
                                                                                        'default': 'v1',
                                                                                        'leading_slash': False,
                                                                                        'trailing_slash': False,
                                                                                        'required': True
                                                                                    }
                                                                    },
                                                    'query_params': ['sportId','date','fields']
                                                },
                'jobs_umpire_games':            {
                                                    'url': BASE_URL + '{ver}/jobs/umpires/games/{umpireId}',
                                                    'path_params':  {
                                                                        'ver':      {
                                                                                        'type': 'str',
                                                                                        'default': 'v1',
                                                                                        'leading_slash': False,
                                                                                        'trailing_slash': False,
                                                                                        'required': True
                                                                                    },
                                                                        'umpireId': {
                                                                                        'type': 'str',
                                                                                        'default': None,
                                                                                        'leading_slash': False,
                                                                                        'trailing_slash': False,
                                                                                        'required': True
                                                                                    }
                                                                    },
                                                    'query_params': ['season','fields']
                                                },
                'jobs_datacasters':             {
                                                    'url': BASE_URL + '{ver}/jobs/datacasters',
                                                    'path_params':  {
                                                                        'ver':      {
                                                                                        'type': 'str',
                                                                                        'default': 'v1',
                                                                                        'leading_slash': False,
                                                                                        'trailing_slash': False,
                                                                                        'required': True
                                                                                    }
                                                                    },
                                                    'query_params': ['sportId','date','fields']
                                                },
                'jobs_officialScorers':         {
                                                    'url': BASE_URL + '{ver}/jobs/officialScorers',
                                                    'path_params':  {
                                                                        'ver':      {
                                                                                        'type': 'str',
                                                                                        'default': 'v1',
                                                                                        'leading_slash': False,
                                                                                        'trailing_slash': False,
                                                                                        'required': True
                                                                                    }
                                                                    },
                                                    'query_params': ['timecode','fields']
                                                },
                'schedule':                     {
                                                    'url': BASE_URL + '{ver}/schedule',
                                                    'path_params':  {
                                                                        'ver':      {
                                                                                        'type': 'str',
                                                                                        'default': 'v1',
                                                                                        'leading_slash': False,
                                                                                        'trailing_slash': False,
                                                                                        'required': True
                                                                                    }
                                                                    },
                                                    'query_params': ['scheduleType','eventTypes','hydrate','teamId','leagueId','sportId','gamePks','venueIds','gameTypes','date','startDate','endDate','opponentId','fields']
                                                },
                'schedule_tied':                {
                                                    'url': BASE_URL + '{ver}/schedule/games/tied',
                                                    'path_params':  {
                                                                        'ver':      {
                                                                                        'type': 'str',
                                                                                        'default': 'v1',
                                                                                        'leading_slash': False,
                                                                                        'trailing_slash': False,
                                                                                        'required': True
                                                                                    }
                                                                    },
                                                    'query_params': ['gameTypes','season','hydrate','fields']
                                                },
                'schedule_postseason':          {
                                                    'url': BASE_URL + '{ver}/schedule/postseason',
                                                    'path_params':  {
                                                                        'ver':      {
                                                                                        'type': 'str',
                                                                                        'default': 'v1',
                                                                                        'leading_slash': False,
                                                                                        'trailing_slash': False,
                                                                                        'required': True
                                                                                    }
                                                                    },
                                                    'query_params': ['gameTypes','seriesNumber','teamId','sportId','season','hydrate','fields']
                                                },
                'schedule_postseason_series':   {
                                                    'url': BASE_URL + '{ver}/schedule/postseason/series',
                                                    'path_params':  {
                                                                        'ver':      {
                                                                                        'type': 'str',
                                                                                        'default': 'v1',
                                                                                        'leading_slash': False,
                                                                                        'trailing_slash': False,
                                                                                        'required': True
                                                                                    }
                                                                    },
                                                    'query_params': ['gameTypes','seriesNumber','teamId','sportId','season','fields']
                                                },
                'schedule_postseason_tuneIn':   {
                                                    'url': BASE_URL + '{ver}/schedule/postseason/tuneIn',
                                                    'path_params':  {
                                                                        'ver':      {
                                                                                        'type': 'str',
                                                                                        'default': 'v1',
                                                                                        'leading_slash': False,
                                                                                        'trailing_slash': False,
                                                                                        'required': True
                                                                                    }
                                                                    },
                                                    'query_params': ['teamId','sportId','season','hydrate','fields'],
                                                    'note': 'The schedule_postseason_tuneIn endpoint appears to return no data.'
                                                },
                'season':                       {
                                                    'url': BASE_URL + '{ver}/seasons{all}',
                                                    'path_params':  {
                                                                        'ver':      {
                                                                                        'type': 'str',
                                                                                        'default': 'v1',
                                                                                        'leading_slash': False,
                                                                                        'trailing_slash': False,
                                                                                        'required': True
                                                                                    },
                                                                        'all':      {
                                                                                        'type': 'bool',
                                                                                        'default': False,
                                                                                        'True': '/all',
                                                                                        'False': '',
                                                                                        'leading_slash': False,
                                                                                        'trailing_slash': False,
                                                                                        'required': False
                                                                                    }
                                                                    },
                                                    'query_params': ['sportId','divisionId','leagueId','fields'],
                                                    'note': 'Include "all" parameter with value of True to query all seasons. The divisionId and leagueId parameters are supported when "all" is used.'
                                                },
                'sports':                       {
                                                    'url': BASE_URL + '{ver}/sports',
                                                    'path_params':  {
                                                                        'ver':      {
                                                                                        'type': 'str',
                                                                                        'default': 'v1',
                                                                                        'leading_slash': False,
                                                                                        'trailing_slash': False,
                                                                                        'required': True
                                                                                    }
                                                                    },
                                                    'query_params': ['sportId','fields']
                                                },
                'sports_players':               {
                                                    'url': BASE_URL + '{ver}/sports/{sportId}/players',
                                                    'path_params':  {
                                                                        'ver':      {
                                                                                        'type': 'str',
                                                                                        'default': 'v1',
                                                                                        'leading_slash': False,
                                                                                        'trailing_slash': False,
                                                                                        'required': True
                                                                                    },
                                                                        'sportId': {
                                                                                        'type': 'str',
                                                                                        'default': '1',
                                                                                        'leading_slash': False,
                                                                                        'trailing_slash': False,
                                                                                        'required': True
                                                                                    }
                                                                    },
                                                    'query_params': ['season','gameType']
                                                },
                'standings':                    {
                                                    'url': BASE_URL + '{ver}/standings',
                                                    'path_params':  {
                                                                        'ver':      {
                                                                                        'type': 'str',
                                                                                        'default': 'v1',
                                                                                        'leading_slash': False,
                                                                                        'trailing_slash': False,
                                                                                        'required': True
                                                                                    }
                                                                    },
                                                    'query_params': ['leagueId','season','standingsTypes','date','hydrate','fields']
                                                },
                'stats':                        {
                                                    'url': BASE_URL + '{ver}/stats',
                                                    'path_params':  {
                                                                        'ver':      {
                                                                                        'type': 'str',
                                                                                        'default': 'v1',
                                                                                        'leading_slash': False,
                                                                                        'trailing_slash': False,
                                                                                        'required': True
                                                                                    }
                                                                    },
                                                    'query_params': ['stats','playerPool','position','teamId','leagueId','limit','offset','group','gameType','season','sportIds','sortStat','order','hydrate','fields']
                                                },
                'stats_leaders':                {
                                                    'url': BASE_URL + '{ver}/stats/leaders',
                                                    'path_params':  {
                                                                        'ver':      {
                                                                                        'type': 'str',
                                                                                        'default': 'v1',
                                                                                        'leading_slash': False,
                                                                                        'trailing_slash': False,
                                                                                        'required': True
                                                                                    }
                                                                    },
                                                    'query_params': ['leaderCategories','playerPool','leaderGameTypes','statGroup','season','leagueId','sportId','hydrate','limit','fields']
                                                },
                'stats_streaks':                {
                                                    'url': BASE_URL + '{ver}/stats/streaks',
                                                    'path_params':  {
                                                                        'ver':      {
                                                                                        'type': 'str',
                                                                                        'default': 'v1',
                                                                                        'leading_slash': False,
                                                                                        'trailing_slash': False,
                                                                                        'required': True
                                                                                    }
                                                                    },
                                                    'query_params': ['streakType','streakSpan','gameType','season','sportId','limit','hydrate','fields']
                                                },
                'teams':                        {
                                                    'url': BASE_URL + '{ver}/teams{teamId}',
                                                    'path_params':  {
                                                                        'ver':      {
                                                                                        'type': 'str',
                                                                                        'default': 'v1',
                                                                                        'leading_slash': False,
                                                                                        'trailing_slash': False,
                                                                                        'required': True
                                                                                    },
                                                                        'teamId':   {
                                                                                        'type': 'str',
                                                                                        'default': None,
                                                                                        'leading_slash': True,
                                                                                        'trailing_slash': False,
                                                                                        'required': False
                                                                                    }
                                                                    },
                                                    'query_params': ['season','activeStatus','leagueIds','sportIds','gameType','hydrate','fields']
                                                },
                'teams_history':                {
                                                    'url': BASE_URL + '{ver}/teams/history',
                                                    'path_params':  {
                                                                        'ver':      {
                                                                                        'type': 'str',
                                                                                        'default': 'v1',
                                                                                        'leading_slash': False,
                                                                                        'trailing_slash': False,
                                                                                        'required': True
                                                                                    }
                                                                    },
                                                    'query_params': ['teamIds','startSeason','endSeason','fields']
                                                },
                'teams_stats':                  {
                                                    'url': BASE_URL + '{ver}/teams/stats',
                                                    'path_params':  {
                                                                        'ver':      {
                                                                                        'type': 'str',
                                                                                        'default': 'v1',
                                                                                        'leading_slash': False,
                                                                                        'trailing_slash': False,
                                                                                        'required': True
                                                                                    }
                                                                    },
                                                    'query_params': ['season','sportIds','statGroup','gameType','stats','order','sortStat','fields']
                                                },
                'teams_affiliates':             {
                                                    'url': BASE_URL + '{ver}/teams/affiliates',
                                                    'path_params':  {
                                                                        'ver':      {
                                                                                        'type': 'str',
                                                                                        'default': 'v1',
                                                                                        'leading_slash': False,
                                                                                        'trailing_slash': False,
                                                                                        'required': True
                                                                                    }
                                                                    },
                                                    'query_params': ['teamIds','sportId','season','hydrate','fields']
                                                },
                'team':                         {
                                                    'url': BASE_URL + '{ver}/teams/{teamId}',
                                                    'path_params':  {
                                                                        'ver':      {
                                                                                        'type': 'str',
                                                                                        'default': 'v1',
                                                                                        'leading_slash': False,
                                                                                        'trailing_slash': False,
                                                                                        'required': True
                                                                                    },
                                                                        'teamId':   {
                                                                                        'type': 'str',
                                                                                        'default': None,
                                                                                        'leading_slash': False,
                                                                                        'trailing_slash': False,
                                                                                        'required': True
                                                                                    }
                                                                    },
                                                    'query_params': ['season','sportId','hydrate','fields']
                                                },
                'team_alumni':                  {
                                                    'url': BASE_URL + '{ver}/teams/{teamId}/alumni',
                                                    'path_params':  {
                                                                        'ver':      {
                                                                                        'type': 'str',
                                                                                        'default': 'v1',
                                                                                        'leading_slash': False,
                                                                                        'trailing_slash': False,
                                                                                        'required': True
                                                                                    },
                                                                        'teamId':   {
                                                                                        'type': 'str',
                                                                                        'default': None,
                                                                                        'leading_slash': False,
                                                                                        'trailing_slash': False,
                                                                                        'required': True
                                                                                    }
                                                                    },
                                                    'query_params': ['season','group','hydrate','fields']
                                                },
                'team_choaches':                {
                                                    'url': BASE_URL + '{ver}/teams/{teamId}/coaches',
                                                    'path_params':  {
                                                                        'ver':      {
                                                                                        'type': 'str',
                                                                                        'default': 'v1',
                                                                                        'leading_slash': False,
                                                                                        'trailing_slash': False,
                                                                                        'required': True
                                                                                    },
                                                                        'teamId':   {
                                                                                        'type': 'str',
                                                                                        'default': None,
                                                                                        'leading_slash': False,
                                                                                        'trailing_slash': False,
                                                                                        'required': True
                                                                                    }
                                                                    },
                                                    'query_params': ['season','date','fields']
                                                },
                'team_personnel':               {
                                                    'url': BASE_URL + '{ver}/teams/{teamId}/personnel',
                                                    'path_params':  {
                                                                        'ver':      {
                                                                                        'type': 'str',
                                                                                        'default': 'v1',
                                                                                        'leading_slash': False,
                                                                                        'trailing_slash': False,
                                                                                        'required': True
                                                                                    },
                                                                        'teamId':   {
                                                                                        'type': 'str',
                                                                                        'default': None,
                                                                                        'leading_slash': False,
                                                                                        'trailing_slash': False,
                                                                                        'required': True
                                                                                    }
                                                                    },
                                                    'query_params': ['date','fields']
                                                },
                'team_leaders':                  {
                                                    'url': BASE_URL + '{ver}/teams/{teamId}/leaders',
                                                    'path_params':  {
                                                                        'ver':      {
                                                                                        'type': 'str',
                                                                                        'default': 'v1',
                                                                                        'leading_slash': False,
                                                                                        'trailing_slash': False,
                                                                                        'required': True
                                                                                    },
                                                                        'teamId':   {
                                                                                        'type': 'str',
                                                                                        'default': None,
                                                                                        'leading_slash': False,
                                                                                        'trailing_slash': False,
                                                                                        'required': True
                                                                                    }
                                                                    },
                                                    'query_params': ['leaderCategories','season','leaderGameTypes','hydrate','limit','fields']
                                                },
                'team_roster':                  {
                                                    'url': BASE_URL + '{ver}/teams/{teamId}/roster',
                                                    'path_params':  {
                                                                        'ver':      {
                                                                                        'type': 'str',
                                                                                        'default': 'v1',
                                                                                        'leading_slash': False,
                                                                                        'trailing_slash': False,
                                                                                        'required': True
                                                                                    },
                                                                        'teamId':   {
                                                                                        'type': 'str',
                                                                                        'default': None,
                                                                                        'leading_slash': False,
                                                                                        'trailing_slash': False,
                                                                                        'required': True
                                                                                    }
                                                                    },
                                                    'query_params': ['rosterType','season','date','hydrate','fields']
                                                },
                'venue':                        {
                                                    'url': BASE_URL + '{ver}/venues',
                                                    'path_params':  {
                                                                        'ver':      {
                                                                                        'type': 'str',
                                                                                        'default': 'v1',
                                                                                        'leading_slash': False,
                                                                                        'trailing_slash': False,
                                                                                        'required': True
                                                                                    }
                                                                    },
                                                    'query_params': ['venueIds','season','hydrate','fields']
                                                }
                #v1/analytics - requires authentication
                #v1/game/{gamePk}/guids - statcast data - requires authentication
            }

def api_call(endpoint,params):
    ep = ENDPOINTS.get(endpoint)
    if not ep: raise ValueError('Invalid endpoint ('+str(endpoint)+').')

    url = ep['url']
    print("URL:",url) #debug

    path_params = {}
    query_params = {}

    for p,pv in params.items():
        if ep['path_params'].get(p):
            print ("Found path param:",p) #debug
            path_params.update({p: str(params[p])})
        elif p in ep['query_params']:
            print ("Found query param:",p) #debug
            query_params.update({p: str(params[p])})
        else:
            print("Found invalid param:",p) #debug

    print ("path_params:",path_params) #debug
    print ("query_params:",query_params) #debug

    for k,v in path_params.items():
        print("Replacing {",k,"}",sep="") #debug
        url = url.replace('{'+k+'}',v)
        print("URL:",url) #debug
    while url.find('{') != -1 and url.find('}') > url.find('{'):
        param = url[url.find('{')+1:url.find('}')]
        if ep.get('path_params',{}).get(param,{}).get('required'): 
            if ep['path_params'][param]['default'] and ep['path_params'][param]['default'] != '':
                print("Replacing {",param,"} with default: ",ep['path_params'][param]['default'],sep="") #debug
                url = url.replace('{'+param+'}',ep['path_params'][param]['default'])
            else:
                raise ValueError('Missing required path parameter {'+str(param)+'}')
        else:
            print("Removing optional param {",param,"}",sep="") #debug
            url = url.replace('{'+param+'}','')
        print("URL:",url) #debug

    if len(query_params) > 0:
        for k,v in query_params.items():
            print("Adding query parameter ",k,"=",v,sep="")
            sep = '?' if url.find('?') == -1 else '&'
            url += sep + k + "=" + v
            print("URL:",url) #debug

    #make the request
    r = requests.get(url)
    if r.status_code not in [200,201]:
        raise ValueError('Request failed. Status Code: ' + str(r.status_code) + '.')
    else:
        return r.json()

    return None
