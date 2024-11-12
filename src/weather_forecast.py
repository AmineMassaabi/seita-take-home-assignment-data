from copy import copy
from datetime import timedelta

import numpy as np
import pandas as pd
from statsmodels.regression.linear_model import OLS
from timetomodel import speccing, create_fitted_model, ModelState, make_forecast_for
from timetomodel.featuring import construct_features
from timetomodel.transforming import Transformation
import statsmodels.api as sm

from src.utils.consts import target_variables, path_url


class MyDFPostProcessing(Transformation):
    """
    Custom transformation class to preprocess DataFrame specific to a given sensor.
    Applies filtering, sorting, and de-duplication.
    """
    def __init__(self, sensor):
        self.sensor = sensor

    def transform_dataframe(self, df: pd.DataFrame):
        """Keep the most recent observation, drop duplicates, filter by sensor"""

        df = df[df['sensor'] == self.sensor]
        return (
            df.sort_values(by=["belief_horizon_in_sec"], ascending=True)
            .drop_duplicates(subset=["event_start"], keep="first")
            .sort_values(by=["event_start"])
        )


def get_speccing_object_series_specs(df, sensor):
    return speccing.ObjectSeriesSpecs(
        data=pd.Series(
            index=df['exact_time'],
            data=list(df['event_value']),
        ),
        name=sensor,
        resampling_config=dict(
            downsampling_method="first",
            event_resolution=timedelta(hours=0),
        ),
        interpolation_config=dict(method="pad", limit=3),
    )


def get_speccing_csv_series_specs(sensor):
    """
    Configure specifications for loading and processing data from a CSV file using the CSVFileSeriesSpecs class
    from timetomodel.
    """
    return speccing.CSVFileSeriesSpecs(
        file_path=path_url,
        time_column='event_start',
        value_column='event_value',
        name=sensor,
        post_load_processing=MyDFPostProcessing(sensor),
        read_csv_config={'parse_dates': ["event_start"]},
        # feature_transformation=BoxCoxTransformation(lambda2=0.1)
    )


