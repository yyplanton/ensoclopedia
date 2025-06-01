# -*- coding:UTF-8 -*-
# ---------------------------------------------------------------------------------------------------------------------#
# Processors built over xarray
# ---------------------------------------------------------------------------------------------------------------------#


# ---------------------------------------------------#
# Import packages
# ---------------------------------------------------#
# basic python package
from copy import deepcopy as copy__deepcopy
from inspect import getmembers as inspect__getmembers
from inspect import isfunction as inspect__isfunction
from inspect import stack as inspect__stack
from json import dumps as json__dumps
from typing import Hashable, Literal, Union
from sys import modules as sys__modules

from xarray.util.generate_aggregations import skipna

# local functions
from ensoclopedia.wrapper import tools
from ensoclopedia.wrapper import xarray_tools as xt
from ensoclopedia.wrapper.wrapper_tools import da_ds_execute
from ensoclopedia.wrapper import xarray_base as xb
from ensoclopedia.wrapper.xarray_base import array_wrapper, dataset_wrapper
# ---------------------------------------------------#


# ---------------------------------------------------------------------------------------------------------------------#
# Functions
# ---------------------------------------------------------------------------------------------------------------------#
def average(
        ds: Union[array_wrapper, dataset_wrapper],
        dim: Union[Hashable, str, list[Hashable], list[str], tuple[Hashable], tuple[str]] = "T",
        variable: list[str] = None,
        kwargs_mean_weighted: dict = None,
        **kwargs) -> Union[array_wrapper, dataset_wrapper, None]:
    """
    Reduce this object’s data by applying mean along some dimension(s).

    Input:
    ------
    :param ds: xarray.DataArray or xarray.Dataset
    :param dim: Hashable or Iterable of Hashable, optional
        Dimension(s) over which to apply the weighted mean; e.g., dim = "X" or dim = ("X", "Y")
        Default is "T"
    :param variable: variable: list[str], optional
        List of variables in ds if it is xarray.Dataset; e.g., variable = ["ts"]
        If ds is xarray.Dataset, variable should be provided
        Default is None
    :param kwargs_mean_weighted: dict, optional
        Key arguments passed to the function mean_weighted;
        e.g., kwargs_mean_weighted = {
            'dim': str,
            'keep_attrs': bool,
            'skipna': bool,
            'weights': xarray.DataArray or numpy.ndarray,
            **other_kwargs,
        }
        Default is None
    **kwargs - Discarded

    Output:
    -------
    :return: xarray.DataArray or xarray.Dataset
        New object (as input) with mean or weighted mean applied to its data and the indicated dimension(s) removed.
    """
    kwargs_mean_weighted = tools.none_to_default(kwargs_mean_weighted, {})
    tools.remove_keys(kwargs_mean_weighted, keys_to_remove=["dim"])
    # compute weighted average
    return da_ds_execute(ds, "mean_weighted", dim=dim, variable=variable, **kwargs_mean_weighted)


def average_moving(
        ds: Union[array_wrapper, dataset_wrapper],
        dim: Union[Hashable, str] = "T",
        min_periods: Union[int, None] = None,
        window: int = 3,
        **kwargs) -> Union[array_wrapper, dataset_wrapper, None]:
    """
    Compute a moving average along given dimension.
    https://docs.xarray.dev/en/stable/generated/xarray.Dataset.rolling.html
    https://docs.xarray.dev/en/stable/generated/xarray.DataArray.rolling.html

    Input:
    ------
    :param ds: xarray.DataArray or xarray.Dataset
    :param dim: Hashable or str, optional
        Dimension over which to apply rolling; e.g., dim = "T"
        Default is "T"
    :param min_periods: int or None, optional
        Minimum number of observations in window required to have a value (otherwise result is NA).
        None is equivalent to setting min_periods equal to the size of the window; e.g., min_periods = None
        Default is None
    :param window: int, optional
        Number of observations to average; e.g., window = 3
        Default is 3
    **kwargs - Discarded

    Output:
    -------
    :return: xarray.DataArray or xarray.Dataset
         New DataArray object with the moving average computed along given dimension.
    """
    ds_o = None
    # fake loop to be able to break out when an error occurs
    for _ in [0]:
        # get dimension name in ds
        dim_name = xt.check_dim(ds, dim)
        if dim is None:
            break
        # get time dimension
        dim_time = xt.cf_dim_to_dim(ds, "T")
        # weights along dimension
        if tools.is_dim(dim_time) is True and dim_time == dim_name:
            weights = xt.weights_time(ds)
        else:
            weights = xb.array_ones(ds[dim_name])
        # input multiplied by weights
        ds_o = ds * weights
        # compute rolling (moving) window sum of da_o
        ds_o = ds_o.rolling(dim={dim_name: window}, center=True, min_periods=min_periods).sum(keep_attrs=True)
        # divide by rolling (moving) window sum of weights
        ds_o = ds_o / weights.rolling(dim={dim_name: window}, center=True, min_periods=min_periods).sum()
    return ds_o


