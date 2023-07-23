from __future__ import annotations

import os

import numpy as np
import datetime
from dateutil.relativedelta import relativedelta
from typing import Literal
from dateutil import parser
from math import isclose
import math
from typing import List
import calendar


def datestring_to_datetime(datestring: str):
    return parser.parse(datestring, dayfirst=True).date()


def datetime_to_datestring(datetime_: datetime.date, format='%d/%m/%Y'):
    return datetime_.strftime(format)


def get_latest_available_date(dates: List[datetime.date], cutoff_date: datetime.date):
    '''
    assert all(isinstance(d, datetime.date) for d in dates)
    assert isinstance(cutoff_date, datetime.date)
    '''
    assert isinstance(dates, list)
    for i, d in enumerate(dates):
        if not isinstance(d, datetime.date):
            dates[i] = datestring_to_datetime(d)
    if not isinstance(cutoff_date, datetime.date):
        cutoff_date = datestring_to_datetime(cutoff_date)

    last_available_holdings_date = max([date for date in dates if date <= cutoff_date])

    return last_available_holdings_date


def increment_eop_date_by_t_periods(base_date: datetime.date, frequency: Literal['Y', 'Q', 'M', 'D'], t_periods: int):
    # assert base_date is in given frequency
    if base_date not in generate_list_of_supported_dates_in_year(base_date.year, frequency):
        raise ValueError("base_date is not at the end of the period in the expected frequency")

    # utility to get last day of month
    def get_last_date_of_month(date: datetime.date):
        y = date.year
        m = date.month
        d = calendar.monthrange(y, m)[1]
        date_ = datetime.date(y, m, d)
        return date_

    # calculate time increment
    if frequency == 'Y':
        time_delta = relativedelta(months=+12)
    elif frequency == 'Q':
        time_delta = relativedelta(months=+3)
    elif frequency == 'M':
        time_delta = relativedelta(months=+1)
    elif frequency == 'D':
        time_delta = relativedelta(days=+1)
    out_date = base_date + time_delta * t_periods

    # push out date to eom
    out_date = get_last_date_of_month(out_date)
    return out_date


def check_dictionary_values_add_to_one(d):
    return isclose(sum(d.values()), 1.0, rel_tol=0.01)


def convert_date_delta_into_frequency_units(t_1: datetime.date, t_0: datetime.date, frequency: Literal[
    'Y', 'Q', 'M']) -> int:  # todo: docstring? ok to round to floor?
    delta = relativedelta(t_1, t_0)
    if frequency == 'Y':
        out = delta.years
    elif frequency == 'M':
        out = delta.years * 12 + delta.months
    elif frequency == 'Q':
        out = (delta.years * 12 + delta.months) // 3
    return int(out)


def format_frequency(frequency: Literal['Y', 'Q', 'M']):
    formatter = {'Q': 'Quarter', 'Y': 'Year', 'M': 'Months'}
    return formatter[frequency]


def format_strats(elem, taxonomy):
    if type(elem) == tuple:
        elem = [x for x in elem if (type(x) == str) or not (math.isnan(x))]
        if set(elem) == set(taxonomy):
            elem = 'All strategies'
        else:
            elem = ', '.join(elem)
            elem = elem.replace("_", ' ')
    else:
        pass
    return elem


def convert_frequency(v: int, base_frequency: Literal['Y', 'Q', 'M'], target_frequency: Literal['Y', 'Q', 'M']) -> int:
    if target_frequency == 'Y':
        if base_frequency == 'Y':
            out = v
        elif base_frequency == 'Q':
            out = v // 4
        else:
            out = v // 12
    elif target_frequency == 'Q':
        if base_frequency == 'Y':
            out = v * 4
        elif base_frequency == 'Q':
            out = v
        else:
            out = v // 3
    else:
        if base_frequency == 'Y':
            out = v * 12
        elif base_frequency == 'Q':
            out = v * 3
        else:
            out = v
    return out


def generate_list_of_supported_dates_in_year(year: int, frequency: Literal['Y', 'Q', 'M']) -> list:
    # local constants
    MONTHS_BY_FREQUENCY = {
        'Y': [12],
        'Q': [3, 6, 9, 12],
        'M': list(range(1, 13))
    }

    # supported months
    months = MONTHS_BY_FREQUENCY[frequency]

    # return list of dates in year
    return [datetime.date(year, m, calendar.monthrange(year, m)[1]) for m in months]


def get_start_of_period(current_date: datetime.date, frequency: Literal['Y', 'Q', 'M', 'D']) -> datetime.date:
    if frequency == 'D':
        out = current_date
    elif frequency == 'M':
        out = datetime.date(year=current_date.year, month=current_date.month, day=1)
    elif frequency == 'Q':
        if 1 <= current_date.month <= 3:
            out = get_start_of_period(current_date=datetime.date(current_date.year, 1, 1), frequency='M')
        elif 4 <= current_date.month <= 6:
            out = get_start_of_period(current_date=datetime.date(current_date.year, 4, 1), frequency='M')
        elif 7 <= current_date.month <= 9:
            out = get_start_of_period(current_date=datetime.date(current_date.year, 7, 1), frequency='M')
        else:
            out = get_start_of_period(current_date=datetime.date(current_date.year, 10, 1),
                                      frequency='M')
    else:
        out = datetime.date(current_date.year, 1, 1)

    return out


