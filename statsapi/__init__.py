# encoding=utf-8
"""# MLB-StatsAPI

Python wrapper for MLB Stats API

Created by Todd Roberts

https://pypi.org/project/MLB-StatsAPI/

Issues: https://github.com/toddrob99/MLB-StatsAPI/issues

Wiki/Documentation: https://github.com/toddrob99/MLB-StatsAPI/wiki
"""
import sys

import copy
import logging
import requests
from datetime import datetime

from . import version
from . import endpoints

__version__ = version.VERSION
"""Installed version of MLB-StatsAPI"""

BASE_URL = endpoints.BASE_URL
"""Base MLB Stats API URL"""
ENDPOINTS = endpoints.ENDPOINTS
"""MLB Stats API endpoint configuration"""

logger = logging.getLogger("statsapi")

# Python 2 Support Warning
if sys.version_info.major < 3:
    logger.warning(
        "WARNING: Support for Python 2 has been discontinued. "
        "The MLB-StatsAPI module may continue to function, but "
        "issues not impacting Python 3 will be closed and support will not be provided."
    )


def schedule(
    date=None,
    start_date=None,
    end_date=None,
    team="",
    opponent="",
    sportId=1,
    game_id=None,
    leagueId=None,
    season=None,
    include_series_status=True,
):
    """Get list of games for a given date/range and/or team/opponent."""
    if end_date and not start_date:
        date = end_date
        end_date = None

    if start_date and not end_date:
        date = start_date
        start_date = None

    params = {}

    if date:
        params.update({"date": date})
    elif start_date and end_date:
        params.update({"startDate": start_date, "endDate": end_date})

    if team != "":
        params.update({"teamId": str(team)})

    if opponent != "":
        params.update({"opponentId": str(opponent)})

    if game_id:
        params.update({"gamePks": game_id})

    if leagueId:
        params.update({"leagueId": leagueId})

    if season:
        params.update({"season": season})

    hydrate = (
        "decisions,probablePitcher(note),linescore,broadcasts,game(content(media(epg)))"
    )
    if include_series_status:
        if date == "2014-03-11" or (str(start_date) <= "2014-03-11" <= str(end_date)):
            # For some reason the seriesStatus hydration throws a server error on 2014-03-11 only (checked back to 2000)
            logger.warning(
                "Excluding seriesStatus hydration because the MLB API throws an error for 2014-03-11 which is included in the requested date range."
            )
        else:
            hydrate += ",seriesStatus"
    params.update(
        {
            "sportId": str(sportId),
            "hydrate": hydrate,
        }
    )

    r = get("schedule", params)

    games = []
    if r.get("totalItems") == 0:
        return games  # TODO: ValueError('No games to parse from schedule object.') instead?
    else:
        for date in r.get("dates"):
            for game in date.get("games"):
                game_info = {
                    "game_id": game["gamePk"],
                    "game_datetime": game["gameDate"],
                    "game_date": date["date"],
                    "game_type": game["gameType"],
                    "status": game["status"]["detailedState"],
                    "away_name": game["teams"]["away"]["team"].get("name", "???"),
                    "home_name": game["teams"]["home"]["team"].get("name", "???"),
                    "away_id": game["teams"]["away"]["team"]["id"],
                    "home_id": game["teams"]["home"]["team"]["id"],
                    "doubleheader": game["doubleHeader"],
                    "game_num": game["gameNumber"],
                    "home_probable_pitcher": game["teams"]["home"]
                    .get("probablePitcher", {})
                    .get("fullName", ""),
                    "away_probable_pitcher": game["teams"]["away"]
                    .get("probablePitcher", {})
                    .get("fullName", ""),
                    "home_pitcher_note": game["teams"]["home"]
                    .get("probablePitcher", {})
                    .get("note", ""),
                    "away_pitcher_note": game["teams"]["away"]
                    .get("probablePitcher", {})
                    .get("note", ""),
                    "away_score": game["teams"]["away"].get("score", "0"),
                    "home_score": game["teams"]["home"].get("score", "0"),
                    "current_inning": game.get("linescore", {}).get(
                        "currentInning", ""
                    ),
                    "inning_state": game.get("linescore", {}).get("inningState", ""),
                    "venue_id": game.get("venue", {}).get("id"),
                    "venue_name": game.get("venue", {}).get("name"),
                    "national_broadcasts": list(
                        set(
                            broadcast["name"]
                            for broadcast in game.get("broadcasts", [])
                            if broadcast.get("isNational", False)
                        )
                    ),
                    "series_status": game.get("seriesStatus", {}).get("result"),
                }
                if game["content"].get("media", {}).get("freeGame", False):
                    game_info["national_broadcasts"].append("MLB.tv Free Game")
                if game_info["status"] in ["Final", "Game Over"]:
                    if game.get("isTie"):
                        game_info.update({"winning_team": "Tie", "losing_Team": "Tie"})
                    else:
                        game_info.update(
                            {
                                "winning_team": (
                                    game["teams"]["away"]["team"].get("name", "???")
                                    if game["teams"]["away"].get("isWinner")
                                    else game["teams"]["home"]["team"].get(
                                        "name", "???"
                                    )
                                ),
                                "losing_team": (
                                    game["teams"]["home"]["team"].get("name", "???")
                                    if game["teams"]["away"].get("isWinner")
                                    else game["teams"]["away"]["team"].get(
                                        "name", "???"
                                    )
                                ),
                                "winning_pitcher": game.get("decisions", {})
                                .get("winner", {})
                                .get("fullName", ""),
                                "losing_pitcher": game.get("decisions", {})
                                .get("loser", {})
                                .get("fullName", ""),
                                "save_pitcher": game.get("decisions", {})
                                .get("save", {})
                                .get("fullName"),
                            }
                        )
                    summary = (
                        date["date"]
                        + " - "
                        + game["teams"]["away"]["team"].get("name", "???")
                        + " ("
                        + str(game["teams"]["away"].get("score", ""))
                        + ") @ "
                        + game["teams"]["home"]["team"].get("name", "???")
                        + " ("
                        + str(game["teams"]["home"].get("score", ""))
                        + ") ("
                        + game["status"]["detailedState"]
                        + ")"
                    )
                    game_info.update({"summary": summary})
                elif game_info["status"] == "In Progress":
                    game_info.update(
                        {
                            "summary": date["date"]
                            + " - "
                            + game["teams"]["away"]["team"]["name"]
                            + " ("
                            + str(game["teams"]["away"].get("score", "0"))
                            + ") @ "
                            + game["teams"]["home"]["team"]["name"]
                            + " ("
                            + str(game["teams"]["home"].get("score", "0"))
                            + ") ("
                            + game["linescore"]["inningState"]
                            + " of the "
                            + game["linescore"]["currentInningOrdinal"]
                            + ")"
                        }
                    )
                else:
                    summary = (
                        date["date"]
                        + " - "
                        + game["teams"]["away"]["team"]["name"]
                        + " @ "
                        + game["teams"]["home"]["team"]["name"]
                        + " ("
                        + game["status"]["detailedState"]
                        + ")"
                    )
                    game_info.update({"summary": summary})

                games.append(game_info)

        return games