def detrend(
        ds: Union[array_wrapper, dataset_wrapper],
        deg: int = 1,
        variable: list[str] = None,
        kwargs_remove_fit: dict = None,
        **kwargs) -> Union[array_wrapper, dataset_wrapper]:
    """
    Detrend the time dimension of given object.

    Input:
    ------
    :param ds: xarray.DataArray or xarray.Dataset
    :param deg: int, optional
        Degree of the polynomial used to detrend; e.g., deg = 1
        Default is 1
    :param variable: list[str], optional
        List of variables in ds if it is xarray.Dataset; e.g., variable = ["ts"]
        If ds is xarray.Dataset, variable must be provided
        Default is None
    :param kwargs_remove_fit: dict, optional
        Key arguments passed to the function kwargs_remove_fit;
        e.g., kwargs_remove_fit = {
            'kwargs_polyfit': dict,
        }
        Default is None
    **kwargs - Discarded

    Output:
    -------
    :return: xarray.DataArray or xarray.Dataset
        New object (as input) detrend along the time dimension
    """
    kwargs_remove_fit = tools.none_to_default(kwargs_remove_fit, {})
    tools.remove_keys(kwargs_remove_fit, keys_to_remove=["deg", "dim"])
    # compute weighted average
    return da_ds_execute(ds, "remove_fit", variable=variable, deg=deg, dim="T", **kwargs_remove_fit)


def interannual_anomalies(
        ds: Union[array_wrapper, dataset_wrapper],
        kwargs_groupby: dict = None,
        kwargs_seasonal_cycle: dict = None,
        **kwargs) -> Union[array_wrapper, dataset_wrapper]:
    """
    Compute interannual anomalies.
    https://docs.xarray.dev/en/stable/generated/xarray.Dataset.groupby.html
    https://docs.xarray.dev/en/stable/generated/xarray.DataArray.groupby.html

    Input:
    ------
    :param ds: xarray.DataArray or xarray.Dataset
    :param kwargs_groupby: dict, optional
        Key arguments passed to xarray groupby (see url above);
        e.g., kwargs_groupby = {
            restore_coord_dims: bool,
        }
        Default is None
    :param kwargs_seasonal_cycle: dict, optional
        Key arguments passed to the function seasonal_cycle;
        e.g., kwargs_groupby = {
            kwargs_groupby: dict,
            kwargs_mean: dict,
        }
        Default is None
    **kwargs - Discarded

    Output:
    -------
    :return: xarray.DataArray or xarray.Dataset
        Object (as input) with seasonal cycle removed
    """
    kwargs_groupby = tools.none_to_default(kwargs_groupby, {})
    tools.remove_keys(kwargs_groupby, desired_keys=["restore_coord_dims"])
    kwargs_seasonal_cycle = tools.none_to_default(kwargs_seasonal_cycle, {})
    ds_o = None
    # fake loop to be able to break out when an error occurs
    for _ in [0]:
        # find time dimension
        dim_time = xt.cf_dim_to_dim(ds, "T")
        if tools.is_dim(dim_time) is False:
            break
        # compute seasonal cycle
        ds = ds.compute()
        sea_cycle = seasonal_cycle(ds, **kwargs_seasonal_cycle)
        sea_cycle = sea_cycle.compute()
        if sea_cycle is None:
            break
        # remove seasonal cycle
        ds_o = ds.groupby(group=str(dim_time) + ".month", **kwargs_groupby) - sea_cycle
        if ds_o is None:
            break
        # remove unused dimensions
        ds_o = xt.remove_unused_coordinates(ds_o)
    return ds_o


