# -*- coding:UTF-8 -*-
# ---------------------------------------------------------------------------------------------------------------------#
# Functions built over xarray.DataArray
# ---------------------------------------------------------------------------------------------------------------------#


# ---------------------------------------------------#
# Import packages
# ---------------------------------------------------#
# basic python package
from copy import deepcopy as copy__deepcopy
from typing import Hashable, Literal, Union

# numpy
from numpy import absolute as numpy__absolute
from numpy import array as numpy__array
from numpy import cos as numpy__cos
from numpy import deg2rad as numpy__deg2rad
from numpy import float32 as numpy__float32
from numpy import ndarray as numpy__ndarray
from numpy import sqrt as numpy__sqrt

# scipy
from scipy.stats import t as scipy__stats__t

# local functions
from ensoclopedia.wrapper import numpy_tools
from ensoclopedia.wrapper import tools
from ensoclopedia.wrapper import xarray_base as xb
from ensoclopedia.wrapper import xarray_tools as xt
from ensoclopedia.wrapper.xarray_tools import array_wrapper, dataset_wrapper
# ---------------------------------------------------#


# ---------------------------------------------------------------------------------------------------------------------#
# Functions
# ---------------------------------------------------------------------------------------------------------------------#
def linear_regression(
        da_x: array_wrapper,
        da_y: array_wrapper,
        alternative: Literal["greater", "less", "two-sided"] = "two-sided",
        dim: Union[Hashable, str] = "T",
        lag_x: int = 0,
        lag_y: int = 0,
        **kwargs) -> dataset_wrapper:
    """
    Takes two xarray.DataArrays of any dimensions (input data could be a 1D time series, or for example, have three
    dimensions e.g. time, lat, lon), and returns regression slope, intercept, Pearson correlation coefficient, p-value
    for given null hypothesis and standard error between the two xarray.DataArrays along given dim.

    Inspired by:
    https://stackoverflow.com/questions/52108417/how-to-apply-linear-regression-to-every-pixel-in-a-large-multi-dimensional-array

    Input:
    ------
    :param da_x: xarray.DataArray
        Array with any number of dimensions, both da_x and da_y must share dim
    :param da_y: xarray.DataArray
        Same as da_x
    :param alternative : {"greater", "less", "two-sided"}, optional
        Defines the alternative hypothesis; e.g., alternative = "two-sided"
        The following options are available:
            'greater':   slope of the regression line is greater than zero
            'less':      slope of the regression line is less than zero
            'two-sided': slope of the regression line is nonzero
        Default is "two-sided"
    :param dim: Hashable or str, optional
        Dimension name along which the regression is computed; e.g., dim = "T"
        Default is "T"
    :param lag_x : int, optional
        Number of steps to shift da_x by; e.g., lag_x = 0
        Default is 0
    :param lag_y : int, optional
        Same as lag_x
    **kwargs - Discarded

    Output:
    -------
    :return: xarray.Dataset
        New dataset comparing the two input array.DataArray along given dim and the indicated dimension removed,
        containing variables including covariance, correlation, coefficient of determination, regression slope,
        intercept, p-value and standard error, and number of valid observations (n).
    """
    ds_o = None
    # fake loop to be able to break out when an error occurs
    for _ in [0]:
        # check alternative value
        if alternative not in ["greater", "less", "two-sided"]:
            break
        # get dimension name in both da
        dim_x = xt.check_dim(da_x, dim)
        dim_y = xt.check_dim(da_y, dim)
        if tools.is_dim(dim_x) is False or tools.is_dim(dim_y) is False:
            break
        # Shift x and y data if lags are specified
        if lag_x != 0:
            # If x lags y by 1, x must be shifted 1 step backwards. But as the 'zero-th' value is nonexistent, xarray
            # assigns it as invalid (nan). Hence, it needs to be dropped
            da_x = da_x.shift(**{dim_x: -lag_x}).dropna(dim=dim_x)
            # Next re-align the two datasets so that y adjusts to the changed coordinates of x
            da_x, da_y = xb.array_align(da_x, da_y)
        if lag_y != 0:
            da_y = da_y.shift(**{dim_y: -lag_y}).dropna(dim=dim_y)
        # Ensure that the data are properly aligned to each other.
        da_x, da_y = xb.array_align(da_x, da_y)
        # Compute data length, mean and standard deviation along dim
        n = da_y.notnull().sum(dim=dim)
        x_mean = da_x.mean(dim=dim)
        y_mean = da_y.mean(dim=dim)
        x_std = da_x.std(dim=dim)
        y_std = da_y.std(dim=dim)
        # Compute covariance, correlation and coefficient of determination
        cov = ((da_x - x_mean) * (da_y - y_mean)).sum(dim=dim) / n
        cor = cov / (x_std * y_std)
        # Compute regression slope and intercept
        slope = cov / (x_std ** 2)
        intercept = y_mean - x_mean * slope
        # Compute t-statistics and standard error
        t_stats = cor * numpy__sqrt(n - 2) / numpy__sqrt(1 - cor ** 2)
        stderr = slope / t_stats
        # Calculate p-values for different alternative hypotheses.
        if alternative == "greater":
            p_value = scipy__stats__t.sf(t_stats, n - 2)
        elif alternative == "less":
            p_value = scipy__stats__t.cdf(numpy__absolute(t_stats), n - 2)
        else:
            p_value = scipy__stats__t.sf(numpy__absolute(t_stats), n - 2) * 2
        # Wrap p-values into an xr.DataArray
        p_value = array_wrapper(coords=cor.coords, data=p_value, dims=cor.dims)
        # Combine into single dataset
        ds_o = {
            "slope": slope.rename("slope").astype(numpy__float32).drop_attrs(),
            "intercept": intercept.rename("intercept").astype(numpy__float32).drop_attrs(),
            "rvalue": cor.rename("rvalue").astype(numpy__float32).drop_attrs(),
            "pvalue": p_value.rename("pvalue").astype(numpy__float32).drop_attrs(),
            "stderr": stderr.rename("stderr").astype(numpy__float32).drop_attrs(),
        }
        ds_o = dataset_wrapper(data_vars=ds_o)
        # get attributes coordinates attributes from da_y
        for k in list(ds_o.coords):
            ds_o[k].attrs.update(da_y[k].attrs)
    return ds_o


