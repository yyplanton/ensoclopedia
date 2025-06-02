# -*- coding:UTF-8 -*-
# ---------------------------------------------------------------------------------------------------------------------#
# Functions to handle time axis
# ---------------------------------------------------------------------------------------------------------------------#


# ---------------------------------------------------#
# Import packages
# ---------------------------------------------------#
# basic python package
from datetime import datetime as datetime__datetime
from typing import Literal

# numpy
from numpy import integer as numpy__integer
from numpy import ndarray as numpy__ndarray
from numpy import zeros as numpy__zeros

# pandas
from pandas import Index
# ---------------------------------------------------#


# ---------------------------------------------------------------------------------------------------------------------#
# Functions
# ---------------------------------------------------------------------------------------------------------------------#
def _leap_year(year: int, calendar: str = "standard") -> bool:
    """
    Determine if year is a leap year for 'gregorian', 'julian', 'proleptic_gregorian', 'standard' calendars.
    For other calendars False will be returned

    Input:
    ------
    :param year: int
        Year
    :param calendar: str
        Name of a calendar
    **kwargs - Discarded

    Output:
    -------
    :return: bool
        True if given year is a leap year
    """
    leap = False
    if calendar in ["gregorian", "julian", "proleptic_gregorian", "standard"] and year % 4 == 0:
        leap = True
        if calendar == "proleptic_gregorian" and year % 100 == 0 and year % 400 != 0:
            leap = False
        elif calendar in ["gregorian", "standard"] and year % 100 == 0 and year % 400 != 0 and year < 1583:
            leap = False
    return leap


def get_days_per_month(
        time: Index,
        calendar: Literal["noleap", "365_day", "standard", "gregorian",
                          "proleptic_gregorian", "all_leap", "366_day", "360_day"] = "standard",
        **kwargs) -> numpy__ndarray:
    """
    Create an array of days per month corresponding to the time axis provided (must be monthly means)

    Input:
    ------
    :param time: Index
        Time axis as index
    :param calendar: {"noleap", "365_day", "standard", "gregorian", "proleptic_gregorian", "all_leap", "366_day",
                      "360_day"}
        Name of a calendar:
            'noleap' or '365_day':     no leap days (365 days per year)
            'all_leap' or '366_day':   all years have a leap day (366 days per year)
            '360_day':                 all months are 30 days long (360 days per year)
            'gregorian' or 'standard': follows the Gregorian calendar, i.e., leap year every 4 year after 1583, except
                                       for years that are divisible by 100 but not by 400
            'julian':                  follows the Julian calendar, i.e., leap year every 4 year
            'proleptic_gregorian':     follows the proleptic Gregorian calendar, i.e., leap year every 4 year, except
                                       for years that are divisible by 100 but not by 400
    **kwargs - Discarded

    Output:
    -------
    :return: numpy__ndarray
        Array of days per month corresponding to the time axis provided
    """
    # create output array
    month_length = numpy__zeros(len(time), dtype=numpy__integer)
    # get the number of days for each month according to the calendar type
    days_per_month = {
        "noleap": [0, 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31],
        "365_day": [0, 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31],
        "standard": [0, 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31],
        "gregorian": [0, 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31],
        "proleptic_gregorian": [0, 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31],
        "all_leap": [0, 31, 29, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31],
        "366_day": [0, 31, 29, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31],
        "360_day": [0, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30],
    }
    nbr_of_days_for_each_month = days_per_month[calendar]
    # number of days for each month of the given time axis
    for k, (month, year) in enumerate(zip(time.month, time.year)):
        month_length[k] = nbr_of_days_for_each_month[month]
        if month == 2 and _leap_year(year, calendar=calendar):
            month_length[k] += 1
    return month_length


def get_time_plot(time: Index, **kwargs) -> numpy__ndarray:
    """
    Create a time axis based on 'year fraction', e.g., 2025-01-16 0:0:0 ~ 2025.0.04, 2025-02-14 0:0:0 ~ 2025.12
    Always uses proleptic Gregorian calendar

    Input:
    ------
    :param time: Index
        Time axis as index
    **kwargs - Discarded

    Output:
    -------
    :return: numpy__ndarray
        Time axis based on 'year fraction'
    """
    # create output array
    time_o = numpy__zeros(len(time))
    # time as year fraction
    for k, (y, m, d, h, mi, se) in enumerate(zip(time.year, time.month, time.day, time.hour, time.minute, time.second)):
        # create datetime for this year and the current time
        year_start = datetime__datetime(y, 1, 1, 0, 0, 0)
        year_end = datetime__datetime(y + 1, 1, 1, 0, 0, 0)
        year_now = datetime__datetime(y, m, d, h, mi, se)
        # number of seconds from the beginning of the year and total number of seconds during this year
        sec_now = (year_now - year_start).total_seconds()
        sec_tot = (year_end - year_start).total_seconds()
        # time is year + second fraction
        time_o[k] = y + sec_now / sec_tot
    return time_o
# ---------------------------------------------------------------------------------------------------------------------#
