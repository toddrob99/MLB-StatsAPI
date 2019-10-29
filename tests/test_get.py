import statsapi


def fake_dict():
    return {
        "foo": {
            "url": "www.foo.com",
            "path_params": {
                "ver": {
                    "type": "str",
                    "default": "v1",
                    "leading_slash": False,
                    "trailing_slash": False,
                    "required": True,
                }
            },
            "query_params": ["bar"],
            "required_params": [[]],
        }
    }


def test_get_returns_dictionary(mocker):
    # mock the ENDPOINTS dictionary
    mocker.patch.dict("statsapi.ENDPOINTS", fake_dict(), clear=True)
    # mock the requests object
    mock_req = mocker.patch("statsapi.requests", autospec=True)
    # mock the status code to always be 200
    mock_req.get.return_value.status_code = 200

    result = statsapi.get("foo", {"bar": "baz"})
    # assert that result is the same as the return value from calling the json method of a response object
    assert result == mock_req.get.return_value.json.return_value