def mean_weighted(
        da: array_wrapper,
        dim: Union[Hashable, str, list[Hashable], list[str], tuple[Hashable], tuple[str]] = "T",
        keep_attrs: bool = True,
        skipna: bool = False,
        weights: Union[array_wrapper, numpy__ndarray, None] = None,
        **kwargs):
    """
    Reduce this DataArray’s data by a weighted mean along given dimension(s).
    https://docs.xarray.dev/en/stable/generated/xarray.DataArray.weighted.html
    https://docs.xarray.dev/en/stable/generated/xarray.computation.weighted.DataArrayWeighted.mean.html
    https://docs.xarray.dev/en/stable/generated/xarray.DataArray.mean.html

    Input:
    ------
    :param da: xarray.DataArray
    :param dim: Hashable or Iterable of Hashable, optional
        Dimension(s) over which to apply the weighted mean; e.g., dim = "X" or dim = ("X", "Y")
        Default is "T"
    :param keep_attrs: bool or None, optional
        If True, attrs will be copied from the original object to the new one.
        If False, the new object will be returned without attributes.
        Default is True
    :param skipna: bool or None, optional
        If True, skip missing values (as marked by NaN).
        Default is None (i.e., only skips missing values for float dtypes)
    :param weights: xarray.DataArray or numpy.ndarray or None, optional
        An array of weights associated with the values in this Dataset. Each value in the data contributes to the
        reduction operation according to its associated weight.
        If not given and latitude in dim, weights are computed using cos(latitude).
        If not given and time in dim, weights are computed using time_weights.
        Then da.weighted(weights).mean() is computed if weights are instance of xarray.DataArray or numpy.ndarray
        Else, ds.mean() is computed.
        Default is None
    **kwargs – Additional keyword arguments passed on to the appropriate array function for calculating mean on this
               object's data. These could include dask-specific kwargs like split_every.

    Output:
    -------
    :return: xarray.DataArray
         New DataArray object with mean or weighted mean applied to its data and the indicated dimension(s) removed.
    """
    da_o = None
    # fake loop to be able to break out when an error occurs
    for _ in [0]:
        # get dimension name in da
        if dim is not None and isinstance(dim, (list, tuple)) is True:
            dim = [xt.check_dim(da, k) for k in dim]
        else:
            dim = xt.check_dim(da, dim)
        # create an iterable of dimensions to facilitate tests
        dim_list = copy__deepcopy(dim) if isinstance(dim, (list, tuple)) is True else [dim]
        if all([tools.is_dim(k) is True for k in dim_list]) is False:
            break
        # get 'theoretical' dimension names of time, longitude and latitude (None is returned if they don't exist)
        time_dim = xt.cf_dim_to_dim(da, "T")
        lon_dim = xt.cf_dim_to_dim(da, "X")
        lat_dim = xt.cf_dim_to_dim(da, "Y")
        # compute weights if not provided and if possible
        if isinstance(weights, bool) is True and weights is True:
            # list longitude and latitude 'theoretical' dimension names if they exist
            hor_dim = [k for k in [lon_dim, lat_dim] if tools.is_dim(k)]
            # check if weights should be computed
            if tools.is_dim(lat_dim) is True and lat_dim in dim_list and len(list(set(dim_list) - set(hor_dim))) == 0:
                # compute weights using cos(latitude) only if dim_list = ['Y'] or ['X', 'Y']
                weights = numpy__cos(numpy__deg2rad(da[lat_dim]))
            elif tools.is_dim(time_dim) is True and time_dim in dim_list and len(dim_list) == 1:
                # compute time weights using days per month only if dim_list = ['T']
                weights = xt.weights_time(da)
        # test if multidimensional coordinates
        if (tools.is_dim(lat_dim) is True and lat_dim in dim_list and len(da[lat_dim].shape) > 1) or (
                tools.is_dim(lon_dim) is True and lon_dim in dim_list and len(da[lon_dim].shape) > 1):
            # is multidimensional
            dim_old = copy__deepcopy(dim) if isinstance(dim, (list, tuple)) is True else [dim]
            # convert lat/lon to y/x
            dim_new = []
            for k in dim_old:
                if tools.is_dim(lat_dim) is True and k == lat_dim and len(da[lat_dim].shape) > 1:
                    dim_new.append(list(da[lat_dim].dims)[0])
                elif tools.is_dim(lon_dim) is True and k == lon_dim and len(da[lon_dim].shape) > 1:
                    dim_new.append(list(da[lat_dim].dims)[1])
                else:
                    dim_new.append(k)
            dim = copy__deepcopy(dim_new) if isinstance(dim, (list, tuple)) is True else dim_new[0]
        # compute mean
        if isinstance(da, array_wrapper) is True and isinstance(weights, (array_wrapper, numpy__ndarray)) is True:
            da_o = da.weighted(weights).mean(dim=dim, keep_attrs=keep_attrs, skipna=skipna)
        else:
            da_o = da.mean(dim=dim, keep_attrs=keep_attrs, skipna=skipna, **kwargs)
    return da_o


