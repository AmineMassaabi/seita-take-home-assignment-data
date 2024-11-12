csv_url = 'https://raw.githubusercontent.com/SeitaBV/assignment-data-engineering/refs/heads/main/weather.csv'
path_url = 'weather.csv'
target_variables = ['temperature', 'irradiance', 'wind speed']

THRESHOLDS = {
    "warm": 20,
    "sunny": 300,
    "windy": 10
}
