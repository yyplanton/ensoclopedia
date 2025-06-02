# -*- coding:UTF-8 -*-
# ---------------------------------------------------------------------------------------------------------------------#
# xarray functions
# ---------------------------------------------------------------------------------------------------------------------#


# ---------------------------------------------------#
# Import packages
# ---------------------------------------------------#
# basic python package
from typing import Union

# xarray
import xarray

# local functions
from ensoclopedia.wrapper import tools
# ---------------------------------------------------#


# ---------------------------------------------------------------------------------------------------------------------#
# Functions
# ---------------------------------------------------------------------------------------------------------------------#
array_wrapper = xarray.DataArray
dataset_wrapper = xarray.Dataset


def array_align(
        *objects: tuple[Union[array_wrapper, dataset_wrapper]],
        **kwargs) -> tuple:
    """
    Given any number of Dataset and/or DataArray objects, returns new objects with aligned indexes and dimension sizes.
    Array from the aligned objects are suitable as input to mathematical operators, because along each dimension they
    have the same index and size.
    https://docs.xarray.dev/en/stable/generated/xarray.align.html

    Input:
    ------
    :param objects: tuple[xarray.DataArray or xarray.Dataset]
        Objects to align
    :param kwargs: dict
        Key arguments passed to xarray alin (see url above)

    Output:
    -------
    :return: tuple[xarray.DataArray or xarray.Dataset]
        Tuple of objects with the same type as *objects with aligned coordinates.
    """
    tools.remove_keys(kwargs, desired_keys=["copy", "exclude", "fill_value", "indexes", "join"])
    return xarray.align(*objects, **kwargs)


def array_ones(
        ds: Union[array_wrapper, dataset_wrapper],
        **kwargs) -> Union[array_wrapper, dataset_wrapper]:
    """
    Return a new object of ones with the same shape and type as a given DataArray or Dataset.
    https://docs.xarray.dev/en/stable/generated/xarray.ones_like.html

    Input:
    ------
    :param ds: xarray.DataArray or xarray.Dataset
        The reference object. The output will have the same dimensions and coordinates as this object.
    :param kwargs: dict
        Key arguments passed to xarray ones_like (see url above)

    Output:
    -------
    :return: xarray.DataArray or xarray.Dataset
        New object of ones with the same shape and type as ds.
    """
    tools.remove_keys(kwargs, desired_keys=["dtype", "chunks", "chunked_array_type", "from_array_kwargs"])
    return xarray.ones_like(ds, **kwargs)


def merge(objects, **kwargs) -> dataset_wrapper:
    """
    Merge any number of xarray objects into a single Dataset as variables.
    https://docs.xarray.dev/en/stable/generated/xarray.merge.html

    Input:
    ------
    :param objects: iterable of Dataset or iterable of DataArray or iterable of dict-like
        Merge together all variables from these objects. If any of them are DataArray objects, they must have a name.
    :param kwargs: dict
        Key arguments passed to xarray marge (see url above)

    Output:
    -------
    :return: xarray.Dataset
        New Dataset with combined variables from each object.
    """
    tools.remove_keys(kwargs, desired_keys=["combine_attrs", "compat", "fill_value", "join"])
    return xarray.merge(objects, **kwargs)


def polynomial_fit(
        coord: Union[array_wrapper, dataset_wrapper],
        coeffs: Union[array_wrapper, dataset_wrapper],
        **kwargs) -> Union[array_wrapper, dataset_wrapper]:
    """
    Evaluate a polynomial at specific values.
    https://docs.xarray.dev/en/stable/generated/xarray.polyval.html

    Input:
    ------
    :param coord: xarray.DataArray or xarray.Dataset
        Values at which to evaluate the polynomial
    :param coeffs: xarray.DataArray or xarray.Dataset
        Coefficients of the polynomial
    **kwargs - Discarded

    Output:
    -------
    :return: xarray.DataArray or xarray.Dataset
        Object (as input) with evaluated polynomial.
    :return:
    """
    return xarray.polyval(coord, coeffs)
# ---------------------------------------------------------------------------------------------------------------------#
