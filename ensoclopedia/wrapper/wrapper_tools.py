# -*- coding:UTF-8 -*-
# ---------------------------------------------------------------------------------------------------------------------#
# Functions built over dataarray_tools and xarray_tools
# ---------------------------------------------------------------------------------------------------------------------#


# ---------------------------------------------------#
# Import packages
# ---------------------------------------------------#
# basic python package
from inspect import stack as inspect__stack
from typing import Union

# local functions
from ensoclopedia.wrapper import dataarray_tools as dt
from ensoclopedia.wrapper import xarray_tools as xt
from ensoclopedia.wrapper.tools import print_fail, unknown_formater
from ensoclopedia.wrapper.xarray_tools import array_wrapper, dataset_wrapper
# ---------------------------------------------------#


# ---------------------------------------------------------------------------------------------------------------------#
# Functions
# ---------------------------------------------------------------------------------------------------------------------#
def da_ds_execute(
        ds: Union[array_wrapper, dataset_wrapper],
        function: str,
        variable: list[str] = None,
        **kwargs) -> Union[array_wrapper, dataset_wrapper, None]:
    """
    Loop on variables (data_vars) if input is instance of Dataset and execute function on DataArray or directly execute
    function.

    Input:
    ------
    :param ds: xarray.DataArray or xarray.Dataset
    :param function: str
        Function to call like getattr(foo, function)
    :param variable: variable: list[str], optional
        List of variables (data_vars) in ds if it is xarray.Dataset; e.g., variable = ["ts"]
        If ds is xarray.Dataset, variable should be provided
        Default is None
    **kwargs - Optional keyword arguments passed directly on to getattr(foo, function)

    Output:
    -------
    :return: xarray.DataArray or xarray.Dataset
        Object (as input) with given function applied.
    """
    if isinstance(ds, dataset_wrapper) is True:
        # compute on all variables
        ds_o = {}
        for k in xt.get_variables(ds, variable=variable):
            ds_o[k] = da_execute(ds[k], function, **kwargs)
        # reconstruct dataset
        ds_o = dataset_wrapper(data_vars=ds_o, attrs=ds.attrs)
    else:
        # compute on single variable
        ds_o = da_execute(ds, function, **kwargs)
    return ds_o


def da_execute(
        da: array_wrapper,
        function: str,
        **kwargs) -> Union[array_wrapper, None]:
    """
    Apply given function on given DataArray.

    Input:
    ------
    :param da: xarray.DataArray
    :param function: str
        Function to call like getattr(foo, function)
    **kwargs - Optional keyword arguments passed directly on to getattr(foo, function)

    Output:
    -------
    :return: xarray.DataArray
        Object (as input) with function applied to its data.
    """
    # function in xarray_tools
    known_dt = [k for k in dir(dt) if "__" not in k]
    known_xt = [k for k in dir(xt) if "__" not in k]
    known_all = sorted(list(set(known_dt + known_xt)), key=lambda v: v.lower())
    da_o = None
    # fake loop to be able to break out when an error occurs
    for _ in [0]:
        # check if given function is known
        if function not in list(set(known_dt + known_xt)):
            print_fail(inspect__stack(), unknown_formater("function", function, known_all), fail_i=False)
            break
        # call function
        if function in known_dt:
            da_o = getattr(dt, function)(da, **kwargs)
        else:
            da_o = getattr(xt, function)(da, **kwargs)
    return da_o
# ---------------------------------------------------------------------------------------------------------------------#
