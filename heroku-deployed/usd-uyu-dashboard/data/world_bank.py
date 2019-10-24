""" Functions to access the World Bank Data API. """
import requests
from collections import defaultdict
import pandas as pd


def download_index(country_code,
                   index_code,
                   start_date=1960,
                   end_date=2018):
    """
    Get a JSON response for the index data of one country.

    Args:
        country_code(str): The two letter code for the World Bank webpage
        index_code(str): The code for the index to retreive
        start_date(int): The initial year to retreive
        end_date(int): The final year to retreive

    Returns:
        str: a JSON string with the raw data
    """
    payload = {'format': 'json',
               'per_page': '500',
               'date': '{}:{}'.format(str(start_date), str(end_date))
               }
    r = requests.get(
        'http://api.worldbank.org/v2/countries/{}/indicators/{}'.format(
            country_code, index_code), params=payload)
    return r.json()


def format_response(raw_res):
    """
    Formats a raw JSON string, returned from the World Bank API into a
    pandas DataFrame.
    """
    result = defaultdict(dict)
    for record in raw_res[1]:
        result[record['country']['value']].update(
            {int(record['date']): record['value']})

    return pd.DataFrame(result)


def download_cpi(country_code, **kwargs):
    """
    Downloads the Consumer Price Index for one country, and returns the data
    as a pandas DataFrame.

    Args:
        country_code(str): The two letter code for the World Bank webpage
        **kwargs: Arguments for 'download_index', for example:
            start_date(int): The initial year to retreive
            end_date(int): The final year to retreive
    """
    cpi_code = 'FP.CPI.TOTL'
    raw_res = download_index(country_code, cpi_code, **kwargs)
    return format_response(raw_res)


def download_cpis(country_codes, **kwargs):
    """
    Download many countries CPIs and store them in a pandas DataFrame.

    Args:
        country_codes(list(str)): A list with the two letter country codes
        **kwargs: Other keyword arguments, such as:
            start_date(int): The initial year to retreive
            end_date(int): The final year to retreive

    Returns:
        pd.DataFrame: A dataframe with the CPIs for all the countries in the
            input list.
    """
    cpi_list = [download_cpi(code, **kwargs) for code in country_codes]
    return pd.concat(cpi_list, axis=1)


def download_exchange_rate(country_code, **kwargs):
    """
    Downloads the Exchange for one country, with respect to USD,
    and returns the data as a pandas DataFrame.

    Args:
        country_code(str): The two letter code for the World Bank webpage
        **kwargs: Arguments for 'download_index', for example:
            start_date(int): The initial year to retreive
            end_date(int): The final year to retreive

    Returns:
        pd.DataFrame: The values for the exchange rates in a dataframe.
    """
    cpi_code = 'PA.NUS.FCRF'
    raw_res = download_index(country_code, cpi_code, **kwargs)
    return format_response(raw_res)
