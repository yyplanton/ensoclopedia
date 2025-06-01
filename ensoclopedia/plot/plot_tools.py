# -*- coding:UTF-8 -*-
# ---------------------------------------------------------------------------------------------------------------------#
# Functions to do basic processing for the figure templates
# ---------------------------------------------------------------------------------------------------------------------#


# ---------------------------------------------------#
# Import packages
# ---------------------------------------------------#
# basic python package
from copy import deepcopy as copy__deepcopy
from math import ceil as math__ceil
from math import floor as math__floor
from math import log as math__log
from string import ascii_lowercase as string__ascii_lowercase
# numpy
from numpy import ndarray as numpy__ndarray

# local package
from ensoclopedia.wrapper.tools import none_to_default
# ---------------------------------------------------#


# ---------------------------------------------------------------------------------------------------------------------#
# Functions
# ---------------------------------------------------------------------------------------------------------------------#
def _flatten_list(arr_i, list_values: list = None) -> list:
    """
    Flatten list of lists

    Inputs:
    -------
    :param arr_i: array_like
    :param list_values: list, optional

    Output:
    -------
    :return list_values: list
        Flatten list
    """
    # set default values if not given
    list_values = none_to_default(list_values, [])
    # if list contains list, flatten
    if isinstance(arr_i, (list, numpy__ndarray)) is True:
        for k in arr_i:
            _flatten_list(k, list_values=list_values)
    else:
        list_values.append(arr_i)
    return list_values


def _axis_auto_ticks(arr_i: list) -> list:
    """
    Create automatic optimized axis ticks

    Input:
    ------
    :param arr_i: list
        Values to plot

    Output:
    -------
    :return list_ticks: list
        Ticks for the plot axis
    """
    # if list contains lists, flatten lists
    list_values = _flatten_list(arr_i)
    # compute auto range
    if len(list_values) == 0:
        list_ticks = list(range(2))
    elif len(list_values) == 1:
        value = list_values[0]
        # order of magnitude of the value
        o_of_magnitude = math__floor(math__log(value, 10))
        # coefficient corresponding to the order of magnitude
        coefficient = 10 ** o_of_magnitude
        # one tick below value and one tick above value
        list_ticks = [math__floor(value / coefficient) * coefficient, math__ceil(value / coefficient) * coefficient]
    else:
        # range of input values
        range_values = max(list_values) - min(list_values)
        # order of magnitude of a 4th of the range (5 ticks between min and max)
        o_of_magnitude = math__floor(math__log(range_values / 4, 10))
        # coefficient corresponding to the order of magnitude - 1 (values in 10s)
        coefficient = 10 ** o_of_magnitude
        # difference between the floor and the maximum value
        delta = max(list_values) / coefficient - math__floor(min(list_values) / coefficient)
        # increment to have 5 ticks between floor and max(list_values)
        increment = math__ceil(delta / 4)
        # adapt coefficient
        while delta / increment <= 3:
            # due to the rounding up, the increment may be too big, if it is the case the coefficient is decreased
            coefficient /= 10
            # difference between the floor and the maximum value
            delta = max(list_values) / coefficient - math__floor(min(list_values) / coefficient)
            # increment to have 5 ticks between floor and max(list_values)
            increment = math__ceil(delta / 4)
        # lowest order of magnitude lower than the minimum value and higher than maximum value
        floor = math__floor(min(list_values) / coefficient)
        ceiling = math__ceil(max(list_values) / coefficient)
        # make sure that there is 4 increments in range
        if ceiling - floor <= 4 * increment:
            ceiling += increment
        # 5 ticks
        list_ticks = [k * coefficient for k in range(floor, ceiling, increment)]
    return list_ticks


