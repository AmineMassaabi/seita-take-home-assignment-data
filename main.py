import os
from datetime import datetime, timedelta
from flask import Flask, jsonify, request
from flask_bootstrap import Bootstrap
from flask_cors import CORS
from waitress import serve
from flask_compress import Compress

from src.utils.helpers import handle_request_errors, parse_date, get_transformed_data_frames, get_nearst_values_to_now, \
    get_difference_of_hour_between_two_dates, check_threshold
from src.weather_forecast import WEATHER_FORECAST_MODEL


def prepare_data_for_prediction(now: datetime, target_time: datetime):
    horizon_hours = (target_time - now).total_seconds() / 3600
    return round(horizon_hours)


def create_app():
    start_date = datetime.today().strftime('%d-%m-%Y %H:%M:%S')
    temperature, irradiance, wind_speed = get_transformed_data_frames()
    forecasting_model = WEATHER_FORECAST_MODEL()
    app = Flask(__name__, instance_relative_config=True)
    app.config['JSON_SORT_KEYS'] = False
    print('start_server')
    compress = Compress()
    compress.init_app(app)

    CORS(app)
    Bootstrap(app)
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    @app.errorhandler(404)
    def page_not_found(error):
        """ Return a custom message for Page Not Found (404) errors. """
        return 'This page does not exist', 404

    @app.route('/', methods=['GET'], endpoint='status')
    @handle_request_errors
    def hello():
        """ Return server status and current time. """
        now = datetime.today().strftime('%d-%m-%Y %H:%M:%S')
        return jsonify({'last_server_update': start_date, 'date_now': now, 'status': 200})

    @app.route('/forecasts', methods=['GET'], endpoint='forecasts')
    @handle_request_errors
    def get_forecasts():
        """
        Handle GET requests to fetch weather forecasts between 'now' and 'then'.
        nown and received passed on the query params should receive a datetime string
        """
        now = request.args.get('now')
        then = request.args.get('then')

        if not now or not then:
            return jsonify({'error': 'Missing required parameters'}), 400

        try:
            now = parse_date(date=now)
            then = parse_date(date=then)
        except:
            return jsonify({'error': 'Invalid date format, please use YYYY-MM-DD HH:MM:SS'}), 400

        assert now <= then <= now + timedelta(
            hours=48), "'then' value should be between 'now' value and 'now' + 48 hours"
        # todo now value validation (check if value in our data range)

        calculation_mesures = get_nearst_values_to_now(temperature, irradiance, wind_speed, now)
        lag = get_difference_of_hour_between_two_dates(now, then)
        forecasting_result = forecasting_model.forecast_model(now, calculation_mesures, lag)

        return jsonify(forecasting_result)

    @app.route('/tomorrow', methods=['GET'], endpoint='tomorrow')
    @handle_request_errors
    def get_tomorrow():
        """
        Provide a weather forecast for the next day based on the 'now' query parameter should receive a datetime string.
        """

        now = request.args.get('now')
        try:
            now = parse_date(date=now)
        except:
            return jsonify({'error': 'Invalid date format, please use YYYY-MM-DD HH:MM:SS'}), 400

        # todo now value validation (check if value in our data range)

        calculation_mesures = get_nearst_values_to_now(temperature, irradiance, wind_speed, now)
        forecasted_result = forecasting_model.forecast_model(now, calculation_mesures)

        return jsonify(check_threshold(forecasted_result))

    return app


if __name__ == "__main__":
    serve(create_app(), host="0.0.0.0", port=5000)
