from pathlib import Path

import pandas as pd
import requests
from geopy.geocoders import Nominatim


class CityNotFoundError(Exception):
    pass


class ForecastUnavailable(Exception):
    pass


def get_forecast(city='Pittsburgh'):
    '''
    Returns the nightly's forecast for a given city.

    Inputs:
    city (string): A valid string

    Output:
    period (dictionary/JSON): a dictionary containing at least,
    the forecast keys startTime, endTime and detailedForecast.

    Throws:
    CityNotFoundError if geopy returns empty list or if
    the latitude longitude fields are empty.

    ForecastUnavailable if the period is empty or the
    API throws any status code that is not 200

    Hint:
    * Return the period that is labeled as "Tonight"
    '''

    # Create geocoder
    geo_coder = Nominatim(user_agent="get-forecast")

    # Check if city exists and got longitude/latitude
    location = geo_coder.geocode(city)
    if not location or not location.latitude or not location.longitude:
        raise CityNotFoundError(f"{city} is not found!")

    latitude, longitude = location.latitude, location.longitude
    # Use api.weather.gov for weather forecasting
    # https://www.weather.gov/documentation/services-web-api
    url = f"https://api.weather.gov/points/{latitude},{longitude}"
    response_json = requests.get(url).json()
    url = response_json["properties"]["forecast"]
    response_json = requests.get(url).json()

    periods = response_json["properties"]["periods"]

    # Get weather forecast for tonight
    tonight = None
    for period in periods:
        if period["name"] == "Tonight":
            tonight = period
            break

    if not tonight:
        raise ForecastUnavailable(f"Tonight's forecast is not available!")

    return tonight


def main():
    period = get_forecast()

    file = 'weather.pkl'

    if Path(file).exists():
        df = pd.read_pickle(file)
    else:
        df = pd.DataFrame(columns=['Start Date', 'End Date', 'Forecast'])

    df = df.append(
        {
            'Start Date': period['startTime'],
            'End Date': period['endTime'],
            'Forecast': period['detailedForecast']
        }, ignore_index=True
    )
    df = df.drop_duplicates()
    df.to_pickle(file)

    # sort repositories
    file = open("README.md", "w")
    file.write('![Status](https://github.com/khionech/python-get-forecast'
               '/actions/workflows/build.yml/badge.svg)\n')
    file.write('![Status](https://github.com/khionech/python-get-forecast'
               '/actions/workflows/pretty.yml/badge.svg)\n')
    file.write('# Pittsburgh Nightly Forecast\n\n')

    file.write(df.to_markdown(tablefmt='github'))
    file.write('\n\n---\nCopyright © 2022 Pittsburgh'
               'Supercomputing Center. All Rights Reserved.')
    file.close()


if __name__ == "__main__":
    main()
