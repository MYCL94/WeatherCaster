from typing import List, Optional
from pydantic import BaseModel, Field, AliasChoices, computed_field
from datetime import datetime, timezone

class Coordinates(BaseModel):
    """Represents the latitude and longitude of a location."""
    lon: float = Field(..., description="Latitude of the location")
    lat: float = Field(..., description="Longitude of the location")
    
class GeocodingResult(BaseModel):
    """Contains coordinates and location name with according country."""
    coordinates: Optional[Coordinates] = Field(None, description="Latitude and longitude of the location")
    name: Optional[str] = Field(None, description="Name of the location")
    country: Optional[str] = Field(None, description="Country of the location")

class WeatherItem(BaseModel):
    """Represents a weather condition."""
    id: int = Field(..., description="Weather condition id")
    main: str = Field(..., description="Group of weather parameters (Rain, Snow, Extreme etc.)")
    description: str = Field(..., description="Weather condition within the group")
    icon: str = Field(..., description="Weather icon id")

class Main(BaseModel):
    """Represents main weather parameters."""
    temp: float = Field(..., description="Temperature. Unit Default: Kelvin, Metric: Celsius, Imperial: Fahrenheit.")
    feels_like: float = Field(..., description="Temperature. This temperature parameter accounts for the human perception of weather.")
    temp_min: float = Field(..., description="Minimum temperature at the moment. This is minimal currently observed temperature (within large megalopolises and urban areas).")
    temp_max: float = Field(..., description="Maximum temperature at the moment. This is maximal currently observed temperature (within large megalopolises and urban areas).")
    pressure: int = Field(..., description="Atmospheric pressure on the sea level, hPa")
    humidity: int = Field(..., description="Humidity, %")
    sea_level: Optional[int] = Field(None, description="Atmospheric pressure on the sea level, hPa")
    grnd_level: Optional[int] = Field(None, description="Atmospheric pressure on the ground level, hPa")

class Wind(BaseModel):
    """Represents wind conditions."""
    speed: float = Field(..., description="Wind speed. Unit Default: meter/sec, Metric: meter/sec, Imperial: miles/hour.")
    deg: int = Field(..., description="Wind direction, degrees (meteorological)")
    gust: Optional[float] = Field(None, description="Wind gust. Unit Default: meter/sec, Metric: meter/sec, Imperial: miles/hour.")

class Rain(BaseModel):
    """Represents rain volume data."""
    h1: Optional[float] = Field(None, validation_alias=AliasChoices('1h', 'rain.1h'), description="Rain volume for the last 1 hour, mm")
    h3: Optional[float] = Field(None, validation_alias=AliasChoices('3h', 'rain.3h'), description="Rain volume for the last 3 hours, mm")
    # AliasChoice is necessary because starting the variable with numbers such as '1h' and '3h' are not allowed

class Clouds(BaseModel):
    """Represents cloudiness information."""
    all: int = Field(..., description="Cloudiness, %")

class Sys(BaseModel):
    """Contains country with sunrise and sunset times."""
    country: Optional[str] = Field(None, description="Country code (GB, JP etc.)")
    sunrise: int = Field(..., description="Sunrise time, unix, UTC")
    sunset: int = Field(..., description="Sunset time, unix, UTC")

# The structure is taken from https://openweathermap.org/current
class WeatherData(BaseModel):
    """Represents detailed weather data."""
    coord: Coordinates = Field(..., description="Latitude and longitude of the location")
    weather: List[WeatherItem] = Field(..., description="List of weather conditions")
    base: str = Field(..., description="Internal parameter from the data source")
    main: Main = Field(..., description="Main weather parameters")
    visibility: int = Field(..., description="Visibility, meter. The maximum value of the visibility is 10km")
    wind: Wind = Field(..., description="Wind information")
    rain: Optional[Rain] = Field(None, description="Rain volume data")
    clouds: Clouds = Field(..., description="Cloudiness information")
    dt: int = Field(..., description="Time of data calculation, unix, UTC")
    sys: Sys = Field(..., description="System parameters")
    timezone: int = Field(..., description="Shift in seconds from UTC")
    id: int = Field(..., description="City ID")
    name: str = Field(..., description="City name")
    cod: int = Field(..., description="Internal parameter (e.g., HTTP status code)")

    @computed_field
    @property
    def dt_human_readable(self) -> str:
        """Human-readable date and time (UTC) of data calculation, derived from 'dt'."""
        return datetime.fromtimestamp(self.dt, tz=timezone.utc).strftime('%Y-%m-%d %H:%M:%S %Z')

# --- Models for Hourly Forecast ---

class PartOfDay(BaseModel):
    """Represents the part of the day."""
    pod : str = Field(..., description="Part of the day (pod: d for day or n for night)")