def get_end_of_period(current_date: datetime.date, frequency: Literal['Y', 'Q', 'M', 'D']) -> datetime.date:
    if frequency == 'D':
        out = current_date
    elif frequency == 'M':
        _, day = calendar.monthrange(current_date.year, current_date.month)
        out = datetime.date(year=current_date.year, month=current_date.month, day=day)
    elif frequency == 'Q':
        if 1 <= current_date.month <= 3:
            out = get_end_of_period(current_date=datetime.date(current_date.year, 3, 1), frequency='M')
        elif 4 <= current_date.month <= 6:
            out = get_end_of_period(current_date=datetime.date(current_date.year, 6, 1), frequency='M')
        elif 7 <= current_date.month <= 9:
            out = get_end_of_period(current_date=datetime.date(current_date.year, 9, 1), frequency='M')
        else:
            out = get_end_of_period(current_date=datetime.date(current_date.year, 12, 1),
                                    frequency='M')
    else:
        out = datetime.date(current_date.year, 12, 31)

    return out


def map_dates_array(dates_to_map: np.ndarray[datetime.date], target_dates: np.ndarray[datetime.date]) -> np.ndarray:
    '''
    This function maps the dates in dates_to_map to the dates in target_dates by selecting the closest date in target_dates AFTER the date in dates_to_map
    '''

    assert isinstance(dates_to_map, np.ndarray)
    assert isinstance(target_dates, np.ndarray)

    # calculate days difference
    diff = target_dates.reshape(-1, 1) - dates_to_map.reshape(1, -1)

    # apply .days to each element in diff - NB the col represents the dates_to_map and the row represents the target_dates, and the numbers reflect time left from dates_to_map to target dates
    diff = np.vectorize(lambda x: float(x.days))(diff)

    # set negative values in diff to np.nan
    diff[diff < 0] = np.nan

    # if a column is full of nans, it means that the corresponding date in dates_to_map is AFTER any date in target_dates
    dates_to_map_beyond_max_target_date = np.all(np.isnan(diff), axis=0)

    # find the index of the minimum value in each row of diff ignoring the nan values
    if np.any(dates_to_map_beyond_max_target_date):
        '''
        # get the indices
        min_diff_idx = np.full(shape=dates_to_map.shape, fill_value=np.nan, dtype=np.float)
        min_diff_idx[~dates_to_map_beyond_max_target_date] = np.nanargmin(diff[:, ~dates_to_map_beyond_max_target_date], axis=0)
        # map the dates
        dates_maps = np.full(shape=dates_to_map.shape, fill_value=np.nan, dtype=np.float)
        dates_maps[~dates_to_map_beyond_max_target_date] = target_dates[min_diff_idx[~dates_to_map_beyond_max_target_date]]
        '''
        # remove the columns with nans
        diff = diff[:, ~dates_to_map_beyond_max_target_date]
        # get the indices
        min_diff_idx = np.nanargmin(diff, axis=0)
        # map the dates
        dates_maps = target_dates[min_diff_idx]
        # checks that the True values in array dates_to_map_beyond_max_target_date are at the end of the array, before concatenating the dates_maps array with the nans
        assert np.all(
            dates_to_map_beyond_max_target_date[np.where(dates_to_map_beyond_max_target_date)[0][-1]:] == True)
        # add back nans to the columns with nans
        dates_maps = np.concatenate(
            [dates_maps, np.full(shape=np.sum(dates_to_map_beyond_max_target_date), fill_value=np.nan, dtype=float)])
    else:
        # get the indices
        min_diff_idx = np.nanargmin(diff, axis=0)
        # map the dates
        dates_maps = target_dates[min_diff_idx]

    return dates_maps


def left_union_dictionaries(dict1, dict2):
    merged_dict = dict(dict1)  # Make a copy of the first dictionary

    for key, value in dict2.items():
        if key not in merged_dict:
            merged_dict[key] = value

    return merged_dict


def round_to_power_of_10(number: float):
    assert number > 0
    power = round(math.log10(number))
    rounded = 10 ** power
    return rounded


def get_file_extension(file_path) -> str:
    _, file_extension = os.path.splitext(file_path)
    return file_extension.lower()

def go_n_levels_up(path, levels_up):
    """
    Navigate n levels up in the folder hierarchy from a given path (please note that one level up means that you have the path of the directory where path is).

    :param path: The starting path.
    :param levels_up: The number of levels to go up.
    :return: The final path after going up n levels.
    """
    if levels_up < 0:
        raise ValueError("levels_up must be a non-negative integer.")

    current_path = os.path.abspath(path)

    for _ in range(levels_up):
        current_path = os.path.dirname(current_path)

    return current_path