def boxscore(
    gamePk,
    battingBox=True,
    battingInfo=True,
    fieldingInfo=True,
    pitchingBox=True,
    gameInfo=True,
    timecode=None,
):
    """Get a formatted boxscore for a given game."""
    boxData = boxscore_data(gamePk, timecode)

    rowLen = 79
    """rowLen is the total width of each side of the box score, excluding the " | " separator"""
    fullRowLen = rowLen * 2 + 3
    """fullRowLen is the full table width"""
    boxscore = ""
    """boxscore will hold the string to be returned"""

    if battingBox:
        # Add column headers
        awayBatters = boxData["awayBatters"]
        homeBatters = boxData["homeBatters"]

        # Make sure the home and away batter lists are the same length
        blankBatter = {
            "namefield": "",
            "ab": "",
            "r": "",
            "h": "",
            "rbi": "",
            "bb": "",
            "k": "",
            "lob": "",
            "avg": "",
            "ops": "",
        }

        while len(awayBatters) > len(homeBatters):
            homeBatters.append(blankBatter)

        while len(awayBatters) < len(homeBatters):
            awayBatters.append(blankBatter)

        # Get team totals
        awayBatters.append(boxData["awayBattingTotals"])
        homeBatters.append(boxData["homeBattingTotals"])

        # Build the batting box!
        for i in range(0, len(awayBatters)):
            if i == 0 or i == len(awayBatters) - 1:
                boxscore += "-" * rowLen + " | " + "-" * rowLen + "\n"

            boxscore += "{namefield:<40} {ab:^3} {r:^3} {h:^3} {rbi:^3} {bb:^3} {k:^3} {lob:^3} {avg:^4} {ops:^5} | ".format(
                **awayBatters[i]
            )
            boxscore += "{namefield:<40} {ab:^3} {r:^3} {h:^3} {rbi:^3} {bb:^3} {k:^3} {lob:^3} {avg:^4} {ops:^5}\n".format(
                **homeBatters[i]
            )
            if i == 0 or i == len(awayBatters) - 1:
                boxscore += "-" * rowLen + " | " + "-" * rowLen + "\n"

        # Get batting notes
        awayBattingNotes = boxData["awayBattingNotes"]
        homeBattingNotes = boxData["homeBattingNotes"]

        while len(awayBattingNotes) > len(homeBattingNotes):
            homeBattingNotes.update({len(homeBattingNotes): ""})

        while len(awayBattingNotes) < len(homeBattingNotes):
            awayBattingNotes.update({len(awayBattingNotes): ""})

        for i in range(0, len(awayBattingNotes)):
            boxscore += "{:<79} | ".format(awayBattingNotes[i])
            boxscore += "{:<79}\n".format(homeBattingNotes[i])

        boxscore += " " * rowLen + " | " + " " * rowLen + "\n"

    # Get batting and fielding info
    awayBoxInfo = {}
    homeBoxInfo = {}
    boxInfo = [awayBoxInfo, homeBoxInfo]
    sides = ["away", "home"]
    for infoType in ["BATTING", "FIELDING"]:
        if (infoType == "BATTING" and battingInfo) or (
            infoType == "FIELDING" and fieldingInfo
        ):
            for i in range(0, len(sides)):
                for z in (
                    x for x in boxData[sides[i]]["info"] if x.get("title") == infoType
                ):
                    boxInfo[i].update({len(boxInfo[i]): z["title"]})
                    for x in z["fieldList"]:
                        if len(x["label"] + ": " + x.get("value", "")) > rowLen:
                            words = iter(
                                (x["label"] + ": " + x.get("value", "")).split()
                            )
                            check = ""
                            lines = []
                            for word in words:
                                if len(check) + 1 + len(word) <= rowLen:
                                    if check == "":
                                        check = word
                                    else:
                                        check += " " + word
                                else:
                                    lines.append(check)
                                    check = "    " + word

                            if len(check):
                                lines.append(check)

                            for j in range(0, len(lines)):
                                boxInfo[i].update({len(boxInfo[i]): lines[j]})
                        else:
                            boxInfo[i].update(
                                {
                                    len(boxInfo[i]): x["label"]
                                    + ": "
                                    + x.get("value", "")
                                }
                            )

            if infoType == "BATTING":
                if len(awayBoxInfo):
                    awayBoxInfo.update({len(awayBoxInfo): " "})

                if len(homeBoxInfo):
                    homeBoxInfo.update({len(homeBoxInfo): " "})

    if len(awayBoxInfo) > 0:
        while len(awayBoxInfo) > len(homeBoxInfo):
            homeBoxInfo.update({len(homeBoxInfo): ""})

        while len(awayBoxInfo) < len(homeBoxInfo):
            awayBoxInfo.update({len(awayBoxInfo): ""})

        # Build info box
        for i in range(0, len(awayBoxInfo)):
            boxscore += ("{:<%s} | " % rowLen).format(awayBoxInfo[i])
            boxscore += ("{:<%s}\n" % rowLen).format(homeBoxInfo[i])
            if i == len(awayBoxInfo) - 1:
                boxscore += "-" * rowLen + " | " + "-" * rowLen + "\n"

    # Get pitching box
    if pitchingBox:
        awayPitchers = boxData["awayPitchers"]
        homePitchers = boxData["homePitchers"]

        # Make sure the home and away pitcher lists are the same length
        blankPitcher = {
            "namefield": "",
            "ip": "",
            "h": "",
            "r": "",
            "er": "",
            "bb": "",
            "k": "",
            "hr": "",
            "era": "",
        }

        while len(awayPitchers) > len(homePitchers):
            homePitchers.append(blankPitcher)

        while len(awayPitchers) < len(homePitchers):
            awayPitchers.append(blankPitcher)

        # Get team totals
        awayPitchers.append(boxData["awayPitchingTotals"])
        homePitchers.append(boxData["homePitchingTotals"])

        # Build the pitching box!
        for i in range(0, len(awayPitchers)):
            if i == 0 or i == len(awayPitchers) - 1:
                boxscore += "-" * rowLen + " | " + "-" * rowLen + "\n"

            boxscore += "{namefield:<43} {ip:^4} {h:^3} {r:^3} {er:^3} {bb:^3} {k:^3} {hr:^3} {era:^6} | ".format(
                **awayPitchers[i]
            )
            boxscore += "{namefield:<43} {ip:^4} {h:^3} {r:^3} {er:^3} {bb:^3} {k:^3} {hr:^3} {era:^6}\n".format(
                **homePitchers[i]
            )
            if i == 0 or i == len(awayPitchers) - 1:
                boxscore += "-" * rowLen + " | " + "-" * rowLen + "\n"

    # Get game info
    if gameInfo:
        z = boxData["gameBoxInfo"]
        gameBoxInfo = {}
        for x in z:
            if (
                len(x["label"] + (": " if x.get("value") else "") + x.get("value", ""))
                > fullRowLen
            ):
                words = iter(
                    (
                        x["label"]
                        + (": " if x.get("value") else "")
                        + x.get("value", "")
                    ).split()
                )
                check = ""
                lines = []
                for word in words:
                    if len(check) + 1 + len(word) <= fullRowLen:
                        if check == "":
                            check = word
                        else:
                            check += " " + word
                    else:
                        lines.append(check)
                        check = "    " + word

                if len(check):
                    lines.append(check)

                for i in range(0, len(lines)):
                    gameBoxInfo.update({len(gameBoxInfo): lines[i]})
            else:
                gameBoxInfo.update(
                    {
                        len(gameBoxInfo): x["label"]
                        + (": " if x.get("value") else "")
                        + x.get("value", "")
                    }
                )

        # Build the game info box
        for i in range(0, len(gameBoxInfo)):
            boxscore += ("{:<%s}" % fullRowLen + "\n").format(gameBoxInfo[i])
            if i == len(gameBoxInfo) - 1:
                boxscore += "-" * fullRowLen + "\n"

    return boxscore


