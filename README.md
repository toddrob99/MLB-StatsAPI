# MLB-StatsAPI

Python wrapper for MLB Stats API

Created by Todd Roberts

https://github.com/toddrob99/MLB-StatsAPI

## Installation
MLB-StatsAPI is listed on the [Python Package Index](https://pypi.org/project/MLB-StatsAPI/), 
and the preferred installation method is pip for all platforms. 
If you install manually, be sure to also install requests.

```pip install MLB-StatsAPI```

## Available Functions

* `statsapi.get()` - make calls directly to MLB StatsAPI endpoints;
  supports the most flexibility in request parameters, and returns raw json data

* `statsapi.meta()` - retrieve available values from StatsAPI for use in other queries,
  or look up descriptions for values found in API results

* `statsapi.notes()` - retrieve notes for a given endpoint, 
  including a list of required parameters, as well as hints for some endpoints

* `statsapi.schedule()` - retrieve a list of games on a given date/range and/or team/opponent

* `statsapi.boxscore()` - generate a formatted boxscore for a given game

* `statsapi.linescore()` - generate a formatted linescore for a given game

* `statsapi.roster()` - generate a list of players on a team's roster

## Example Use

###Print the number of games won by the Oakland Athletics in 2018

Use `statsapi.schedule()` to retrieve all A's games for 2018,
and use `sum()` to count records in the resultset where the A's were the winning_team.

```print('The A\'s won %s games in 2018.' % sum(1 for x in statsapi.schedule(team=133,start_date='01/01/2018',end_date='12/31/2018') if x.get('winning_team','')=='Oakland Athletics'))```

###Print the linescore for all games the Phillies won in July 2008

Use `statsapi.schedule()` to retrieve all games for July 2018,
run the resulting dict through a list comprehension
to iterate over the records where the Phillies are the winning team,
and feed the `game_id` into `statsapi_linescore()`.

```for x in [y for y in statsapi.schedule(team=143,start_date='07/01/2008',end_date='07/31/2008') if y.get('winning_team','')=='Philadelphia Phillies']:
    print('%s\nWinner: %s, Loser: %s\n%s\n\n' % (x['game_date'], x['winning_team'], x['losing_team'], statsapi.linescore(x['game_id'])))```

###Print the Phillies 40-man Roster on opening day of the 2018 season

Use `statsapi.get('season')` to retrieve the dates for the 2018 season,
feed the opening day date into `statsapi.roster()`.

```print('Phillies 40-man roster on opening day of the 2018 season:\n%s' % statsapi.roster(143,'40Man',date=statsapi.get('season',{'seasonId':2018,'sportId':1})['seasons'][0]['regularSeasonStartDate']))```

###Print the boxscore and linescore from the A's most recent game (which may be in progress)

Use `statsapi.get('schedule')` with the `team(previousSchedule)` hydration to retrieve the most recent A's game
and feed the gamePk into `statsapi.boxscore()` and `statsapi.linescore()`.

```most_recent_game = statsapi.get('schedule',{'teamId':133,'sportId':1,'hydration':'team(previousSchedule)'})['dates'][0]['games'][0]['gamePk']
print(statsapi.boxscore(most_recent_game))
print(statsapi.linescore(most_recent_game))```