def netcdf_reader(
        bounds: dict[str, tuple[str, str]] = None,
        ensure_constant_mask: bool = False,
        filename: Union[str, list[str]] = None,
        remove_regional_mean: dict = None,
        variable: list[str] = None,
        kwargs_netcdf_open: dict = None,
        kwargs_netcdf_selector: dict = None,
        **kwargs) -> Union[dataset_wrapper, None]:
    """
    Open file(s) as a single dataset.

    Input:
    ------
    :param filename: str or list[str], optional
        Paths to dataset files:
            - Directory path (e.g., "path/to/files"), which is converted to a string glob of *.nc files
            - String glob (e.g., "path/to/files/*.nc"), which is expanded to a 1-dimensional list of file paths
            - File path to dataset (e.g., "path/to/files/file1.nc")
            - List of file paths (e.g., ["path/to/files/file1.nc", ...])
        If multiple files, concatenation along the time dimension recommended
        Default is None
    :param bounds: dict[str, tuple[str, str]], optional
        Dictionary of desired bounds to select along the specified dimension(s);
        e.g., bounds = {"T": ("1980-01-01", "2014-12-31")}
        Default is None
    :param ensure_constant_mask: bool, optional
        True to ensure that the mask is constant through time; e.g., ensure_constant_mask = True
        Default is False
    :param remove_regional_mean: dict, optional
        Pass a dictionary defining spatial bounds of the region to average;
        e.g., remove_regional_mean = {
            "bounds": {"X": (0., 360.), "Y": (-90., 90.)},
            "kwargs_mean_weighted": {"dim": ("X", "Y")}, -> see mean_weighted for keywords
            "kwargs_netcdf_selector": {}, -> see netcdf_selector for keywords
        }
    :param variable: list[str], optional
        List of variables to read in filename
        Default is None
    :param kwargs_netcdf_open: dict, optional
        Key arguments for xt.netcdf_open
        Default is None
    :param kwargs_netcdf_selector: dict, optional
        Key arguments for selector_netcdf
        Default is None
    **kwargs - Discarded

    Output:
    -------
    :return: xarray.Dataset
        Newly created dataset. Note that T, X, Y dimensions will be renamed time, longitude, latitude
    """
    kwargs_netcdf_open = tools.none_to_default(kwargs_netcdf_open, {})
    kwargs_netcdf_selector = tools.none_to_default(kwargs_netcdf_selector, {})
    tools.remove_keys(kwargs_netcdf_selector, keys_to_remove=["bounds"])
    remove_regional_mean = tools.none_to_default(remove_regional_mean, {})
    ds = None
    if filename is not None and isinstance(filename, (str, list)) is True:
        # create dataset
        ds = xt.netcdf_open(filename, variable, **kwargs_netcdf_open)
        # remove regional mean
        if "bounds" in list(remove_regional_mean.keys()) and \
                isinstance(remove_regional_mean["bounds"], dict) is True and \
                len(list(remove_regional_mean["bounds"].keys())) > 0:
            # select region
            bd = copy__deepcopy(remove_regional_mean["bounds"])
            kw = {}
            if "kwargs_netcdf_selector" in list(remove_regional_mean.keys()) and \
                    isinstance(remove_regional_mean["kwargs_netcdf_selector"], dict) is True:
                kw = copy__deepcopy(remove_regional_mean["kwargs_netcdf_selector"])
            ds_reg = netcdf_selector(ds, bounds=bd, **kw)
            # spatial average
            kw = {}
            if "kwargs_mean_weighted" in list(remove_regional_mean.keys()) and \
                    isinstance(remove_regional_mean["kwargs_mean_weighted"], dict) is True:
                kw = copy__deepcopy(remove_regional_mean["kwargs_mean_weighted"])
            tools.remove_keys(kw, keys_to_remove=["dim"])
            ds_reg = average(ds_reg, dim=("X", "Y"), variable=variable, kwargs_mean_weighted=kw)
            # remove spatial average
            ds = ds - ds_reg
        # select bounds
        ds = netcdf_selector(ds, bounds=bounds, **kwargs_netcdf_selector)
        # find time dimension
        dim_time = xt.cf_dim_to_dim(ds, "T")
        # mask constant through time
        if tools.is_dim(dim_time) is True and ensure_constant_mask is True:
            ds = xt.constant_mask(ds)
    return ds