def boxscore_data(gamePk, timecode=None):
    """Returns a python dict containing boxscore data for a given game."""

    boxData = {}
    """boxData holds the dict to be returned"""

    params = {
        "gamePk": gamePk,
        "fields": "gameData,game,teams,teamName,shortName,teamStats,batting,atBats,runs,hits,doubles,triples,homeRuns,rbi,stolenBases,strikeOuts,baseOnBalls,leftOnBase,pitching,inningsPitched,earnedRuns,homeRuns,players,boxscoreName,liveData,boxscore,teams,players,id,fullName,allPositions,abbreviation,seasonStats,batting,avg,ops,obp,slg,era,pitchesThrown,numberOfPitches,strikes,battingOrder,info,title,fieldList,note,label,value,wins,losses,holds,blownSaves",
    }
    if timecode:
        params.update({"timecode": timecode})

    r = get("game", params)

    boxData.update({"gameId": r["gameData"]["game"]["id"]})
    boxData.update({"teamInfo": r["gameData"]["teams"]})
    boxData.update({"playerInfo": r["gameData"]["players"]})
    boxData.update({"away": r["liveData"]["boxscore"]["teams"]["away"]})
    boxData.update({"home": r["liveData"]["boxscore"]["teams"]["home"]})

    batterColumns = [
        {
            "namefield": boxData["teamInfo"]["away"]["teamName"] + " Batters",
            "ab": "AB",
            "r": "R",
            "h": "H",
            "doubles": "2B",
            "triples": "3B",
            "hr": "HR",
            "rbi": "RBI",
            "sb": "SB",
            "bb": "BB",
            "k": "K",
            "lob": "LOB",
            "avg": "AVG",
            "ops": "OPS",
            "personId": 0,
            "substitution": False,
            "note": "",
            "name": boxData["teamInfo"]["away"]["teamName"] + " Batters",
            "position": "",
            "obp": "OBP",
            "slg": "SLG",
            "battingOrder": "",
        }
    ]
    # Add away and home column headers
    sides = ["away", "home"]
    awayBatters = copy.deepcopy(batterColumns)
    homeBatters = copy.deepcopy(batterColumns)
    homeBatters[0]["namefield"] = boxData["teamInfo"]["home"]["teamName"] + " Batters"
    homeBatters[0]["name"] = boxData["teamInfo"]["home"]["teamName"] + " Batters"
    batters = [awayBatters, homeBatters]

    for i in range(0, len(sides)):
        side = sides[i]
        for batterId_int in [
            x
            for x in boxData[side]["batters"]
            if boxData[side]["players"].get("ID" + str(x), {}).get("battingOrder")
        ]:
            batterId = str(batterId_int)
            namefield = (
                str(boxData[side]["players"]["ID" + batterId]["battingOrder"])[0]
                if str(boxData[side]["players"]["ID" + batterId]["battingOrder"])[-1]
                == "0"
                else "   "
            )
            namefield += " " + boxData[side]["players"]["ID" + batterId]["stats"][
                "batting"
            ].get("note", "")
            namefield += (
                boxData["playerInfo"]["ID" + batterId]["boxscoreName"]
                + "  "
                + boxData[side]["players"]["ID" + batterId]["position"]["abbreviation"]
            )
            if not len(
                boxData[side]["players"]["ID" + batterId]
                .get("stats", {})
                .get("batting", {})
            ):
                # Protect against player with no batting data in the box score (#37)
                continue

            batter = {
                "namefield": namefield,
                "ab": str(
                    boxData[side]["players"]["ID" + batterId]["stats"]["batting"][
                        "atBats"
                    ]
                ),
                "r": str(
                    boxData[side]["players"]["ID" + batterId]["stats"]["batting"][
                        "runs"
                    ]
                ),
                "h": str(
                    boxData[side]["players"]["ID" + batterId]["stats"]["batting"][
                        "hits"
                    ]
                ),
                "doubles": str(
                    boxData[side]["players"]["ID" + batterId]["stats"]["batting"][
                        "doubles"
                    ]
                ),
                "triples": str(
                    boxData[side]["players"]["ID" + batterId]["stats"]["batting"][
                        "triples"
                    ]
                ),
                "hr": str(
                    boxData[side]["players"]["ID" + batterId]["stats"]["batting"][
                        "homeRuns"
                    ]
                ),
                "rbi": str(
                    boxData[side]["players"]["ID" + batterId]["stats"]["batting"]["rbi"]
                ),
                "sb": str(
                    boxData[side]["players"]["ID" + batterId]["stats"]["batting"][
                        "stolenBases"
                    ]
                ),
                "bb": str(
                    boxData[side]["players"]["ID" + batterId]["stats"]["batting"][
                        "baseOnBalls"
                    ]
                ),
                "k": str(
                    boxData[side]["players"]["ID" + batterId]["stats"]["batting"][
                        "strikeOuts"
                    ]
                ),
                "lob": str(
                    boxData[side]["players"]["ID" + batterId]["stats"]["batting"][
                        "leftOnBase"
                    ]
                ),
                "avg": str(
                    boxData[side]["players"]["ID" + batterId]["seasonStats"]["batting"][
                        "avg"
                    ]
                ),
                "ops": str(
                    boxData[side]["players"]["ID" + batterId]["seasonStats"]["batting"][
                        "ops"
                    ]
                ),
                "personId": batterId_int,
                "battingOrder": str(
                    boxData[side]["players"]["ID" + batterId]["battingOrder"]
                ),
                "substitution": (
                    False
                    if str(boxData[side]["players"]["ID" + batterId]["battingOrder"])[
                        -1
                    ]
                    == "0"
                    else True
                ),
                "note": boxData[side]["players"]["ID" + batterId]["stats"][
                    "batting"
                ].get("note", ""),
                "name": boxData["playerInfo"]["ID" + batterId]["boxscoreName"],
                "position": boxData[side]["players"]["ID" + batterId]["position"][
                    "abbreviation"
                ],
                "obp": str(
                    boxData[side]["players"]["ID" + batterId]["seasonStats"]["batting"][
                        "obp"
                    ]
                ),
                "slg": str(
                    boxData[side]["players"]["ID" + batterId]["seasonStats"]["batting"][
                        "slg"
                    ]
                ),
            }
            batters[i].append(batter)

    boxData.update({"awayBatters": awayBatters})
    boxData.update({"homeBatters": homeBatters})

    # Add team totals
    sidesBattingTotals = ["awayBattingTotals", "homeBattingTotals"]
    for i in range(0, len(sides)):
        side = sides[i]
        boxData.update(
            {
                sidesBattingTotals[i]: {
                    "namefield": "Totals",
                    "ab": str(boxData[side]["teamStats"]["batting"]["atBats"]),
                    "r": str(boxData[side]["teamStats"]["batting"]["runs"]),
                    "h": str(boxData[side]["teamStats"]["batting"]["hits"]),
                    "hr": str(boxData[side]["teamStats"]["batting"]["homeRuns"]),
                    "rbi": str(boxData[side]["teamStats"]["batting"]["rbi"]),
                    "bb": str(boxData[side]["teamStats"]["batting"]["baseOnBalls"]),
                    "k": str(boxData[side]["teamStats"]["batting"]["strikeOuts"]),
                    "lob": str(boxData[side]["teamStats"]["batting"]["leftOnBase"]),
                    "avg": "",
                    "ops": "",
                    "obp": "",
                    "slg": "",
                    "name": "Totals",
                    "position": "",
                    "note": "",
                    "substitution": False,
                    "battingOrder": "",
                    "personId": 0,
                }
            }
        )

    # Get batting notes
    awayBattingNotes = {}
    homeBattingNotes = {}
    battingNotes = [awayBattingNotes, homeBattingNotes]
    for i in range(0, len(sides)):
        for n in boxData[sides[i]]["note"]:
            battingNotes[i].update(
                {len(battingNotes[i]): n["label"] + "-" + n["value"]}
            )

    boxData.update({"awayBattingNotes": awayBattingNotes})
    boxData.update({"homeBattingNotes": homeBattingNotes})

    # Get pitching box
    # Add column headers
    pitcherColumns = [
        {
            "namefield": boxData["teamInfo"]["away"]["teamName"] + " Pitchers",
            "ip": "IP",
            "h": "H",
            "r": "R",
            "er": "ER",
            "bb": "BB",
            "k": "K",
            "hr": "HR",
            "era": "ERA",
            "p": "P",
            "s": "S",
            "name": boxData["teamInfo"]["away"]["teamName"] + " Pitchers",
            "personId": 0,
            "note": "",
        }
    ]
    awayPitchers = copy.deepcopy(pitcherColumns)
    homePitchers = copy.deepcopy(pitcherColumns)
    homePitchers[0]["namefield"] = boxData["teamInfo"]["home"]["teamName"] + " Pitchers"
    homePitchers[0]["name"] = boxData["teamInfo"]["away"]["teamName"] + " Pitchers"
    pitchers = [awayPitchers, homePitchers]

    for i in range(0, len(sides)):
        side = sides[i]
        for pitcherId_int in boxData[side]["pitchers"]:
            pitcherId = str(pitcherId_int)
            if not boxData[side]["players"].get("ID" + pitcherId) or not len(
                boxData[side]["players"]["ID" + pitcherId]
                .get("stats", {})
                .get("pitching", {})
            ):
                # Skip pitcher with no pitching data in the box score (#37)
                # Or skip pitcher listed under the wrong team (from comments on #37)
                continue

            namefield = boxData["playerInfo"]["ID" + pitcherId]["boxscoreName"]
            namefield += (
                "  "
                + boxData[side]["players"]["ID" + pitcherId]["stats"]["pitching"].get(
                    "note", ""
                )
                if boxData[side]["players"]["ID" + pitcherId]["stats"]["pitching"].get(
                    "note"
                )
                else ""
            )
            pitcher = {
                "namefield": namefield,
                "ip": str(
                    boxData[side]["players"]["ID" + pitcherId]["stats"]["pitching"][
                        "inningsPitched"
                    ]
                ),
                "h": str(
                    boxData[side]["players"]["ID" + pitcherId]["stats"]["pitching"][
                        "hits"
                    ]
                ),
                "r": str(
                    boxData[side]["players"]["ID" + pitcherId]["stats"]["pitching"][
                        "runs"
                    ]
                ),
                "er": str(
                    boxData[side]["players"]["ID" + pitcherId]["stats"]["pitching"][
                        "earnedRuns"
                    ]
                ),
                "bb": str(
                    boxData[side]["players"]["ID" + pitcherId]["stats"]["pitching"][
                        "baseOnBalls"
                    ]
                ),
                "k": str(
                    boxData[side]["players"]["ID" + pitcherId]["stats"]["pitching"][
                        "strikeOuts"
                    ]
                ),
                "hr": str(
                    boxData[side]["players"]["ID" + pitcherId]["stats"]["pitching"][
                        "homeRuns"
                    ]
                ),
                "p": str(
                    boxData[side]["players"]["ID" + pitcherId]["stats"]["pitching"].get(
                        "pitchesThrown",
                        boxData[side]["players"]["ID" + pitcherId]["stats"][
                            "pitching"
                        ].get("numberOfPitches", 0),
                    )
                ),
                "s": str(
                    boxData[side]["players"]["ID" + pitcherId]["stats"]["pitching"][
                        "strikes"
                    ]
                ),
                "era": str(
                    boxData[side]["players"]["ID" + pitcherId]["seasonStats"][
                        "pitching"
                    ]["era"]
                ),
                "name": boxData["playerInfo"]["ID" + pitcherId]["boxscoreName"],
                "personId": pitcherId_int,
                "note": boxData[side]["players"]["ID" + pitcherId]["stats"][
                    "pitching"
                ].get("note", ""),
            }
            pitchers[i].append(pitcher)

    boxData.update({"awayPitchers": awayPitchers})
    boxData.update({"homePitchers": homePitchers})

    # Get team totals
    pitchingTotals = ["awayPitchingTotals", "homePitchingTotals"]
    for i in range(0, len(sides)):
        side = sides[i]
        boxData.update(
            {
                pitchingTotals[i]: {
                    "namefield": "Totals",
                    "ip": str(boxData[side]["teamStats"]["pitching"]["inningsPitched"]),
                    "h": str(boxData[side]["teamStats"]["pitching"]["hits"]),
                    "r": str(boxData[side]["teamStats"]["pitching"]["runs"]),
                    "er": str(boxData[side]["teamStats"]["pitching"]["earnedRuns"]),
                    "bb": str(boxData[side]["teamStats"]["pitching"]["baseOnBalls"]),
                    "k": str(boxData[side]["teamStats"]["pitching"]["strikeOuts"]),
                    "hr": str(boxData[side]["teamStats"]["pitching"]["homeRuns"]),
                    "p": "",
                    "s": "",
                    "era": "",
                    "name": "Totals",
                    "personId": 0,
                    "note": "",
                }
            }
        )

    # Get game info
    boxData.update({"gameBoxInfo": r["liveData"]["boxscore"].get("info", [])})

    return boxData


