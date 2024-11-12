from datetime import datetime, timedelta
from flask import json


# todo : tests data need to be dummy, so we should create a data generation function on conftest_file

def test_status_endpoint(client):
    """Test the status endpoint for correct HTTP response and data structure."""
    print(f'test_status_endpoint is running')
    response = client.get('/')
    data = json.loads(response.data)

    assert response.status_code == 200
    assert 'last_server_update' in data
    assert 'date_now' in data
    assert 'status' in data


def test_forecasts_endpoint_missing_parameters(client):
    """Test the forecasts endpoint without parameters should return error 400."""

    response = client.get('/forecasts')
    assert response.status_code == 400


def test_forecasts_endpoint_valid_request(client):
    """Test the forecasts endpoint with a valid request."""
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    then = (datetime.now() + timedelta(hours=24)).strftime('%Y-%m-%d %H:%M:%S')
    response = client.get(f'/forecasts?now={now}&then={then}')
    assert response.status_code == 200


def test_tomorrow_endpoint_invalid_date_format(client):
    """Test the tomorrow endpoint with an invalid date format."""
    response = client.get('/tomorrow?now=01-15-2024')
    print(response.json)
    assert response.status_code == 400


def test_tomorrow_endpoint_valid_date(client):
    """Test the tomorrow endpoint with a valid date."""
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    response = client.get(f'/tomorrow?now={now}')
    assert response.status_code == 200


def test_non_integer_lag(client):
    """
    Test the response when 'lag' parameter is not an integer.
    """
    response = client.get('/forecast_rmse_precision?lag=123.54')
    assert response.status_code == 400
    assert response.json == {'error': "'lag' value should be an integer"}


def test_valid_lag(client):
    """
    Test the response when 'lag' parameter is a valid integer.
    """

    response = client.get('/forecast_rmse_precision?lag=24')
    assert response.status_code == 200
    data = response.json
    assert 'rmse_values' in data
    assert 'percentage_accuracy' in data