def netcdf_selector(
        ds: Union[array_wrapper, dataset_wrapper],
        bounds: dict[str, Union[tuple[str, str], tuple[float, float]]] = None,
        kwargs_check_time_bounds: dict = None,
        kwargs_sel: dict = None,
        **kwargs) -> Union[array_wrapper, dataset_wrapper]:
    """
    Select bounds.
    https://docs.xarray.dev/en/latest/generated/xarray.Dataset.sel.html
    https://docs.xarray.dev/en/latest/generated/xarray.DataArray.sel.html

    Input:
    ------
    :param ds: xarray.DataArray or xarray.Dataset
    :param bounds: dict[str, tuple[str, str]], optional
        Dictionary of desired bounds to select along the specified dimension(s);
        e.g., bounds = {"T": ("1980-01-01", "2014-12-31")}
        Default is None
    :param kwargs_check_time_bounds: dict
        Key arguments passed to xt.check_time_bounds;
        e.g., kwargs_check_time_bounds = {
            'kwargs_isel': dict,
        }
        Default is None
    :param kwargs_sel: dict, optional
        Key arguments for xarray sel (see url above);
        e.g., kwargs_sel = {
            'drop': bool,
            'method': {None, "nearest", "pad", "ffill", "backfill", "bfill"},
            'tolerance': ?,
        }
        Default is None
    **kwargs - Discarded

    Output:
    -------
    :return: xarray.DataArray or xarray.Dataset
        Object (as input) with selected data along the specified dimension(s)
    """
    kwargs_check_time_bounds = tools.none_to_default(kwargs_check_time_bounds, {})
    kwargs_sel = tools.none_to_default(kwargs_sel, {})
    tools.remove_keys(kwargs_sel, desired_keys=["drop", "method", "tolerance"])
    if isinstance(bounds, dict) is True and len(list(bounds.keys())) > 0:
        # get dimension name
        coordinates1, coordinates2 = {}, {}
        for k1, k2 in bounds.items():
            dim_name = copy__deepcopy(k1)
            if k1 in ["T", "X", "Y"]:
                dim_name = xt.cf_dim_to_dim(ds, k1)
            if tools.is_dim(dim_name) is True and isinstance(k2, tuple) is True and len(k2) == 2:
                coordinates1[dim_name] = slice(*k2)
                coordinates2[dim_name] = copy__deepcopy(k2)
        # select using bounds like ("1980-01-01", "2014-12-31")
        if len(list(coordinates1.keys())) > 0:
            dim_time = xt.cf_dim_to_dim(ds, "T")
            dim_lon = xt.cf_dim_to_dim(ds, "X")
            dim_lat = xt.cf_dim_to_dim(ds, "Y")
            # longitudes are usually [0; 360], if desired bounds are on another scale, e.g., [-180; 180], roll longitude
            if tools.is_dim(dim_lon) is True and dim_lon in list(coordinates2.keys()) and \
                    (min(coordinates2[dim_lon]) < 0 or max(coordinates2[dim_lon]) > 360):
                # minimum value of coordinates1[dim_lon]
                lon_min = min(coordinates2[dim_lon])
                if max(coordinates2[dim_lon]) - lon_min < 360:
                    # modify minimum to be slightly lower, a maximum of 10 degree lower
                    lon_min -= min(10, 360 - (max(coordinates2[dim_lon]) - lon_min) / 2)
                # update longitude and roll, i.e., add minimum value to dataset's longitude to shift the dimension
                # e.g., initial longitude = [0; 360], desired = [-60; 30], lon_min = -70, new longitude = [-70; 290]
                ds = xt.roll_longitude(ds, lon_min)
            # select
            print("netcdf_selector", bounds)
            if xt.check_multidimensional_coordinates(ds) is False:
                # normal selection method
                ds = ds.sel(indexers=coordinates1, **kwargs_sel)
            else:
                print("netcdf_selector multidimensional coordinates", bounds)
                # for multidimensional coordinates (e.g., curvilinear grids)
                # select time
                if tools.is_dim(dim_time) is True and dim_time in list(coordinates1.keys()):
                    ds = ds.sel(indexers={dim_time: coordinates1[dim_time]}, **kwargs_sel)
                # select X / Y
                if (tools.is_dim(dim_lat) is True and dim_lat in list(coordinates1.keys())) or (
                        tools.is_dim(dim_lon) is True and dim_lon in list(coordinates1.keys())):
                    # create condition
                    if dim_lat in list(coordinates1.keys()) and dim_lon not in list(coordinates1.keys()):
                        # select Y
                        arr_lat = ds[dim_lat]
                        cond = (coordinates2[dim_lat][0] < arr_lat) & (arr_lat < coordinates2[dim_lat][1])
                    elif dim_lat not in list(coordinates1.keys()) and dim_lon in list(coordinates1.keys()):
                        # select X
                        arr_lon = ds[dim_lon]
                        cond = (coordinates2[dim_lon][0] < arr_lon) & (arr_lon < coordinates2[dim_lon][1])
                    else:
                        # select X / Y
                        arr_lat, arr_lon = ds[dim_lat], ds[dim_lon]
                        cond = (coordinates2[dim_lat][0] <= arr_lat) & (arr_lat <= coordinates2[dim_lat][1]) & \
                              (coordinates2[dim_lon][0] <= arr_lon) & (arr_lon <= coordinates2[dim_lon][1])
                    ds = ds.where(cond)
        # sometimes selecting time is slightly wrong
        # this section checks if one time step has been included by error at the beginning or the end of the time series
        dim_time = xt.cf_dim_to_dim(ds, "T")
        if tools.is_dim(dim_time) and dim_time in list(coordinates2.keys()):
            # check lower time bound
            ds = xt.check_time_bounds(ds, coordinates2[dim_time], "lower", **kwargs_check_time_bounds)
            # check upper time bound
            ds = xt.check_time_bounds(ds, coordinates2[dim_time], "upper", **kwargs_check_time_bounds)
    return ds