def linescore(gamePk, timecode=None):
    """Get formatted linescore for a given game."""
    linescore = ""
    params = {
        "gamePk": gamePk,
        "fields": "gameData,teams,teamName,shortName,status,abstractGameState,liveData,linescore,innings,num,home,away,runs,hits,errors",
    }
    if timecode:
        params.update({"timecode": timecode})

    r = get("game", params)

    header_name = r["gameData"]["status"]["abstractGameState"]
    away_name = r["gameData"]["teams"]["away"]["teamName"]
    home_name = r["gameData"]["teams"]["home"]["teamName"]
    header_row = []
    away = []
    home = []

    for x in r["liveData"]["linescore"]["innings"]:
        header_row.append(str(x.get("num", "")))
        away.append(str(x.get("away", {}).get("runs", 0)))
        home.append(str(x.get("home", {}).get("runs", 0)))

    if len(r["liveData"]["linescore"]["innings"]) < 9:
        for i in range(len(r["liveData"]["linescore"]["innings"]) + 1, 10):
            header_row.append(str(i))
            away.append(" ")
            home.append(" ")

    header_row.extend(["R", "H", "E"])
    away_prefix = r["liveData"]["linescore"].get("teams", {}).get("away", {})
    away.extend(
        [
            str(away_prefix.get("runs", 0)),
            str(away_prefix.get("hits", 0)),
            str(away_prefix.get("errors", 0)),
        ]
    )
    home_prefix = r["liveData"]["linescore"].get("teams", {}).get("home", {})
    home.extend(
        [
            str(home_prefix.get("runs", 0)),
            str(home_prefix.get("hits", 0)),
            str(home_prefix.get("errors", 0)),
        ]
    )

    # Build the linescore
    for k in [[header_name, header_row], [away_name, away], [home_name, home]]:
        linescore += (
            "{:<%s}" % str(len(max([header_name, away_name, home_name], key=len)) + 1)
        ).format(k[0])
        linescore += ("{:^2}" * (len(k[1]) - 3)).format(*k[1])
        linescore += ("{:^4}" * 3).format(*k[1][-3:])
        linescore += "\n"

    if len(linescore) > 1:
        linescore = linescore[:-1]  # strip the extra line break

    return linescore


