import pytest
from datetime import datetime, timedelta
from flask import json, jsonify

from main import create_app


@pytest.fixture
def client():
    print(f'client is running')
    app = create_app()
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


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
    print(f'test_forecasts_endpoint_missing_parameters is running')

    response = client.get('/forecasts')
    assert response.status_code == 400


def test_forecasts_endpoint_wrong_date_format(client):
    """Test the forecasts endpoint with incorrect date format."""
    print(f'test_forecasts_endpoint_wrong_date_format is running')
    response = client.get('/forecasts?now=2022-09-01&then=2022-09-02')
    assert response.status_code == 400


def test_forecasts_endpoint_valid_request(client):
    """Test the forecasts endpoint with a valid request."""
    print(f'test_forecasts_endpoint_valid_request is running')
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    then = (datetime.now() + timedelta(hours=24)).strftime('%Y-%m-%d %H:%M:%S')
    response = client.get(f'/forecasts?now={now}&then={then}')
    assert response.status_code == 200


def test_tomorrow_endpoint_invalid_date_format(client):
    """Test the tomorrow endpoint with an invalid date format."""
    print(f'test_tomorrow_endpoint_invalid_date_format is running')
    response = client.get('/tomorrow?now=2024-01-01')
    assert response.status_code == 400


def test_tomorrow_endpoint_valid_date(client):
    """Test the tomorrow endpoint with a valid date."""
    print(f'test_tomorrow_endpoint_valid_date is running')
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    response = client.get(f'/tomorrow?now={now}')
    assert response.status_code == 200
