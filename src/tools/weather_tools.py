import logging
from datetime import datetime, timezone
from typing import List
import httpx
from enum import Enum
from configs.config import env

from model_definition.final_response import CurrentWeather, DailyWeather, HourlyWeather, WeatherForecast, WindInfo, DaylightInfo
from model_definition.response_types import Coordinates, GeocodingResult, WeatherData, HourlyForecastData, DailyForecastData

logger = logging.getLogger(__name__)

class ForecastType(str, Enum):
    """Lists all available forecast types and their corresponding API endpoint URLs."""
    CURRENT = "https://api.openweathermap.org/data/2.5/weather" # Everything related to today
    HOURLY = "https://pro.openweathermap.org/data/2.5/forecast/hourly" # Hourly forecast for 4 days (max. 96 timestamps)
    DAILY = "https://api.openweathermap.org/data/2.5/forecast/daily" # Daily Forecast 16 Days
    TOMORROW = "https://api.openweathermap.org/data/2.5/forecast/daily" # For "tomorrow" queries, data is fetched using the daily forecast

class ForecastRange(str, Enum):
    """Lists all available forecast types and their corresponding API endpoint URLs."""
    CURRENT = "current"
    HOURLY = "hourly"
    DAILY = "daily"
    TOMORROW = "tomorrow"

def get_weather_emoji(icon_id: str) -> str:
    """Maps an OpenWeatherMap icon ID to an appropriate emoji.
    
    Reference: https://openweathermap.org/weather-conditions
    Args:
        icon_id (str): The icon ID from the OpenWeatherMap API)
    
    Returns:
        str: The corresponding emoji for the given icon ID.       
    """
    
    icon_map = {
        # Day icons
        "01d": "☀️",  # clear sky
        "02d": "🌤️",  # few clouds
        "03d": "☁️",  # scattered clouds
        "04d": "🌥️",  # broken clouds / overcast clouds
        "09d": "🌦️",  # shower rain
        "10d": "🌧️",  # rain
        "11d": "⛈️",  # thunderstorm
        "13d": "❄️",  # snow
        "50d": "🌫️",  # mist
        # Night icons
        "01n": "🌙",  # clear sky
        "02n": "☁️",  # few clouds
        "03n": "☁️",  # scattered clouds
        "04n": "🌥️",  # broken clouds / overcast clouds
        "09n": "🌦️",  # shower rain
        "10n": "🌧️",  # rain
        "11n": "⛈️",  # thunderstorm
        "13n": "❄️",  # snow
        "50n": "🌫️",  # mist
    }
    return icon_map.get(icon_id, "❓") # Default emoji if icon_id is unknown