def last_game(teamId):
    """Get the gamePk for the given team's most recent completed game."""
    previousSchedule = get(
        "team",
        {
            "teamId": teamId,
            "hydrate": "previousSchedule",
            "fields": "teams,team,id,previousGameSchedule,dates,date,games,gamePk,gameDate,status,abstractGameCode",
        },
    )
    games = []
    for d in previousSchedule["teams"][0]["previousGameSchedule"]["dates"]:
        games.extend([x for x in d["games"] if x["status"]["abstractGameCode"] == "F"])

    if not len(games):
        return None

    return games[-1]["gamePk"]


def next_game(teamId):
    """Get the gamePk for the given team's next unstarted game."""
    nextSchedule = get(
        "team",
        {
            "teamId": teamId,
            "hydrate": "nextSchedule",
            "fields": "teams,team,id,nextGameSchedule,dates,date,games,gamePk,gameDate,status,abstractGameCode",
        },
    )
    games = []
    for d in nextSchedule["teams"][0]["nextGameSchedule"]["dates"]:
        games.extend([x for x in d["games"] if x["status"]["abstractGameCode"] == "P"])

    if not len(games):
        return None

    return games[0]["gamePk"]


def game_scoring_plays(gamePk):
    """Get a text-formatted list of scoring plays for a given game."""
    sortedPlays = game_scoring_play_data(gamePk)
    scoring_plays = ""
    for a in sortedPlays["plays"]:
        scoring_plays += "{}\n{} {} - {}: {}, {}: {}\n\n".format(
            a["result"]["description"],
            a["about"]["halfInning"][0:1].upper() + a["about"]["halfInning"][1:],
            a["about"]["inning"],
            sortedPlays["away"]["name"],
            a["result"]["awayScore"],
            sortedPlays["home"]["name"],
            a["result"]["homeScore"],
        )

    if len(scoring_plays) > 1:
        scoring_plays = scoring_plays[:-2]  # strip the extra line break

    return scoring_plays


def game_scoring_play_data(gamePk):
    """Returns a python dict of scoring plays for a given game containing 3 keys:

    * home - home team data
    * away - away team data
    * plays - sorted list of scoring play data
    """
    r = get(
        "game",
        {
            "gamePk": gamePk,
            "fields": (
                "gamePk,link,gameData,game,pk,teams,away,id,name,teamCode,fileCode,"
                "abbreviation,teamName,locationName,shortName,home,liveData,plays,"
                "allPlays,scoringPlays,scoringPlays,atBatIndex,result,description,"
                "awayScore,homeScore,about,halfInning,inning,endTime"
            ),
        },
    )
    if not len(r["liveData"]["plays"].get("scoringPlays", [])):
        return {
            "home": r["gameData"]["teams"]["home"],
            "away": r["gameData"]["teams"]["away"],
            "plays": [],
        }

    unorderedPlays = {}
    for i in r["liveData"]["plays"].get("scoringPlays", []):
        play = next(
            (p for p in r["liveData"]["plays"]["allPlays"] if p.get("atBatIndex") == i),
            None,
        )
        if play:
            unorderedPlays.update({play["about"]["endTime"]: play})

    sortedPlays = []
    for x in sorted(unorderedPlays):
        sortedPlays.append(unorderedPlays[x])

    return {
        "home": r["gameData"]["teams"]["home"],
        "away": r["gameData"]["teams"]["away"],
        "plays": sortedPlays,
    }


def game_highlights(gamePk):
    """Get the highlight video links for a given game."""
    sortedHighlights = game_highlight_data(gamePk)

    highlights = ""
    for a in sortedHighlights:
        # if sum(1 for t in a['keywordsAll'] if t['type']=='team_id') == 1:
        #    highlights += next(t['displayName'] for t in a['keywordsAll'] if t['type']=='team_id') + '\n'
        highlights += "{} ({})\n{}\n{}\n\n".format(
            a.get("title", a.get("headline", "")),
            a["duration"],
            a.get("description", ""),
            next(
                (s["url"] for s in a["playbacks"] if s["name"] == "mp4Avc"),
                next(
                    (
                        s["url"]
                        for s in a["playbacks"]
                        if s["name"] == "FLASH_2500K_1280X720"
                    ),
                    "Link not found",
                ),
            ),
        )

    return highlights


