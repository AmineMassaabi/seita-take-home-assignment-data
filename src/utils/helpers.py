import traceback
from datetime import datetime

import pandas
import pandas as pd
from flask import jsonify
from dateutil.parser import parse

from src.utils.consts import csv_url, THRESHOLDS, path_url


def handle_request_errors(f):
    """
    Decorator function to handle exceptions that occur within Flask routes.
    It logs the error and returns a JSON response indicating the failure.
    """
    def wrapper(*args, **kwargs):
        try:
            print(f'start {f.__name__}')
            return f(*args, **kwargs)
        except:
            error_msg = f'Error on {f.__name__} \n{traceback.format_exc()}'
            traceback.print_exc()
            response = {
                'result': 'failed',
                'status': 'down',
                'error': error_msg

            }
            return jsonify(response), 500

    return wrapper


def parse_date(date: str) -> datetime:
    """
    Parse a string date into a datetime object, assuming the year is first.
    """
    # return pd.to_datetime(date, yearfirst=True, utc=True).to_pydatetime()
    return parse(date, yearfirst=True, ignoretz=True)


def get_transformed_data_frames(get_online: bool = False) -> [pd.DataFrame]:
    """
    Fetch weather data from a CSV, either online from the original git repo or local,
    then transform and split by sensor type.
    """
    if get_online:
        weather_data = pandas.read_csv(csv_url)
    else:
        weather_data = pandas.read_csv(path_url)
    transformed_weather_data = data_transform(weather_data)
    [temperature, irradiance, wind_speed] = data_split(transformed_weather_data)
    return [temperature, irradiance, wind_speed]


def data_transform(df: pd.DataFrame) -> pd.DataFrame:
    """
    Transform the DataFrame by parsing event start times and adjusting for belief horizon.
    """
    df['event_start'] = pd.to_datetime(df['event_start'])
    df['exact_time'] = df['event_start'] - pd.to_timedelta(df['belief_horizon_in_sec'], unit='s')
    df = df.rename({'belief_horizon_in_sec': 'horizon'})
    return df


def data_split(df: pd.DataFrame) -> [pd.DataFrame]:
    """
    Split the data into separate DataFrames for temperature, irradiance, and wind speed.
    """
    temperature = df[df['sensor'] == 'temperature']
    irradiance = df[df['sensor'] == 'irradiance']
    wind_speed = df[df['sensor'] == 'wind speed']
    return [temperature, irradiance, wind_speed]


def extract_nearset_value_to_date(table, given_date):
    """
    Extract the closest event value to a given date from the DataFrame.
    """
    # table = table[table.event_start == given_date]
    return table.loc[(table['exact_time'] - pd.to_datetime(given_date, utc=True)).abs().idxmin()]['event_value']


def get_nearst_values_to_now(temperature, irradiance, wind_speed, now):
    """
    Retrieve the closest data points to the current date ('now') for all sensors.
    """
    # looked_date = pd.date_range(start=now, end=now, freq="H")
    temperature_value = extract_nearset_value_to_date(temperature, now)
    irradiance_value = extract_nearset_value_to_date(irradiance, now)
    wind_speed_value = extract_nearset_value_to_date(wind_speed, now)

    return {'temperature': temperature_value, 'irradiance': irradiance_value, 'wind_speed': wind_speed_value}


def get_difference_of_hour_between_two_dates(now, then):
    """
    Calculate the difference in hours between two datetime objects.
    """
    # looked_date = pd.date_range(start=now, end=now, freq="H")
    difference = round((then - now).total_seconds() / 3600)
    return difference


def check_threshold(forecasted_results):
    """
    Check if the forecasted results exceed predefined threshold values.
    Returns a dictionary indicating whether each condition is met.
    """
    return {
        "warm": bool(forecasted_results['temperature'] > THRESHOLDS['warm']),
        "sunny": bool(forecasted_results['irradiance'] > THRESHOLDS['sunny']),
        "windy": bool(forecasted_results['wind speed'] > THRESHOLDS['windy'])
    }
