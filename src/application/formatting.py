"""Formatting Functions for Weather Forecast"""

from model_definition.final_response import WeatherForecast

def format_weather_summary(forecast: WeatherForecast) -> str:
    """Formats the WeatherForecast object into a summary string.

    Args:
        forecast (WeatherForecast): The WeatherForecast object to format.
         
    Returns:
        str: The formatted summary string.
    """
    summary_parts = []
    current = forecast.current
    summary_parts.append(f"Currently in {current.location} ({current.date_time.strftime('%b %d, %H:%M')}):")
    summary_parts.append(f"  Condition: {current.condition} {current.emoji}")
    summary_parts.append(f"  Temperature: {current.temperature:.2f}°C (Feels like: {current.feels_like_temperature:.2f}°C)")
    summary_parts.append(f"  Wind: {current.wind.speed:.2f} m/s @ {current.wind.direction}°")
    summary_parts.append(f"  Humidity: {current.humidity}%")
    summary_parts.append(f"  Pressure: {current.pressure} hPa")
    summary_parts.append(f"  Sunrise: {current.daylight.sunrise.strftime('%b %d, %H:%M')} | Sunset: {current.daylight.sunset.strftime('%b %d, %H:%M')}")

    if forecast.hourly:
        summary_parts.append("\nHourly Forecast (next 24 hours):")
        # Display up to 8 hourly entries
        for hourly in forecast.hourly[:8]:
            summary_parts.append(f"  {hourly.time.strftime('%H:%M')}: {hourly.condition} {hourly.emoji}, {hourly.temperature:.1f}°C, Wind: {hourly.wind.speed:.1f} m/s @ {hourly.wind.direction}°")

    if forecast.daily:
        summary_parts.append("\nDaily Forecast (next 5 days):")
        # Display up to 5 daily entries
        for daily in forecast.daily[:5]:
            summary_parts.append(f"  {daily.forecast_date.strftime('%b %d')}: {daily.condition} {daily.emoji}, High: {daily.max_temperature:.1f}°C, Low: {daily.min_temperature:.1f}°C, Wind: {daily.wind.speed:.1f} m/s @ {daily.wind.direction}°")

    return "\n".join(summary_parts)