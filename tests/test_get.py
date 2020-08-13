import statsapi
import pytest
import requests.exceptions
import responses


def fake_dict():
    return {
        "foo": {
            "url": "http://www.foo.com",
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


def test_get_calls_correct_url(mocker):
    # mock the ENDPOINTS dictionary
    mocker.patch.dict("statsapi.ENDPOINTS", fake_dict(), clear=True)
    # mock the requests object
    mock_req = mocker.patch("statsapi.requests", autospec=True)

    statsapi.get("foo", {"bar": "baz"})
    mock_req.get.assert_called_with("http://www.foo.com?bar=baz")


@responses.activate
def test_get_server_error(mocker):
    # mock the ENDPOINTS dictionary
    mocker.patch.dict("statsapi.ENDPOINTS", fake_dict(), clear=True)
    responses.add(responses.GET, "http://www.foo.com?bar=baz", status=500)

    with pytest.raises(requests.exceptions.HTTPError):
        statsapi.get("foo", {"bar": "baz"})


def test_get_invalid_endpoint(mocker):
    # mock the ENDPOINTS dictionary
    mocker.patch.dict("statsapi.ENDPOINTS", fake_dict(), clear=True)
    # mock the requests object
    mock_req = mocker.patch("statsapi.requests", autospec=True)
    # invalid endpoint
    with pytest.raises(ValueError):
        statsapi.get("bar", {"foo": "baz"})

    # TODO: add test for path requirement not met
    # TODO: add test for required params
