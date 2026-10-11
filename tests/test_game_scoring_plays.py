import statsapi


def fake_game_data():
    """The smallest response game_scoring_play_data will walk without raising."""
    return {
        "gameData": {
            "teams": {
                "home": {"name": "Home Team"},
                "away": {"name": "Away Team"},
            }
        },
        "liveData": {
            "plays": {
                "scoringPlays": [7],
                "allPlays": [
                    {
                        "atBatIndex": 7,
                        "result": {
                            "description": "Batter homers.",
                            "awayScore": 0,
                            "homeScore": 1,
                        },
                        "about": {
                            "halfInning": "bottom",
                            "inning": 3,
                            "endTime": "2026-10-09T01:00:00.000Z",
                        },
                    }
                ],
            }
        },
    }


def test_game_scoring_play_data_omits_timecode_when_not_given(mocker):
    mock_get = mocker.patch("statsapi.get", return_value=fake_game_data())

    statsapi.game_scoring_play_data(123)

    params = mock_get.call_args[0][1]
    assert "timecode" not in params


def test_game_scoring_play_data_passes_timecode_through(mocker):
    mock_get = mocker.patch("statsapi.get", return_value=fake_game_data())

    statsapi.game_scoring_play_data(123, "20261009_015302")

    endpoint, params = mock_get.call_args[0]
    assert endpoint == "game"
    assert params["timecode"] == "20261009_015302"
    assert params["gamePk"] == 123


def test_game_scoring_plays_forwards_timecode(mocker):
    mock_data = mocker.patch(
        "statsapi.game_scoring_play_data",
        return_value={"home": {"name": "H"}, "away": {"name": "A"}, "plays": []},
    )

    statsapi.game_scoring_plays(123, "20261009_015302")

    mock_data.assert_called_once_with(123, "20261009_015302")


def test_game_scoring_plays_still_works_without_a_timecode(mocker):
    mock_data = mocker.patch(
        "statsapi.game_scoring_play_data",
        return_value={"home": {"name": "H"}, "away": {"name": "A"}, "plays": []},
    )

    statsapi.game_scoring_plays(123)

    mock_data.assert_called_once_with(123, None)