def netcdf_writer(
        ds: Union[array_wrapper, dataset_wrapper],
        filename: str,
        kwargs_to_netcdf: dict = None,
        **kwargs):
    """
    Write DataArray or Dataset contents to a netCDF file.
    https://docs.xarray.dev/en/stable/generated/xarray.Dataset.to_netcdf.html
    https://docs.xarray.dev/en/stable/generated/xarray.DataArray.to_netcdf.html

    Input:
    ------
    :param ds: xarray.DataArray or xarray.Dataset
    :param filename: str
        Path to which to save the DataArray or Dataset
    :param kwargs_to_netcdf: dict, optional
        Key arguments passed to xarray to_netcdf (see url above)
        Default is None
    **kwargs - Discarded
    """
    kwargs_to_netcdf = tools.none_to_default(kwargs_to_netcdf, {})
    # check key arguments
    known_kwargs = ["auto_complex", "compute", "encoding", "engine", "format", "group", "invalid_netcdf", "mode",
                    "unlimited_dims"]
    tools.remove_keys(kwargs_to_netcdf, desired_keys=known_kwargs)
    # remove unused dimensions
    ds = xt.remove_unused_coordinates(ds)
    # save object as Netcdf
    ds.to_netcdf(path=filename, **kwargs_to_netcdf)


