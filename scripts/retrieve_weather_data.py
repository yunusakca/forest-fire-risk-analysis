import openmeteo_requests
import requests_cache
import pandas as pd
from retry_requests import retry
from scripts.calculate_coordinates import parse_dms_string
from datetime import datetime, timedelta

def download_and_process_weather_data(dms_string, csv_prefix="weather_data", daily_vars=None):
    today = datetime.today().date()
    end_date = today.isoformat()
    start_date = (today - timedelta(days=365 * 10)).isoformat()

    if daily_vars is None:
        daily_vars = ["precipitation_sum", "temperature_2m_mean", "wind_speed_10m_max"]

    coords = parse_dms_string(dms_string)
    latitude, longitude = coords[0], coords[1]

    cache_session = requests_cache.CachedSession('.cache', expire_after = -1)
    retry_session = retry(cache_session, retries = 5, backoff_factor = 0.2)
    openmeteo = openmeteo_requests.Client(session = retry_session)

    url = "https://archive-api.open-meteo.com/v1/archive"
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "start_date": start_date,
        "end_date": end_date,
        "daily": daily_vars
    }
    responses = openmeteo.weather_api(url, params=params)

    response = responses[0]

    # Process daily data
    daily = response.Daily()
    daily_values = [daily.Variables(i).ValuesAsNumpy() for i in range(len(daily_vars))]

    daily_data = {
        "date": pd.date_range(
            start=pd.to_datetime(daily.Time(), unit="s", utc=True),
            end=pd.to_datetime(daily.TimeEnd(), unit="s", utc=True),
            freq=pd.Timedelta(seconds=daily.Interval()),
            inclusive="left"
        )
    }

    for i, var in enumerate(daily_vars):
        daily_data[var] = daily_values[i]

    daily_dataframe = pd.DataFrame(data=daily_data)
    daily_csv = f"{csv_prefix}.csv"
    monthly_csv = f"{csv_prefix}_monthly_averages.csv"

    # daily_dataframe.to_csv(daily_csv, index=False)
    daily_dataframe["year_month"] = daily_dataframe["date"].dt.to_period("M")
    monthly_avg = daily_dataframe.groupby("year_month").mean(numeric_only=True).reset_index()
    # monthly_avg.to_csv(monthly_csv, index=False)

    return monthly_avg