def game_highlight_data(gamePk):
    """Returns a list of highlight data for a given game."""
    r = get(
        "schedule",
        {
            "sportId": 1,
            "gamePk": gamePk,
            "hydrate": "game(content(highlights(highlights)))",
            "fields": "dates,date,games,gamePk,content,highlights,items,headline,type,value,title,description,duration,playbacks,name,url",
        },
    )
    gameHighlights = (
        r["dates"][0]["games"][0]
        .get("content", {})
        .get("highlights", {})
        .get("highlights", {})
    )
    if not gameHighlights or not len(gameHighlights.get("items", [])):
        return []

    unorderedHighlights = {}
    for v in (
        x
        for x in gameHighlights["items"]
        if isinstance(x, dict) and x["type"] == "video"
    ):
        unorderedHighlights.update({v["date"]: v})

    sortedHighlights = []
    for x in sorted(unorderedHighlights):
        sortedHighlights.append(unorderedHighlights[x])

    return sortedHighlights


def game_pace(season=datetime.now().year, sportId=1):
    """Get a text-formatted list about pace of game for a given season (back to 1999)."""
    r = game_pace_data(season, sportId)

    pace = ""

    pace += "{} Game Pace Stats\n".format(season)
    for s in r["sports"]:
        for k in s.keys():
            if k in ["season", "sport"]:
                continue

            if k == "prPortalCalculatedFields":
                for x in s[k].keys():
                    pace += "{}: {}\n".format(x, s[k][x])
            else:
                pace += "{}: {}\n".format(k, s[k])

    return pace


def game_pace_data(season=datetime.now().year, sportId=1):
    """Returns data about pace of game for a given season (back to 1999)."""
    params = {}
    if season:
        params.update({"season": season})

    if sportId:
        params.update({"sportId": sportId})

    r = get("gamePace", params)

    if not len(r["sports"]):
        raise ValueError(
            "No game pace info found for the {} season. Game pace data appears to begin in 1999.".format(
                season
            )
        )

    return r


def player_stats(
    personId, group="[hitting,pitching,fielding]", type="season", season=None
):
    """Get current season or career stats for a given player."""
    player = player_stat_data(personId, group, type, season)

    stats = ""
    stats += player["first_name"]
    if player["nickname"]:
        stats += ' "{nickname}"'.format(**player)

    stats += " {last_name}, {position} ({mlb_debut:.4}-".format(**player)
    if not player["active"]:
        stats += "{last_played:.4}".format(**player)

    stats += ")\n\n"

    for x in player["stats"]:
        stats += (
            x["type"][0:1].upper()
            + x["type"][1:]
            + " "
            + x["group"][0:1].upper()
            + x["group"][1:]
        )
        if x["stats"].get("position"):
            stats += " ({})".format(x["stats"]["position"]["abbreviation"])

        stats += "\n"
        for y in x["stats"].keys():
            if y == "position":
                continue
            stats += "{}: {}\n".format(y, x["stats"][y])

        stats += "\n"

    return stats


def player_stat_data(
    personId, group="[hitting,pitching,fielding]", type="season", sportId=1, season=None
):
    """Returns a list of current season or career stat data for a given player."""

    if season is not None and "season" not in type:
        raise ValueError(
            "The 'season' parameter is only valid when using the 'season' type."
        )

    params = {
        "personId": personId,
        "hydrate": "stats(group="
        + group
        + ",type="
        + type
        + (",season=" + str(season) if season else "")
        + ",sportId="
        + str(sportId)
        + "),currentTeam",
    }
    r = get("person", params)

    stat_groups = []

    player = {
        "id": r["people"][0]["id"],
        "first_name": r["people"][0]["useName"],
        "last_name": r["people"][0]["lastName"],
        "active": r["people"][0]["active"],
        "current_team": r["people"][0]["currentTeam"]["name"],
        "position": r["people"][0]["primaryPosition"]["abbreviation"],
        "nickname": r["people"][0].get("nickName"),
        "last_played": r["people"][0].get("lastPlayedDate"),
        "mlb_debut": r["people"][0].get("mlbDebutDate"),
        "bat_side": r["people"][0]["batSide"]["description"],
        "pitch_hand": r["people"][0]["pitchHand"]["description"],
    }

    for s in r["people"][0].get("stats", []):
        for i in range(0, len(s["splits"])):
            stat_group = {
                "type": s["type"]["displayName"],
                "group": s["group"]["displayName"],
                "season": s["splits"][i].get("season"),
                "stats": s["splits"][i]["stat"],
            }
            stat_groups.append(stat_group)

    player.update({"stats": stat_groups})

    return player


def latest_season(sportId=1):
    """Get the latest season for a given sportId. Returns a dict containing seasonId and various dates."""
    params = {
        "sportId": sportId,
        "seasonId": "all",
    }
    all_seasons = get("season", params)
    return next(
        (
            s
            for s in all_seasons.get("seasons", [])
            if (datetime.today().strftime("%Y-%m-%d") < s.get("seasonEndDate", ""))
        ),
        all_seasons["seasons"][-1],
    )


def lookup_player(lookup_value, gameType=None, season=None, sportId=1):
    """Get data about players based on first, last, or full name."""
    params = {
        "sportId": sportId,
        "fields": "people,id,fullName,firstName,lastName,primaryNumber,currentTeam,id,primaryPosition,code,abbreviation,useName,boxscoreName,nickName,mlbDebutDate,nameFirstLast,firstLastName,lastFirstName,lastInitName,initLastName,fullFMLName,fullLFMName,nameSlug",
    }
    if gameType:
        params.update(
            {
                "gameType": gameType,
            }
        )
    if not season:
        season_data = latest_season(sportId=sportId)
        season = season_data.get("seasonId", datetime.now().year)
    params.update(
        {
            "season": season,
        }
    )
    r = get("sports_players", params)

    players = []
    lookup_values = str(lookup_value).lower().split()
    for player in r["people"]:
        for l in lookup_values:
            for v in player.values():
                if l in str(v).lower():
                    break
            else:
                break
        else:
            players.append(player)

    return players


def lookup_team(lookup_value, activeStatus="Y", season=None, sportIds=1):
    """Get a info about a team or teams based on the team name, city, abbreviation, or file code."""
    params = {
        "activeStatus": activeStatus,
        "sportIds": sportIds,
        "fields": "teams,id,name,teamCode,fileCode,teamName,locationName,shortName",
    }
    if not season:
        season_data = latest_season(sportId=str(sportIds).split(",")[0])
        season = season_data.get("seasonId", datetime.now().year)
    params.update(
        {
            "season": season,
        }
    )
    r = get("teams", params)

    teams = []
    for team in r["teams"]:
        for v in team.values():
            if str(lookup_value).lower() in str(v).lower():
                teams.append(team)
                break

    return teams


def team_leaders(
    teamId, leaderCategories, season=datetime.now().year, leaderGameTypes="R", limit=10
):
    """Get stat leaders for a given team."""
    lines = team_leader_data(teamId, leaderCategories, season, leaderGameTypes, limit)

    leaders = ""

    leaders += "{:<4} {:<20} {:<5}\n".format(*["Rank", "Name", "Value"])
    for a in lines:
        leaders += "{:^4} {:<20} {:^5}\n".format(*a)

    return leaders


