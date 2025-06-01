# -*- coding:UTF-8 -*-
# ---------------------------------------------------------------------------------------------------------------------#
# Functions built over numpy
# ---------------------------------------------------------------------------------------------------------------------#


# ---------------------------------------------------#
# Import packages
# ---------------------------------------------------#
# basic python package
from copy import deepcopy as copy__deepcopy

# numpy
from numpy import array as numpy__array
from numpy import nan as numpy__nan
from numpy import ndarray as numpy__ndarray
from numpy import ones as numpy__ones
# ---------------------------------------------------#


# ---------------------------------------------------------------------------------------------------------------------#
# Functions
# ---------------------------------------------------------------------------------------------------------------------#
def splice(
        arr: numpy__ndarray,
        delta: int,
        window: int,
        **kwargs) -> numpy__ndarray:
    """
    Duplicate and reorganize data according to a window and delta.
    E.g., multi-year evolution arr[time], window = 24 months, delta = 12 months
    arr_o[year-1, 24]
    arr_o[0] = month 0 to 23
    arr_o[1] = month 12 to 35
    ...
    arr_o[n] = month n*12 to n*12 + 24 - 1

    Input:
    ------
    :param arr: numpy.ndarray
    :param delta: int
        Number of steps to shift the data at each splice; e.g., delta = 12
    :param window: int
        Window length; e.g., window = 24
    **kwargs - Discarded

    Output:
    -------
    :return: numpy.ndarray
        New array with spliced data (duplicated and reorganized)
    """
    # reorganize data along the first dimension
    arr_o = []
    half = window // 2
    h1 = half - delta
    h2 = half + delta
    for k in range(-h1, len(arr) - h2 + 1, delta):
        # 'window' sized array
        arr_t = numpy__ones((window,) + arr.shape[1:], dtype=arr.dtype) * numpy__nan
        # indices taken from input array
        i1, i2 = max(0, k), min(k + window, len(arr))
        # indices where to place input slice in output array
        o1, o2 = 0, copy__deepcopy(window)
        if k < 0:
            # the first 'h1' indices are not centered, they need to be handled properly
            o1 = i1 - k
        elif k + window > len(arr):
            # the last 'window' indices are not centered, they need to be handled properly
            o2 = o1 + i2 - i1
        arr_t[o1: o2] = arr[i1: i2]
        arr_o.append(arr_t)
    return numpy__array(arr_o)
# ---------------------------------------------------------------------------------------------------------------------#