class WEATHER_FORECAST_MODEL():
    """
    A model for forecasting weather variables such as temperature, irradiance, and wind speed.
    Initializes data series from specified sources and prepares them for modeling.
    """
    def __init__(self):

        """
        I commented the code below because I worked ObjectSeriesSpecs first and changed  to CSVFileSeriesSpecs
        """
        # def __init__(self, temperature_data=None, irradiance_data=None, wind_speed_data=None):
        # also we can work wih CSVFileSeriesSpecs inplace of ObjectSeriesSpecs
        # temperature_data_specs = get_speccing_object_series_specs(temperature_data, 'temperature')
        # irradiance_data_specs = get_speccing_object_series_specs(irradiance_data, 'irradiance')
        # wind_speed_data_specs = get_speccing_object_series_specs(wind_speed_data, 'wind_speed')
        # temperature_series = temperature_data_specs.load_series(expected_frequency=timedelta(hours=1))
        # irradiance_series = irradiance_data_specs.load_series(expected_frequency=timedelta(hours=1))
        # wind_speed_series = wind_speed_data_specs.load_series(expected_frequency=timedelta(hours=1))

        self.fitted_model = None
        self.temperature_series = get_speccing_csv_series_specs('temperature').load_series(
            expected_frequency=timedelta(hours=1))
        self.temperature_object_series = speccing.ObjectSeriesSpecs(self.temperature_series, name="temperature")
        self.irradiance_series = get_speccing_csv_series_specs('irradiance').load_series(
            expected_frequency=timedelta(hours=1))
        self.irradiance_object_series = speccing.ObjectSeriesSpecs(self.irradiance_series, name="irradiance")
        self.wind_speed_series = get_speccing_csv_series_specs('wind speed').load_series(
            expected_frequency=timedelta(hours=1))
        self.wind_speed_object_series = speccing.ObjectSeriesSpecs(self.wind_speed_series, name="wind speed")
        self.fitted_models = {}

    def get_model_specs(self, lag=24, target_variable="temperature"):
        """
        Generate specifications for the forecasting model, including setting up the outcome variable and regressors.
        """

        # Define the time range for training and testing data
        start_of_training = self.temperature_series.index[0]  # First date in the temperature series
        end_of_testing = self.temperature_series.index[-1]  # Last date in the temperature series

        if target_variable == 'temperature':
            outcome_var = copy(self.temperature_object_series)
            regressors = [copy(self.irradiance_object_series), copy(self.wind_speed_object_series)]
        elif target_variable == 'irradiance':
            outcome_var = copy(self.irradiance_object_series)
            regressors = [copy(self.temperature_object_series), copy(self.wind_speed_object_series)]
        else:
            outcome_var = copy(self.wind_speed_object_series)
            regressors = [copy(self.temperature_object_series), copy(self.irradiance_object_series)]

        # todo : test on other regression models ( like VAR for Multivariate Forecasting from statsmodels.tsa.api)
        model_specs = speccing.ModelSpecs(
            model=OLS,
            outcome_var=outcome_var,
            frequency=timedelta(hours=1),
            horizon=timedelta(hours=lag),  # Forecast horizon based on calculated lag
            lags=[lag],  # Use only the lag equal to the forecast horizon
            regressors=regressors,
            start_of_training=start_of_training + timedelta(hours=lag),
            end_of_testing=end_of_testing - timedelta(hours=lag),
            ratio_training_testing_data=0.80,  # Train-test split ratio
        )
        return model_specs

    def train_models(self, lag=24):
        """
        Train models for each target variable based on generated specifications.
        """
        for target_variable in target_variables:
            model_specs = self.get_model_specs(lag=lag, target_variable=target_variable)
            fitted_model = create_fitted_model(model_specs, f"Weather Forecast {target_variable} Model")
            self.fitted_models[target_variable] = fitted_model

    def evaluate_models(self, lag):
        """
        We transformed evaluate_models from timetomodel to get adequate output
        :return: rmse values for each model
        """
        rmse_values = {}
        percentage_accuracy = {}
        for target_variable in target_variables:
            m1 = ModelState(self.fitted_models[target_variable], self.get_model_specs(lag=lag,
                                                                                      target_variable=target_variable))
            fitted_m1, m1_specs = m1.split()
            regression_frame = construct_features(time_range="test", specs=m1_specs)
            x_test = regression_frame.iloc[:, 1:]
            y_test = np.array(regression_frame.iloc[:, 0])
            try:
                y_hat_test = fitted_m1.predict(x_test)
            except TypeError:
                y_hat_test = fitted_m1.predict(start=x_test.index[0], end=x_test.index[-1], exog=x_test)

            if m1_specs.outcome_var.feature_transformation is not None:
                y_test = m1_specs.outcome_var.feature_transformation.back_transform_value(y_test)
                y_hat_test = m1_specs.outcome_var.feature_transformation.back_transform_value(y_hat_test)
            target_range = np.max(y_test) - np.min(y_test)

            rmse_values[target_variable] = round(sm.tools.eval_measures.rmse(y_test, y_hat_test, axis=0), 4)
            percentage_accuracy[target_variable] = round((1.0 - (rmse_values[target_variable] / target_range)) * 100)
        return rmse_values, percentage_accuracy

    def forecast_model(self, now, calculation_mesures, lag=24):
        """
        Generate a forecast for specified weather variables using trained models and current conditions.
        """
        self.train_models(lag)
        features = pd.DataFrame(
            index=pd.date_range(start=now, end=now, freq="H"),
            data=calculation_mesures,
        ).iloc[0]

        forecasted_values = {}
        for target_variable in target_variables:
            model_specs = self.get_model_specs(lag, target_variable=target_variable)
            forecasted_value = make_forecast_for(
                specs=model_specs,
                features=features,
                model=self.fitted_models[target_variable]
            )
            forecasted_values[target_variable] = forecasted_value
        return forecasted_values