def team_leader_data(
    teamId, leaderCategories, season=datetime.now().year, leaderGameTypes="R", limit=10
):
    """Returns a python list of stat leader data for a given team."""
    params = {
        "leaderCategories": leaderCategories,
        "season": season,
        "teamId": teamId,
        "leaderGameTypes": leaderGameTypes,
        "limit": limit,
    }
    params.update({"fields": "teamLeaders,leaders,rank,value,person,fullName"})

    r = get("team_leaders", params)

    lines = []
    for player in [x for x in r["teamLeaders"][0]["leaders"]]:
        lines.append([player["rank"], player["person"]["fullName"], player["value"]])

    return lines


def league_leaders(
    leaderCategories,
    season=None,
    limit=10,
    statGroup=None,
    leagueId=None,
    gameTypes=None,
    playerPool=None,
    sportId=1,
    statType=None,
):
    """Get stat leaders overall or for a given league (103=AL, 104=NL)."""
    lines = league_leader_data(
        leaderCategories,
        season,
        limit,
        statGroup,
        leagueId,
        gameTypes,
        playerPool,
        sportId,
        statType,
    )

    leaders = ""

    leaders += "{:<4} {:<20} {:<23} {:<5}\n".format(*["Rank", "Name", "Team", "Value"])
    for a in lines:
        leaders += "{:^4} {:<20} {:<23} {:^5}\n".format(*a)

    return leaders


def league_leader_data(
    leaderCategories,
    season=None,
    limit=10,
    statGroup=None,
    leagueId=None,
    gameTypes=None,
    playerPool=None,
    sportId=1,
    statType=None,
):
    """Returns a python list of stat leaders overall or for a given league (103=AL, 104=NL)."""
    params = {"leaderCategories": leaderCategories, "sportId": sportId, "limit": limit}
    if season:
        params.update({"season": season})

    if statType:
        params.update({"statType": statType})

    if not season and not statType:
        params.update(
            {"season": datetime.now().year}
        )  # default season to current year if no season or statType provided

    if statGroup:
        if statGroup == "batting":
            statGroup = "hitting"

        params.update({"statGroup": statGroup})

    if gameTypes:
        params.update({"leaderGameTypes": gameTypes})

    if leagueId:
        params.update({"leagueId": leagueId})

    if playerPool:
        params.update({"playerPool": playerPool})

    params.update(
        {
            "fields": "leagueLeaders,leaders,rank,value,team,name,league,name,person,fullName"
        }
    )

    r = get("stats_leaders", params)

    lines = []
    for player in [x for x in r["leagueLeaders"][0]["leaders"]]:
        lines.append(
            [
                player["rank"],
                player["person"]["fullName"],
                player["team"].get("name", ""),
                player["value"],
            ]
        )

    return lines


def standings(
    leagueId="103,104",
    division="all",
    include_wildcard=True,
    season=None,
    standingsTypes=None,
    date=None,
):
    """Get formatted standings for a given league/division and season."""
    divisions = standings_data(
        leagueId, division, include_wildcard, season, standingsTypes, date
    )

    standings = ""

    for div in divisions.values():
        standings += div["div_name"] + "\n"
        if include_wildcard:
            standings += (
                "{:^4} {:<21} {:^3} {:^3} {:^4} {:^4} {:^7} {:^5} {:^4}\n".format(
                    *[
                        "Rank",
                        "Team",
                        "W",
                        "L",
                        "GB",
                        "(E#)",
                        "WC Rank",
                        "WC GB",
                        "(E#)",
                    ]
                )
            )
            for t in div["teams"]:
                standings += "{div_rank:^4} {name:<21} {w:^3} {l:^3} {gb:^4} {elim_num:^4} {wc_rank:^7} {wc_gb:^5} {wc_elim_num:^4}\n".format(
                    **t
                )
        else:
            standings += "{:^4} {:<21} {:^3} {:^3} {:^4} {:^4}\n".format(
                *["Rank", "Team", "W", "L", "GB", "(E#)"]
            )
            for t in div["teams"]:
                standings += "{div_rank:^4} {name:<21} {w:^3} {l:^3} {gb:^4} {elim_num:^4}\n".format(
                    **t
                )
        standings += "\n"

    return standings


def standings_data(
    leagueId="103,104",
    division="all",
    include_wildcard=True,
    season=None,
    standingsTypes=None,
    date=None,
):
    """Returns a dict of standings data for a given league/division and season."""
    params = {"leagueId": leagueId}
    if date:
        params.update({"date": date})

    if not season:
        if date:
            season = date[-4:]
        else:
            season = datetime.now().year

    if not standingsTypes:
        standingsTypes = "regularSeason"

    params.update({"season": season, "standingsTypes": standingsTypes})
    params.update(
        {
            "hydrate": "team(division)",
            "fields": "records,standingsType,teamRecords,team,name,division,id,nameShort,abbreviation,divisionRank,gamesBack,wildCardRank,wildCardGamesBack,wildCardEliminationNumber,divisionGamesBack,clinched,eliminationNumber,winningPercentage,type,wins,losses,leagueRank,sportRank",
        }
    )

    r = get("standings", params)

    divisions = {}

    for y in r["records"]:
        for x in (
            x
            for x in y["teamRecords"]
            if str(division).lower() == "all"
            or str(division).lower() == x["team"]["division"]["abbreviation"].lower()
            or str(division) == str(x["team"]["division"]["id"])
        ):
            if x["team"]["division"]["id"] not in divisions.keys():
                divisions.update(
                    {
                        x["team"]["division"]["id"]: {
                            "div_name": x["team"]["division"]["name"],
                            "teams": [],
                        }
                    }
                )

            team = {
                "name": x["team"]["name"],
                "div_rank": x["divisionRank"],
                "w": x["wins"],
                "l": x["losses"],
                "gb": x["gamesBack"],
                "wc_rank": x.get("wildCardRank", "-"),
                "wc_gb": x.get("wildCardGamesBack", "-"),
                "wc_elim_num": x.get("wildCardEliminationNumber", "-"),
                "elim_num": x.get("eliminationNumber", "-"),
                "team_id": x["team"]["id"],
                "league_rank": x.get("leagueRank", "-"),
                "sport_rank": x.get("sportRank", "-"),
            }
            divisions[x["team"]["division"]["id"]]["teams"].append(team)

    return divisions


def roster(teamId, rosterType=None, season=datetime.now().year, date=None):
    """Get the roster for a given team."""
    if not rosterType:
        rosterType = "active"

    params = {"rosterType": rosterType, "season": season, "teamId": teamId}
    if date:
        params.update({"date": date})

    r = get("team_roster", params)

    roster = ""
    players = []
    for x in r["roster"]:
        players.append(
            [x["jerseyNumber"], x["position"]["abbreviation"], x["person"]["fullName"]]
        )

    for i in range(0, len(players)):
        roster += ("#{:<3} {:<3} {}\n").format(*players[i])

    return roster