def axis_ticklabel(arr_i: list, nam_i: str = "") -> list:
    """
    Format list of ints or floats into a list of str with the same number of decimals (up to 3 decimals)

    Inputs:
    -------
    :param arr_i: list
        Axis ticks; e.g., arr_i = [1, 2.5]
    :param nam_i: str, optional
        Name of the axis to do special labels (nam_i = 'latitude' or 'longitude')
        Default is '' (no special label)

    Output:
    -------
    :return labels: list
        Tick labels; e.g., labels = ['1.0', '2.5']
    """
    # keep a copy of the input array
    input_array = copy__deepcopy(arr_i)
    # create labels
    labels = copy__deepcopy(arr_i)
    if nam_i == "latitude":
        arr_i = [abs(k) if k < 0 else k for k in arr_i]
    elif nam_i == "longitude":
        arr_i = [360 - k if k > 180 else (abs(k) if k < 0 else k) for k in arr_i]
    if all([int(k) == k for k in arr_i]) is True:
        # int to str
        labels = [str(k) for k in arr_i]
    elif all([int(round(k * 10, 8)) == round(k * 10, 8) for k in arr_i]) is True:
        # format all values with 1 decimal
        labels = ["{0:.1f}".format(round(k, 1)) for k in arr_i]
    elif all([int(round(k * 100, 8)) == round(k * 100, 8) for k in arr_i]) is True:
        # format all values with 2 decimals
        labels = ["{0:.2f}".format(round(k, 2)) for k in arr_i]
    elif all([int(round(k * 1000, 8)) == round(k * 1000, 8) for k in arr_i]) is True:
        # format all values with 3 decimals
        labels = ["{0:.3f}".format(round(k, 3)) for k in arr_i]
    # latitude / longitude
    if nam_i == "latitude":
        labels = [str(k2) + "$^\circ$S" if k1 < 0 else (str(k2) + "$^\circ$N" if k1 > 0 else str(k2) + "$^\circ$")
                  for k1, k2 in zip(input_array, labels)]
    elif nam_i == "longitude":
        labels = [str(k2) + "$^\circ$E" if 0 < k1 < 180 or -360 < k1 < -180 else (
            str(k2) + "$^\circ$W" if 180 < k1 < 360 or -180 < k1 < 0 else str(k2) + "$^\circ$")
                  for k1, k2 in zip(input_array, labels)]
    return labels


def figure_axis(user_ticks, arr_i=None, axis_name: str = "") -> (list, list):
    """
    Create axis ticks, tick labels and limits

    Inputs:
    -------
    :param user_ticks: list
        User defined tics; e.g., user_ticks = [1, 2, 3, 4]
    :param arr_i: list, optional
        Values to plot; e.g., arr_i = [[1, 2], [3, 4], [[5, 6], [7, 8]]]
    :param axis_name: str, optional
        Name of the axis to do special labels; e.g., nam_i = 'latitude'
        Two names are recognized: 'latitude', 'longitude'
        Default is '' (no special label)

    Outputs:
    --------
    :return axis_tick_labels: list
        Axis tick labels
    :return axis_ticks: list
        Axis ticks
    """
    if user_ticks is None:
        axis_ticks = _axis_auto_ticks(arr_i)
    else:
        axis_ticks = copy__deepcopy(user_ticks)
    axis_tick_labels = axis_ticklabel(axis_ticks, nam_i=axis_name)
    return axis_tick_labels, axis_ticks


def panel_numbering(nbr_panels: int) -> list[str]:
    """
    Create a list of panel 'number' (i.e., 'a' -> 'z')

    Input:
    ------
    :param nbr_panels: int
        Number of panels in the figure; e.g., nbr_panels = 4

    Output:
    -------
    :return numbering: list[str]
        List of panel 'number'; e.g., numbering = ['a', 'b', 'c', 'd']
    """
    letters = string__ascii_lowercase
    if nbr_panels < len(letters):
        numbering = [k for k in letters[:nbr_panels]]
    else:
        # number of alphabet
        n_alpha = math__ceil(nbr_panels / len(letters))
        numbering = []
        for k1 in letters[:n_alpha]:
            for k2 in letters:
                numbering.append(str(k1) + str(k2))
    return numbering
# ---------------------------------------------------------------------------------------------------------------------#
