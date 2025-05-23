"""Simplified Pydantic Models (Target Output for Agent)"""
from datetime import datetime, date
from typing import List
from pydantic import BaseModel, Field

class WindInfo(BaseModel):
    speed: float = Field(..., description="The wind speed in meters per second (m/s).")
    direction: int = Field(..., description="The direction from which the wind is blowing in degrees (0-360, where 0 is North).")

class DaylightInfo(BaseModel):
    sunrise: datetime = Field(..., description="The specific date and time of sunrise (UTC).")
    sunset: datetime = Field(..., description="The specific date and time of sunset (UTC).")

class CurrentWeather(BaseModel):
    location: str = Field(..., description="The geographical location for the weather data (e.g., 'Konya').")
    date_time: datetime = Field(..., description="The exact date and time of the current weather observation.")
    condition: str = Field(..., description="A brief description of the current weather condition (e.g., 'Clouds', 'Clear Sky').")
    emoji: str = Field(..., description="An emoji representing the weather condition.")
    temperature: float = Field(..., description="The current temperature in Celsius.")
    feels_like_temperature: float = Field(..., description="The 'feels like' temperature in Celsius, accounting for wind chill and humidity.")
    high_temperature: float = Field(..., description="The highest temperature recorded for the current day in Celsius.")
    low_temperature: float = Field(..., description="The lowest temperature recorded for the current day in Celsius.")
    wind: WindInfo = Field(..., description="Wind conditions.")
    humidity: int = Field(..., description="The relative humidity as a percentage (0-100%).")
    pressure: int = Field(..., description="The atmospheric pressure in hectopascals (hPa).")
    daylight: DaylightInfo = Field(..., description="Sunrise and sunset times for the current day.")

class HourlyWeather(BaseModel):
    time: datetime = Field(..., description="The specific hour for which the forecast is provided.")
    temperature: float = Field(..., description="The forecasted temperature in Celsius for this hour.")
    condition: str = Field(..., description="A brief description of the forecasted weather condition for this hour.")
    emoji: str = Field(..., description="An emoji representing the weather condition.")
    wind: WindInfo = Field(..., description="Forecasted wind conditions for this hour.")
    humidity: int = Field(..., description="The forecasted relative humidity as a percentage for this hour.")
    pressure: int = Field(..., description="The forecasted atmospheric pressure in hectopascals (hPa) for this hour.")

class DailyWeather(BaseModel):
    forecast_date: date = Field(..., description="The specific date for which the forecast is provided.")
    max_temperature: float = Field(..., description="The maximum forecasted temperature in Celsius for this day.")
    min_temperature: float = Field(..., description="The minimum forecasted temperature in Celsius for this day.")
    condition: str = Field(..., description="A brief description of the overall forecasted weather condition for this day.")
    emoji: str = Field(..., description="An emoji representing the weather condition.")
    wind: WindInfo = Field(..., description="Average or maximum forecasted wind conditions for this day.")
    humidity: int = Field(..., description="The average forecasted relative humidity as a percentage for this day.")
    daylight: DaylightInfo = Field(..., description="Sunrise and sunset times for this forecasted day.")

class WeatherForecast(BaseModel):
    current: CurrentWeather = Field(..., description="The current weather conditions.")
    hourly: List[HourlyWeather] = Field(..., description="A list of hourly weather forecasts.")
    daily: List[DailyWeather] = Field(..., description="A list of daily weather forecasts.")