class WeatherAPIClient:
    def __init__(self) -> None:
        self.api_key = env.WEATHER_API_KEY
        self.geocoding_url = "http://api.openweathermap.org/geo/1.0/direct"
        self.max_hourly_forecast_items = env.MAX_HOURLY_FORECAST_ITEMS

    async def _get_coordinates(self, location_name: str) -> GeocodingResult | None:
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
            async with httpx.AsyncClient() as client:
                response = await client.get(self.geocoding_url, params=params)
                response.raise_for_status()
                data = response.json()

                if data and isinstance(data, list) and len(data) > 0:
                    location_data = data[0]
                    return GeocodingResult(coordinates=Coordinates(lat=location_data.get('lat'), lon=location_data.get('lon')),
                                           name=location_data.get('name'),
                                           country=location_data.get('country')
                    )
                else:
                    logger.warning(f"Geocoding: No coordinates found for {location_name}")
                    return None
        except httpx.RequestError as e:
            logger.error(f"Geocoding request error for {location_name}: {e}", exc_info=True)
            return None
        except Exception as e:
            logger.error(f"Error during geocoding for {location_name}: {e}", exc_info=True)
            return None

    def _transform_api_data_to_weather_forecast(self,
                                                location_name: str,
                                                current_weather_api_model: WeatherData | None,
                                                hourly_forecast_api_model: HourlyForecastData | None,
                                                daily_forecast_api_model: DailyForecastData | None
                                                ) -> WeatherForecast | None:
        """Transforms raw API data into a WeatherForecast object.
        
        Args: 
            location_name (str): The name of the location (e.g., "London", "Paris, FR").
            currently_weather_api_model (WeatherData): Current weather data from the API.
            hourly_forecast_api_model (HourlyForecastData): Hourly forecast data from the API.
            daily_forecast_api_model (DailyForecastData): Daily forecast data from the API.

        Returns:
            WeatherForecast | None
        """
        current_weather: CurrentWeather | None = None
        hourly_forecast_list: List[HourlyWeather] = []
        daily_forecast_list: List[DailyWeather] = []

        if current_weather_api_model:
            weather_item = current_weather_api_model.weather[0]
            condition_str = weather_item.description.capitalize()
            current_weather = CurrentWeather(
                location=current_weather_api_model.name,
                date_time=datetime.fromtimestamp(current_weather_api_model.dt, tz=timezone.utc),
                condition=condition_str,
                emoji=get_weather_emoji(weather_item.icon),
                temperature=current_weather_api_model.main.temp,
                feels_like_temperature=current_weather_api_model.main.feels_like,
                high_temperature=current_weather_api_model.main.temp_max,
                low_temperature=current_weather_api_model.main.temp_min,
                wind=WindInfo(
                    speed=current_weather_api_model.wind.speed,
                    direction=current_weather_api_model.wind.deg
                ),
                humidity=current_weather_api_model.main.humidity,
                pressure=current_weather_api_model.main.pressure,
                daylight=DaylightInfo(
                    sunrise=datetime.fromtimestamp(current_weather_api_model.sys.sunrise, tz=timezone.utc),
                    sunset=datetime.fromtimestamp(current_weather_api_model.sys.sunset, tz=timezone.utc)
                )
            )

        if hourly_forecast_api_model and hourly_forecast_api_model.list:
            # Limit to the configured max_hourly_forecast_items (e.g., 10 for next 10 hours)
            for item in hourly_forecast_api_model.list[:self.max_hourly_forecast_items]:
                weather_item = item.weather[0]
                condition_str = weather_item.description.capitalize()
                hourly_forecast_list.append(HourlyWeather(
                    time=datetime.fromtimestamp(item.dt, tz=timezone.utc),
                    temperature=item.main.temp,
                    condition=condition_str,
                    emoji=get_weather_emoji(weather_item.icon),
                    wind=WindInfo(speed=item.wind.speed, direction=item.wind.deg),
                    humidity=item.main.humidity,
                    pressure=item.main.pressure
                ))

        if daily_forecast_api_model and daily_forecast_api_model.list:
            for item in daily_forecast_api_model.list:
                sunrise_time = datetime.fromtimestamp(item.sunrise, tz=timezone.utc) if item.sunrise else (current_weather.daylight.sunrise if current_weather and current_weather.daylight else None)
                sunset_time = datetime.fromtimestamp(item.sunset, tz=timezone.utc) if item.sunset else (current_weather.daylight.sunset if current_weather and current_weather.daylight else None)
                weather_item = item.weather[0]
                condition_str = weather_item.description.capitalize()
                daily_forecast_list.append(DailyWeather(
                    forecast_date=datetime.fromtimestamp(item.dt, tz=timezone.utc).date(),
                    max_temperature=item.temp.max, min_temperature=item.temp.min,
                    condition=condition_str, emoji=get_weather_emoji(weather_item.icon),
                    wind=WindInfo(speed=item.speed if item.speed else 0.0, direction=item.deg if item.deg else 0),
                    humidity=item.humidity, daylight=DaylightInfo(sunrise=sunrise_time, sunset=sunset_time)
                ))

        if current_weather or hourly_forecast_list or daily_forecast_list:
            return WeatherForecast(current=current_weather, hourly=hourly_forecast_list, daily=daily_forecast_list)
        else:
            logger.warning(f"Failed to retrieve sufficient weather data for {location_name} to transform.")
            return None

    async def get_weather_forecast(self, location_name: str, forecast_range: ForecastRange) -> WeatherForecast | None:
        """
        Gets comprehensive weather forecast data (current, hourly, daily) for a given location.

        This tool performs multiple API calls internally to gather all necessary data
        and then transforms it into a unified, simplified WeatherForecast object.

        Args:
            location_name (str): The name of the location (e.g., "London", "Paris, FR").
            forecast_range (str): The timerange selected by the user. Available options are "current", "hourly", and "daily".

        Returns:
            Optional[WeatherForecast]: A simplified Pydantic model containing current,
                                     hourly, and daily weather data. Returns None if
                                     data cannot be retrieved or an error occurs.
        """
        georesult = await self._get_coordinates(location_name)
        if not georesult or not georesult.coordinates:
            logger.warning(f"Could not get valid coordinates for {location_name}. Cannot fetch weather.")
            return None

        lat, lon = georesult.coordinates.lat, georesult.coordinates.lon

        current_weather_api_model: WeatherData | None = None
        hourly_forecast_api_model: HourlyForecastData | None = None
        daily_forecast_api_model: DailyForecastData | None = None

        async with httpx.AsyncClient() as client:
            # 1. Fetch Current Weather
            current_params = {
                "lat": lat,
                "lon": lon,
                "appid": self.api_key,
                "units": "metric"
            }
            if forecast_range.lower() == ForecastRange.CURRENT:
                try:
                    current_response = await client.get(ForecastType.CURRENT.value, params=current_params)
                    current_response.raise_for_status()
                    current_weather_api_model = WeatherData(**current_response.json())
                except httpx.RequestError as e:
                    logger.error(f"Error fetching current weather for {location_name}: {e}", exc_info=True)
                except Exception as e:
                    logger.error(f"Error parsing current weather data for {location_name}: {e}", exc_info=True)

            # 2. Fetch Hourly Forecast
            hourly_params = {
                "lat": lat,
                "lon": lon,
                "appid": self.api_key,
                "units": "metric"
            }
            if forecast_range.lower() == ForecastRange.HOURLY:
                try:
                    hourly_response = await client.get(ForecastType.HOURLY.value, params=hourly_params)
                    hourly_response.raise_for_status()
                    hourly_forecast_api_model = HourlyForecastData(**hourly_response.json())
                except httpx.RequestError as e:
                    logger.error(f"Error fetching hourly forecast for {location_name}: {e}", exc_info=True)
                except Exception as e:
                    logger.error(f"Error parsing hourly forecast data for {location_name}: {e}", exc_info=True)

            # 3. Fetch Daily Forecast
            daily_params = {
                "lat": lat,
                "lon": lon,
                "appid": self.api_key,
                "units": "metric",
                "cnt": 16
            }
            if forecast_range.lower() == ForecastRange.DAILY or forecast_range == ForecastRange.TOMORROW:
                try:
                    daily_response = await client.get(ForecastType.DAILY.value, params=daily_params)
                    daily_response.raise_for_status()
                    daily_forecast_api_model = DailyForecastData(**daily_response.json())
                except httpx.RequestError as e:
                    logger.error(f"Error fetching daily forecast for {location_name}: {e}", exc_info=True)
                except Exception as e:
                    logger.error(f"Error parsing daily forecast data for {location_name}: {e}", exc_info=True)

        # Transform the API data
        return self._transform_api_data_to_weather_forecast(
            location_name=location_name,
            current_weather_api_model=current_weather_api_model,
            hourly_forecast_api_model=hourly_forecast_api_model,
            daily_forecast_api_model=daily_forecast_api_model
        )