def meta(type, fields=None):
    """Get available values from StatsAPI for use in other queries,
    or look up descriptions for values found in API results.

    For example, to get a list of leader categories to use when calling team_leaders():
    statsapi.meta('leagueLeaderTypes')
    """
    types = [
        "awards",
        "baseballStats",
        "eventTypes",
        "freeGameTypes",
        "gameStatus",
        "gameTypes",
        "hitTrajectories",
        "jobTypes",
        "languages",
        "leagueLeaderTypes",
        "logicalEvents",
        "metrics",
        "pitchCodes",
        "pitchTypes",
        "platforms",
        "positions",
        "reviewReasons",
        "rosterTypes",
        "runnerDetailTypes",
        "scheduleTypes",
        "scheduleEventTypes",
        "situationCodes",
        "sky",
        "standingsTypes",
        "statGroups",
        "statTypes",
        "violationTypes",
        "windDirection",
    ]
    if type not in types:
        raise ValueError("Invalid meta type. Available meta types: %s." % types)

    return get("meta", {"type": type})


def notes(endpoint):
    """Get notes for a given endpoint."""
    msg = ""
    if not endpoint:
        msg = "No endpoint specified."
    else:
        if not ENDPOINTS.get(endpoint):
            msg = "Invalid endpoint specified."
        else:
            msg += "Endpoint: " + endpoint + " \n"
            path_params = [k for k, v in ENDPOINTS[endpoint]["path_params"].items()]
            required_path_params = [
                k
                for k, v in ENDPOINTS[endpoint]["path_params"].items()
                if v["required"]
            ]
            if required_path_params == []:
                required_path_params = "None"

            query_params = ENDPOINTS[endpoint]["query_params"]
            required_query_params = ENDPOINTS[endpoint]["required_params"]
            if required_query_params == [[]]:
                required_query_params = "None"
            msg += "All path parameters: %s. \n" % path_params
            msg += (
                "Required path parameters (note: ver will be included by default): %s. \n"
                % required_path_params
            )
            msg += "All query parameters: %s. \n" % query_params
            msg += "Required query parameters: %s. \n" % required_query_params
            if "hydrate" in query_params:
                msg += "The hydrate function is supported by this endpoint. Call the endpoint with {'hydrate':'hydrations'} in the parameters to return a list of available hydrations. For example, statsapi.get('schedule',{'sportId':1,'hydrate':'hydrations','fields':'hydrations'})\n"
            if ENDPOINTS[endpoint].get("note"):
                msg += "Developer notes: %s" % ENDPOINTS[endpoint].get("note")

    return msg


def get(endpoint, params={}, force=False, *, request_kwargs={}):
    """Call MLB StatsAPI and return JSON data.

    This function is for advanced querying of the MLB StatsAPI,
    and is used by the functions in this library.
    """
    # Lookup endpoint from input parameter
    ep = ENDPOINTS.get(endpoint)
    if not ep:
        raise ValueError("Invalid endpoint (" + str(endpoint) + ").")

    url = ep["url"]
    logger.debug("URL: {}".format(url))

    path_params = {}
    query_params = {}

    # Parse parameters into path and query parameters, and discard invalid parameters
    for p, pv in params.items():
        if ep["path_params"].get(p):
            logger.debug("Found path param: {}".format(p))
            if ep["path_params"][p].get("type") == "bool":
                if str(pv).lower() == "false":
                    path_params.update({p: ep["path_params"][p].get("False", "")})
                elif str(pv).lower() == "true":
                    path_params.update({p: ep["path_params"][p].get("True", "")})
            else:
                path_params.update({p: str(pv)})
        elif p in ep["query_params"]:
            logger.debug("Found query param: {}".format(p))
            query_params.update({p: str(pv)})
        else:
            if force:
                logger.debug(
                    "Found invalid param, forcing into query parameters per force flag: {}".format(
                        p
                    )
                )
                query_params.update({p: str(pv)})
            else:
                logger.debug("Found invalid param, ignoring: {}".format(p))

    logger.debug("path_params: {}".format(path_params))
    logger.debug("query_params: {}".format(query_params))

    # Replace path parameters with their values
    for k, v in path_params.items():
        logger.debug("Replacing {%s}" % k)
        url = url.replace(
            "{" + k + "}",
            ("/" if ep["path_params"][k]["leading_slash"] else "")
            + v
            + ("/" if ep["path_params"][k]["trailing_slash"] else ""),
        )
        logger.debug("URL: {}".format(url))

    while url.find("{") != -1 and url.find("}") > url.find("{"):
        param = url[url.find("{") + 1 : url.find("}")]
        if ep.get("path_params", {}).get(param, {}).get("required"):
            if (
                ep["path_params"][param]["default"]
                and ep["path_params"][param]["default"] != ""
            ):
                logger.debug(
                    "Replacing {%s} with default: %s."
                    % (param, ep["path_params"][param]["default"])
                )
                url = url.replace(
                    "{" + param + "}",
                    ("/" if ep["path_params"][param]["leading_slash"] else "")
                    + ep["path_params"][param]["default"]
                    + ("/" if ep["path_params"][param]["trailing_slash"] else ""),
                )
            else:
                if force:
                    logger.warning(
                        "Missing required path parameter {%s}, proceeding anyway per force flag..."
                        % param
                    )
                else:
                    raise ValueError("Missing required path parameter {%s}" % param)
        else:
            logger.debug("Removing optional param {%s}" % param)
            url = url.replace("{" + param + "}", "")

        logger.debug("URL: {}".format(url))
    # Add query parameters to the URL
    if len(query_params) > 0:
        for k, v in query_params.items():
            logger.debug("Adding query parameter {}={}".format(k, v))
            sep = "?" if url.find("?") == -1 else "&"
            url += sep + k + "=" + v
            logger.debug("URL: {}".format(url))

    # Make sure required parameters are present
    satisfied = False
    missing_params = []
    for x in ep.get("required_params", []):
        if len(x) == 0:
            satisfied = True
        else:
            missing_params.extend([a for a in x if a not in query_params])
            if len(missing_params) == 0:
                satisfied = True
                break

    if not satisfied and not force:
        if ep.get("note"):
            note = "\n--Endpoint note: " + ep.get("note")
        else:
            note = ""

        raise ValueError(
            "Missing required parameter(s): "
            + ", ".join(missing_params)
            + ".\n--Required parameters for the "
            + endpoint
            + " endpoint: "
            + str(ep.get("required_params", []))
            + ". \n--Note: If there are multiple sets in the required parameter list, you can choose any of the sets."
            + note
        )

    if len(request_kwargs):
        logger.debug(
            "Including request_kwargs in requests.get call: {}".format(request_kwargs)
        )

    # Make the request
    r = requests.get(url, **request_kwargs)
    if r.status_code not in [200, 201]:
        r.raise_for_status()
    else:
        return r.json()

    return None