def processor(
        ds: Union[array_wrapper, dataset_wrapper],
        processors: dict,
        variable: list[str] = None,
        **kwargs) -> Union[array_wrapper, dataset_wrapper, None]:
    """
    Compute multiple processors one after the other on input object

    Input:
    ------
    :param ds: xarray.DataArray or xarray.Dataset
    :param processors: dict of dict
        Dictionary of processors names and associated keywords;
        e.g., processors = {
            '1--interannual_anomalies': {},
            '2--normalize': {},
            '3--average': {},
        }
        Processors or functions in current module. See each function for their required keywords
    :param variable: variable: list[str], optional
        List of variables in ds if it is xarray.Dataset; e.g., variable = ["ts"]
        If ds is xarray.Dataset, variable should be provided
        Default is None
    **kwargs - Discarded

    Output:
    -------
    :return: xarray.DataArray or xarray.Dataset
        Object (as input) with processors applied
    """
    # loop on processors to apply to object
    for k1 in list(processors.keys()):
        # get processor name
        process = k1.split("--")[-1]
        # list of processors
        known_processors = [name for name, obj in inspect__getmembers(sys__modules[__name__])
                            if (inspect__isfunction(obj) and name != "processor" and "__" not in name)]
        # check if it is a known processor
        if process not in known_processors:
            message = tools.unknown_formater("processor", process, known_processors)
            tools.print_fail(inspect__stack(), message, fail_i=False)
            continue
        # apply processor
        print("processor", process)
        v1 = list(ds.keys())[0]
        print("in ", v1, ds[v1].shape, float(ds[v1].min()), float(ds[v1].max()), list(ds.coords))
        print(ds.coords)
        ds = globals()[process](ds, variable=variable, **processors[k1])
        print("out", v1, ds[v1].shape, float(ds[v1].min()), float(ds[v1].max()), list(ds.coords))
        print(ds.coords)
        if ds is None:
            break
    return ds


def normalize(
        ds: Union[array_wrapper, dataset_wrapper],
        variable: list[str] = None,
        kwargs_std: dict = None,
        **kwargs) -> Union[array_wrapper, dataset_wrapper]:
    """
    Normalize distributions by dividing them by their standard deviation.
    https://docs.xarray.dev/en/stable/generated/xarray.Dataset.std.html
    https://docs.xarray.dev/en/stable/generated/xarray.DataArray.std.html

    Input:
    ------
    :param ds: xarray.DataArray or xarray.Dataset
    :param variable: variable: list[str], optional
        List of variables in ds if it is xarray.Dataset; e.g., variable = ["ts"]
        If ds is xarray.Dataset, variable should be provided
        Default is None
    :param kwargs_std: dict, optional
        Additional key arguments for xarray std (see url above);
        e.g., kwargs_std = {
            'ddof': int,
            'keep_attrs': bool,
            'skipna': bool,
            **other_kwargs
        }
        Default is None
    **kwargs - Discarded

    Output:
    -------
    :return: xarray.DataArray or xarray.Dataset
        Object as input with normalized distributions
    """
    kwargs_std = tools.none_to_default(kwargs_std, {})
    tools.remove_keys(kwargs_std, keys_to_remove=["dim"])
    ds_o = None
    # find time dimension
    dim_time = xt.cf_dim_to_dim(ds, "T")
    # normalize distributions
    if tools.is_dim(dim_time) is True:
        ds_o = ds.copy(deep=True) / ds.std(dim=dim_time, **kwargs_std)
        if isinstance(ds, dataset_wrapper) is True:
            # update units
            for k in xt.get_variables(ds, variable=variable):
                if "units" in list(ds[k].attrs):
                    ds_o[k].attrs["units"] = ""
        else:
            if "units" in list(ds.attrs):
                ds_o.attrs["units"] = ""
    return ds_o


def reshape_lead_lag(
        ds: Union[array_wrapper, dataset_wrapper],
        delta: int = 12,
        window: int = 24,
        variable: list[str] = None,
        **kwargs) -> Union[array_wrapper, dataset_wrapper, None]:
    """
    Reduce this object’s data by applying mean along some dimension(s).

    Input:
    ------
    :param ds: xarray.DataArray or xarray.Dataset
    :param delta: int, optional
        Number of time step to shift the data at each splice; e.g., delta = 12
        Default is 12
    :param window: int, optional
        Number of time steps of the window; e.g., window = 24
        Default is 24
    :param variable: variable: list[str], optional
        List of variables in ds if it is xarray.Dataset; e.g., variable = ["ts"]
        If ds is xarray.Dataset, variable should be provided
        Default is None
    **kwargs - Discarded

    Output:
    -------
    :return: xarray.DataArray or xarray.Dataset
        New object (as input) reshaped according to instructions.
    """
    # compute splice
    return da_ds_execute(ds, "reshape_splice", variable=variable, delta=delta, dim="T", window=window)