def remove_fit(
        da: array_wrapper,
        deg: int = 1,
        dim: Union[Hashable, str] = "T",
        kwargs_polyfit: dict = None,
        **kwargs):
    """
    Compute the least squares polynomial fit, evaluate fit and remove it.
    https://docs.xarray.dev/en/stable/generated/xarray.DataArray.polyfit.html
    https://docs.xarray.dev/en/stable/generated/xarray.polyval.html

    Input:
    ------
    :param da: xarray.DataArray
    :param deg: int, optional
        Degree of the fitting polynomial; e.g., deg = 1
        Default is 1
    :param dim: Hashable or str, optional
        Dimension(s) over which to apply polyfit; e.g., dim = "T"
        Default is "T"
    :param kwargs_polyfit: dict, optional
        Key arguments passed to xarray polyfit (see url above);
        e.g., kwargs_polyfit = {
            'cov': bool,
            'full': bool,
            'rcond': float or None,
            'skipna': bool,
            'w': Hashable or array-like or None
        }
        Default is None
    **kwargs - Discarded

    Output:
    -------
    :return: xarray.DataArray
         New DataArray object with the least squares polynomial fit removed along the indicated dimension.
    """
    kwargs_polyfit = tools.none_to_default(kwargs_polyfit, {})
    da_o = None
    # fake loop to be able to break out when an error occurs
    for _ in [0]:
        # get dimension name in da
        dim = xt.check_dim(da, dim)
        if dim is None:
            break
        # compute coefficient
        p = da.polyfit(dim, deg, **kwargs_polyfit)
        # remove fit
        da_o = da.copy(deep=True) - xb.polynomial_fit(da[dim], p["polyfit_coefficients"])
    return da_o


def reshape_splice(
        da: array_wrapper,
        delta: int = 12,
        dim: Union[Hashable, str] = None,
        window: int = 24,
        **kwargs) -> Union[array_wrapper, None]:
    # set given dimension as first dimension
    da_o = xt.set_dim_as_first(da, dim)
    if da_o is not None:
        # splice using numpy
        da_o = numpy_tools.splice(da_o.to_numpy(), delta, window)
        # dimensions
        dim_name = xt.check_dim(da, dim)
        time_dim = xt.check_dim(da, "T")
        # recreate array
        if tools.is_dim(time_dim) is True and dim_name == time_dim and isinstance(delta, int) is True and delta == 12 \
                and isinstance(window, int) is True and window % 12 == 0:
            # time splicing on year / month
            year = int(xt.get_time_bounds(da)[0].split("-")[0])
            coordinates = {
                "year": numpy__array(list(range(year, year + da_o.shape[0]))),
                "month": numpy__array(list(range(da_o.shape[1]))),
            }
            dim_added = ["year", "month"]
        else:
            coordinates = {
                str(dim_name) + "_a": numpy__array(list(range(da_o.shape[0]))),
                str(dim_name) + "_b": numpy__array(list(range(da_o.shape[1]))),
            }
            dim_added = [str(dim_name) + "_a", str(dim_name) + "_b"]
        da_o = xt.recreate_array(
            da_o, da, axis_added=[0, 1], coords_added=coordinates, dim_added=dim_added, dim_removed=[dim_name])
    return da_o
# ---------------------------------------------------------------------------------------------------------------------#