# The structure is taken from https://openweathermap.org/api/hourly-forecast
class HourlyForecastItem(BaseModel):
    """Represents an hourly forecast item."""
    dt: int = Field(..., description="Time of data forecasted, unix, UTC")
    main: Main = Field(..., description="Main weather parameters for this hourly forecast point")
    weather: List[WeatherItem] = Field(..., description="List of weather conditions for this hourly forecast point")
    clouds: Clouds = Field(..., description="Cloudiness information for this hourly forecast point")
    wind: Wind = Field(..., description="Wind information for this hourly forecast point")
    visibility: Optional[int] = Field(None, description="Average visibility, metres")
    pop: Optional[float] = Field(None, description="Probability of precipitation")
    rain: Optional[Rain] = Field(None, description="Rain volume for last 3 hours, mm")
    snow: Optional[float] = Field(None, description="Snow volume for last 3 hours, mm")
    sys: Optional[PartOfDay] = Field(None, description="Part of the day (pod: d for day or n for night)")
    dt_txt: str = Field(..., description="Data/time of calculation, UTC")

    @computed_field
    @property
    def dt_human_readable(self) -> str:
        """Human-readable date and time (UTC) of the forecast, derived from 'dt'."""
        return datetime.fromtimestamp(self.dt, tz=timezone.utc).strftime('%Y-%m-%d %H:%M:%S %Z')

# --- Models for City Information ---


class CityInfo(BaseModel):
    """Represents information about a city."""
    id: int = Field(..., description="City ID")
    name: str = Field(..., description="City name")
    coord: Coordinates = Field(..., description="Geographical coordinates of the city")
    country: str = Field(..., description="Country code (e.g., US, GB)")
    population: Optional[int] = Field(None, description="City population")
    timezone: Optional[int] = Field(None, description="Shift in seconds from UTC")
    sunrise: Optional[int] = Field(None, description="Sunrise time, unix, UTC")
    sunset: Optional[int] = Field(None, description="Sunset time, unix, UTC")

class HourlyForecastData(BaseModel):
    cod: str = Field(..., description="API response code")
    message: Optional[int | float] = Field(None, description="Internal message parameter, can be int or float")
    cnt: Optional[int] = Field(None, description="Number of hourly forecast items returned")
    list: List[HourlyForecastItem] = Field(..., description="List of hourly forecast items")
    city: CityInfo = Field(..., description="Information about the city for the forecast")

# --- Models for Daily Forecast ---
class DailyTemp(BaseModel):
    """Represents daily temperature."""
    day: float = Field(..., description="Daytime temperature")
    min: Optional[float] = Field(None, description="Minimum daily temperature")
    max: Optional[float] = Field(None, description="Maximum daily temperature")
    night: float = Field(..., description="Nighttime temperature")
    eve: float = Field(..., description="Evening temperature")
    morn: float = Field(..., description="Morning temperature")

class DailyFeelsLike(BaseModel):
    """Represents daily feels like temperature."""
    day: float = Field(..., description="Daytime feels like temperature")
    night: float = Field(..., description="Nighttime feels like temperature")
    eve: float = Field(..., description="Evening feels like temperature")
    morn: float = Field(..., description="Morning feels like temperature")

#The structure is taken from https://openweathermap.org/forecast16
class DailyForecastItem(BaseModel):
    """Represents a daily forecast item."""
    dt: int = Field(..., description="Time of data forecasted, unix, UTC")
    sunrise: Optional[int] = Field(None, description="Sunrise time, unix, UTC")
    sunset: Optional[int] = Field(None, description="Sunset time, unix, UTC")
    temp: DailyTemp = Field(..., description="Temperature details for the day")
    feels_like: DailyFeelsLike = Field(..., description="Feels like temperature details for the day")
    pressure: int = Field(..., description="Atmospheric pressure on the sea level, hPa")
    humidity: int = Field(..., description="Humidity, %")
    weather: List[WeatherItem] = Field(..., description="List of weather conditions for the day")
    speed: Optional[float] = Field(None, description="Wind speed. Unit Default: meter/sec")
    deg: Optional[int] = Field(None, description="Wind direction, degrees (meteorological)")
    gust: Optional[float] = Field(None, description="Wind gust. Unit Default: meter/sec")
    clouds: Optional[int] = Field(None, description="Cloudiness, %")
    pop: Optional[float] = Field(None, description="Probability of precipitation")
    rain: Optional[float] = Field(None, description="Rain volume, mm") 
    snow: Optional[float] = Field(None, description="Snow volume, mm")

    @computed_field
    @property
    def dt_human_readable(self) -> str:
        """Human-readable date (UTC) of the forecast, derived from 'dt'."""
        return datetime.fromtimestamp(self.dt, tz=timezone.utc).strftime('%Y-%m-%d %Z')

class DailyForecastData(BaseModel):
    """Represents daily forecast data."""
    city: CityInfo = Field(..., description="Information about the city for the forecast")
    cod: str = Field(..., description="API response code")
    message: Optional[float | int] = Field(None, description="Internal message parameter, can be float or int")
    cnt: Optional[int] = Field(None, description="Number of daily forecast items returned")
    list: List[DailyForecastItem] = Field(..., description="List of daily forecast items")