def season_mean(
        ds: Union[array_wrapper, dataset_wrapper],
        season: Literal["DJF", "JFM", "FMA", "MAM", "AMJ", "MJJ", "JJA", "JAS", "ASO", "SON", "OND", "NDJ"] = "NDJ",
        kwargs_average_moving: dict = None,
        kwargs_get_season: dict = None,
        **kwargs) -> Union[array_wrapper, dataset_wrapper, None]:
    """
    Average data over a given season.

    Input:
    ------
    :param ds: xarray.DataArray or xarray.Dataset
    :param season: {"DJF", "JFM", "FMA", "MAM", "AMJ", "MJJ", "JJA", "JAS", "ASO", "SON", "OND", "NDJ"}
        Name of a season
        Default is 'NDJ'
    :param kwargs_average_moving: dict, optional
        Key arguments passed to the function average_moving;
        e.g., kwargs_average_moving = {
            'min_periods': int,
        }
        Default is None
    :param kwargs_get_season: dict, optional
        Key arguments passed to the function get_season;
        e.g., kwargs_get_season = {
            'drop': bool,
            'missing_dims': {"raise", "warn", "ignore"},
            'restore_coord_dims': bool,
        }
        Default is None
    **kwargs - Discarded

    Output:
    -------
    :return: xarray.DataArray or xarray.Dataset
        Object (as input) with the data averaged over a given season.
    """
    kwargs_average_moving = tools.none_to_default(kwargs_average_moving, {})
    tools.remove_keys(kwargs_average_moving, keys_to_remove=["dim", "window"])
    kwargs_get_season = tools.none_to_default(kwargs_get_season, {})
    tools.remove_keys(kwargs_get_season, keys_to_remove=["season"])
    # fake loop to be able to break out when an error occurs
    for _ in [0]:
        # moving average over 3 time steps
        ds_o = average_moving(ds, dim="T", window=3, **kwargs_average_moving)
        if ds_o is None:
            break
        # select desired season
        ds_o = xt.get_season(ds_o, season=season, **kwargs_get_season)
        if ds_o is None:
            break
        # remove unused dimensions
        ds_o = xt.remove_unused_coordinates(ds_o)
    return ds_o


def seasonal_cycle(
        ds: Union[array_wrapper, dataset_wrapper],
        kwargs_groupby: dict = None,
        kwargs_mean: dict = None,
        **kwargs) -> Union[array_wrapper, dataset_wrapper]:
    """
    Compute seasonal cycle.
    https://docs.xarray.dev/en/stable/generated/xarray.Dataset.groupby.html
    https://docs.xarray.dev/en/stable/generated/xarray.DataArray.groupby.html
    https://docs.xarray.dev/en/stable/generated/xarray.Dataset.mean.html
    https://docs.xarray.dev/en/stable/generated/xarray.DataArray.mean.html

    Input:
    ------
    :param ds: xarray.DataArray or xarray.Dataset
    :param kwargs_groupby: dict, optional
        Key arguments passed to xarray groupby (see url above);
        e.g., kwargs_groupby = {
            'restore_coord_dims': bool,
        }
        Default is None
    :param kwargs_mean: dict, optional
        Key arguments passed to xarray mean (see url above);
        e.g., kwargs_mean = {
            'keep_attrs': bool,
            'skipna': bool,
            **other_kwargs
        }
        Default is None
    **kwargs - Discarded

    Output:
    -------
    :return: xarray.DataArray or xarray.Dataset
        Object (as input) with seasonal cycle
    """
    kwargs_groupby = tools.none_to_default(kwargs_groupby, {})
    tools.remove_keys(kwargs_groupby, desired_keys=["restore_coord_dims"])
    kwargs_mean = tools.none_to_default(kwargs_mean, {})
    tools.remove_keys(kwargs_mean, keys_to_remove=["dim"])
    # find time dimension
    dim_time = xt.cf_dim_to_dim(ds, "T")
    # compute seasonal cycle
    if dim_time is not None and isinstance(dim_time, (Hashable, str)) is True:
        # regroup by month
        ds = ds.groupby(str(dim_time) + ".month", **kwargs_groupby)
        # mean along the time dimension
        ds = ds.mean(dim=dim_time, **kwargs_mean)
    return ds


def select_variable(ds: Union[array_wrapper, dataset_wrapper], variable: str, **kwargs) -> array_wrapper:
    if isinstance(ds, dataset_wrapper) is True:
        ds = ds[variable]
    return ds
# ---------------------------------------------------------------------------------------------------------------------#
