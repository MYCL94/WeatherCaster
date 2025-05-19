import requests
from config import env
from enum import Enum

from model_definition.response_types import (Coordinates, GeocodingResult,
      WeatherData, HourlyForecastData, DailyForecastData)

class ForecastType(str, Enum):
    """Lists all available forecast types and their corresponding API endpoint URLs."""
    CURRENT = "https://api.openweathermap.org/data/2.5/weather" # Everything related to today
    TOMORROW = "https://pro.openweathermap.org/data/2.5/forecast/hourly" # In case LLM chooses, everything related to tomorrow same as hourly
    HOURLY = "https://pro.openweathermap.org/data/2.5/forecast/hourly" # Hourly forecast for 4 days (max. 96 timestamps)
    DAILY = "https://api.openweathermap.org/data/2.5/forecast/daily" # Daily Forecast 16 Days

class WeatherAPIClient:
    def __init__(self) -> None:
        self.api_key = env.WEATHER_API_KEY
        self.geocoding_url = "http://api.openweathermap.org/geo/1.0/direct"
        self.max_hourly_forecast_items = env.MAX_HOURLY_FORECAST_ITEMS

    def _get_coordinates(self, location_name: str) -> GeocodingResult | None:
        """Gets coordinates (latitude and longitude), name, and country for a given location.

        This tool is essential for converting a human-readable location name into
        geographical coordinates required by other weather tools.

        Args:
            location_name (str): The name of the location (e.g., "London", "Paris, FR").

        Returns:
            GeocodingResult | None: A GeocodingResult object containing 'coordinates' (with 'latitude' and 'longitude'),
                                    'name', and 'country' if the location is found.
                                    Returns None if the location cannot be found or an error occurs.
        """
        params = {
            'q': location_name,
            'limit': 1, # Get the most relevant location
            'appid': self.api_key
        }
        try:
            response = requests.get(self.geocoding_url, params=params)
            response.raise_for_status()  # Raise an exception for HTTP errors
            data = response.json()

            if data and isinstance(data, list) and len(data) > 0:
                # Assuming the first result is the most relevant
                location_data = data[0]
                return GeocodingResult(coordinates=
                                    (Coordinates(lat=location_data.get('lat'),
                                                    lon=location_data.get('lon'))),
                                    name=location_data.get('name'),
                                    country=location_data.get('country'))
            else:
                print(f"Geocoding: No coordinates found for {location_name}")
                return None
        except requests.exceptions.RequestException as e:
            print(f"Geocoding request error for {location_name}: {e}")
            return None
        except Exception as e:
            print(f"Error during geocoding for {location_name}: {e}")
            return None
        
    def _get_forecast_type(self, forecast_type: str) -> ForecastType | None:
        """Gets the correct API endpoint URL for a given forecast type.

        Args:
            forecast_type (str): The type of forecast (e.g., "current", "hourly", "daily").

        Returns:
            ForecastType | None: The API endpoint URL for the specified forecast type.
                            Returns None if the forecast type is not recognized.
                            Input `forecast_type` is case-insensitive.
        """
        try:
            # ("current" -> "CURRENT")
            member_name = forecast_type.strip().upper()

            # Access the enum member by its name (ForecastType['CURRENT']).
            enum_member = ForecastType[member_name]

            return enum_member
        except KeyError:
            valid_types = [member.name.lower() for member in ForecastType]
            print(f"Invalid forecast type: '{forecast_type}'. Must be one of {valid_types}.")
            return None
        except Exception as e:
            print(f"An unexpected error occurred while processing forecast type '{forecast_type}': {e}")
            return None

    def get_weather_forecast(self, location_name: str, forecast_type: str) -> WeatherData | HourlyForecastData | DailyForecastData | None:
        """Gets detailed current weather forecast for a given location using its latitude and longitude.

        Provides comprehensive weather data, including temperature, conditions, wind, etc.

        Args:
            location_name (str): The name of the location (e.g., "London", "Paris, FR").
            forecast_type_api (str): The API endpoint URL for the specified forecast type.

        Returns:
            Union[WeatherData, HourlyForecastData, DailyForecastData, None]:
                An object containing detailed weather data, specific to the forecast type.
                - WeatherData for current weather.
                - HourlyForecastData for hourly forecasts.
                - DailyForecastData for daily forecasts.
                Returns None if data cannot be retrieved or an error occurs.
        """
        georesult = self._get_coordinates(location_name)
        forecast_type_api = self._get_forecast_type(forecast_type)
        
        if not georesult or not georesult.coordinates or georesult.coordinates.lat is None or georesult.coordinates.lon is None:
            print(f"Could not get valid coordinates for {location_name}")
            return None
        coordinates = georesult.coordinates

        params = {
            'lat': coordinates.lat,
            'lon': coordinates.lon,
            'appid': self.api_key,
            'units': "metric",
        }
        
        api_url_str = forecast_type_api.value

        try:
            response = requests.get(api_url_str, params=params)
            response.raise_for_status()
            response_json = response.json()

            if forecast_type_api == ForecastType.CURRENT:
                return WeatherData(**response_json)
            elif forecast_type_api == ForecastType.HOURLY or forecast_type_api == ForecastType.TOMORROW:
                # limit the number of hourly forecast items.
                # The API can return up to 96 hourly forecasts (4 days).
                # We cap it to MAX_HOURLY_FORECAST_ITEMS (e.g., X hours)
                # to provide a more manageable dataset to the LLM. The context lenght
                # is exceeded in my testing with llama3.1:8b for already 12 items
                MAX_HOURLY_FORECAST_ITEMS = self.max_hourly_forecast_items

                if 'list' in response_json and isinstance(response_json['list'], list):
                    response_json['list'] = response_json['list'][:MAX_HOURLY_FORECAST_ITEMS]
                    # Update to new number of items
                    if 'cnt' in response_json:
                        response_json['cnt'] = len(response_json['list'])
                return HourlyForecastData(**response_json)
            elif forecast_type_api == ForecastType.DAILY:
                return DailyForecastData(**response_json)
            else:
                print(f"Unknown forecast type API URL: {api_url_str} for location {location_name}")
                return None

        except requests.exceptions.RequestException as e:
            print(f"Weather API request error for {location_name} ({api_url_str}): {e}")
            return None
        except Exception as e: 
            print(f"Error processing weather data for {location_name} ({api_url_str}): {e}")
            return None