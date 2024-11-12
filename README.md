# Seita data engineering assignment

Thanks for taking the time to review my application at Seita Energy Flexibility!

# Weather Forecast API

This project provides a weather forecast API for accessing weather data, designed as part of a data engineering assignment for Seita Energy Flexibility. The application utilizes **Timely-Beliefs** for structured data representation of weather forecasts and **FlexMeasures** for embedding API endpoints.

## Table of Contents
- [Features](#features)
- [Project Structure](#project-structure)
- [Setup](#setup)
- [Future Improvements](#future-improvements)

---


## Features

- **Structured Forecast Representation**: Represents forecasts with Timely-Beliefs, supporting complex temporal data handling.
- **REST API Endpoints**: Provides endpoints for frontend developers to easily fetch JSON responses with weather forecasts.
- **Scalable and Modular Design**: The project is built with a modular structure to support scalability and easy maintenance.
- **Configurable and Extendable**: Uses a configuration file for easy adjustments and supports plugin extensions.

## Project Structure



seita-take-home-assignment-data/\n

├── data/           

│   └── weather_forecast.csv    # CSV data file containing weather forecasts

│

├── my_weather_plugin/          

│   ├── __init__.py

│   ├── consts.py                # Constants for configurations or settings

│   ├── helpers.py               # Helper functions for data processing

│   ├── weather_forecast.py      # Main module for processing weather forecasts

│   └── tests/                   # Unit tests for the plugin

│       ├── __init__.py

│       ├── conftest.py          # Tests configuration

│       └── test_app.py          # The application setup and API functionality Tests

│

├── docker-compose.yml           # Docker Compose configuration to run the app and Test

├── Dockerfile                   # Dockerfile to build the app container

├── main.py                      # Main entry point to run the application

├── README.md                    # Project documentation

├── requirements.txt             # Dependencies for the project

└── test.dockerfile              # Dockerfile for testing the application

## Setup

### Prerequisites

- Docker and Docker Compose installed on your machine.

### Installation and Running with Docker

1. **Clone the Repository**
   ```bash
   git clone https://github.com/AmineMassaabi/weather-forecast-api.git
   cd weather-forecast-api
   ```
2. **Build the Docker Image and Start running Test**
   ```bash
   docker-compose up --build
   ```

## Future Improvements
- Error Handling and Validation: Improve error responses for invalid requests.
- Caching: Implement caching for frequently requested forecasts to improve performance.
- Additional Forecast Types: Extend the model to handle additional weather data (e.g., humidity, precipitation).
- Authentication: Add authentication for production environments to limit access.

### Thanks in advance 
