# -*- coding:UTF-8 -*-
# ---------------------------------------------------------------------------------------------------------------------#
# Functions built over xarray
# ---------------------------------------------------------------------------------------------------------------------#


# ---------------------------------------------------#
# Import packages
# ---------------------------------------------------#
# basic python package
from copy import deepcopy as copy__deepcopy
from inspect import stack as inspect__stack
from json import dumps as json__dumps
from re import split as re__split
from typing import Literal, Union, Hashable

# numpy
from numpy import array as numpy__array
from numpy import ndarray as numpy__ndarray

# xarray
import xarray

# local functions
from ensoclopedia.wrapper import tools
from ensoclopedia.wrapper import time_tools as tt
from ensoclopedia.wrapper.xarray_base import array_wrapper, dataset_wrapper
# ---------------------------------------------------#


# ---------------------------------------------------------------------------------------------------------------------#
# Functions
# ---------------------------------------------------------------------------------------------------------------------#
def _split_time_bound(time_bound: str) -> list[str]:
    """
    Split string by multiple delimiter patterns: '-', ' ' or ':'.

    Input:
    ------
    :param time_bound: str
        Any string but usually a time bound, e.g., time_bound = '1980-01-15 12:00:00.0'

    Output:
    -------
    :return: list[str]
        List of string corresponding to input time_bound split at each '-', ' ' or ':'
    """
    return re__split("-| |:", time_bound)


def cf_dim_to_dim(
        ds: Union[array_wrapper, dataset_wrapper],
        cf_dim: Literal["T", "X", "Y"],
        **kwargs) -> Union[Hashable, str, None]:
    """
    Return dimension name corresponding to CF dimension name (T is time, X is longitude, Y is latitude).

    Input:
    ------
    :param ds: xarray.DataArray or xarray.Dataset
        DataArray or Dataset
    :param cf_dim: {"X", "Y", "T", "Z"}
        Name of a CF dimension
    **kwargs - Discarded

    Output:
    -------
    :return: Hashable or str or None
        Name of given CF dimension in input xarray.DataArray or xarray.Dataset.
    """
    # list dimension
    list_dim = list(ds.coords)
    # dimension to find
    dim_to_find = {
        "T": ["time", "tim"],
        "X": ["longitude", "lon", "x"],
        "Y": ["latitude", "lat", "y"],
    }
    # find the name in the dataset
    dim_o = None
    for k1 in dim_to_find[cf_dim]:
        if k1 in list_dim:
            # k1 is a dimension name in ds
            dim_o = copy__deepcopy(k1)
            break
        else:
            # k1 is not an exact match -> check if k1 is included in a dimension name
            for k2 in list_dim:
                # if k1 is a single letter it must be the first letter k2 (dimension name)
                #     e.g., k1 = 'x', if k2 = 'xt_ocean' or 'x_dim', k2 is probably the dimension we are looking for
                # otherwise, k1 must be included in k2 (dimension name)
                #     e.g., k1 = 'lon', if k2 = 'dim_lon' or 'dim_lon', k2 is probably the dimension we are looking for
                if (len(k1) == 1 and k2[:1] == k1) or (len(k1) > 1 and k1 in k2):
                    dim_o = copy__deepcopy(k2)
                    break
        if tools.is_dim(dim_o) is True:
            break
    return dim_o


def check_dim(
        ds: Union[array_wrapper, dataset_wrapper],
        dim: Union[Hashable, str],
        **kwargs) -> Union[Hashable, str]:
    """
    Ensures that desired dimension exists in given object.

    Input:
    ------
    :param ds: xarray.DataArray or xarray.Dataset
        DataArray or Dataset
    :param dim: Hashable or str
        Dimension name
    **kwargs - Discarded

    Output:
    -------
    :return: Hashable or str
        Dimension name in ds
    """
    dim_o = None
    if dim is None or isinstance(dim, (Hashable, str)) is False:
        pass
    elif dim in ds.dims:
        dim_o = copy__deepcopy(dim)
    elif dim in ["T", "X", "Y"]:
        dim_o = cf_dim_to_dim(ds, dim)
    if dim_o is None or isinstance(dim_o, (Hashable, str)) is False:
        tools.print_fail(inspect__stack(), tools.unknown_formater("dimension", dim, ds.dims), fail_i=False)
    return dim_o


def check_multidimensional_coordinates(ds: Union[array_wrapper, dataset_wrapper], **kwargs) -> bool:
    dim_lat = cf_dim_to_dim(ds, "Y")
    dim_lon = cf_dim_to_dim(ds, "X")
    bool_o = False
    if (tools.is_dim(dim_lat) is True and len(ds[dim_lat].shape) > 1) or (
            tools.is_dim(dim_lon) is True and len(ds[dim_lon].shape) > 1):
        bool_o = True
    return bool_o


def check_time_bounds(
        ds: Union[array_wrapper, dataset_wrapper],
        time_bounds: Union[tuple[str, str]],
        side: Literal["lower", "upper"],
        kwargs_isel: dict = None,
        **kwargs) -> Union[array_wrapper, dataset_wrapper]:
    """
    Check if desired time bounds were properly selected, i.e., did one time step has been included by error at the
    beginning or the end of the time series.
    https://docs.xarray.dev/en/latest/generated/xarray.Dataset.isel.html
    https://docs.xarray.dev/en/latest/generated/xarray.DataArray.isel.html

    Input:
    ------
    :param ds: xarray.DataArray or xarray.Dataset
        DataArray or Dataset
    :param time_bounds: tuple[str]
        Time bounds desired
    :param side: {"lower", "upper"}
        Side of bounds to be checked (lower and upper correspond respectively to the first and last time steps)
    :param kwargs_isel: dict, optional
        Key arguments for xarray isel (see url above);
        e.g., kwargs_isel = {
            'drop': bool,
            'missing_dims': {"raise", "warn", "ignore"},
        }
        Default is None
    **kwargs - Discarded

    Output:
    -------
    :return: xarray.DataArray or xarray.Dataset
        Object (as input) with time bounds checked
    """
    kwargs_isel = tools.none_to_default(kwargs_isel, {})
    tools.remove_keys(kwargs_isel, desired_keys=["drop", "missing"])
    # get time dimension
    dim_time = cf_dim_to_dim(ds, "T")
    # fake loop to be able to break out when an error occurs
    l0 = [0] if isinstance(dim_time, str) is True else []
    for _ in l0:
        # bound position (0 or 1)
        position = 0 if side == "lower" else 1
        # split time bound in ["year", "month", "day"]
        tb = get_time_bounds(ds)
        if tb is None:
            break
        split_ta = _split_time_bound(tb[position])
        split_td = _split_time_bound(time_bounds[position])
        while (side == "lower" and all([float(k1) >= float(k2) for k1, k2 in zip(split_ta, split_td)]) is False) or \
                (side == "upper" and all([float(k1) <= float(k2) for k1, k2 in zip(split_ta, split_td)]) is False):
            # if side == "lower" & one of available("year", "month", "day") is smaller than desired
            # ("year", "month", "day")
            # or
            # if side == "upper" & one of available("year", "month", "day") is larger than desired
            # ("year", "month", "day")
            # remove the first (last) time step
            time_slice = slice(1, int(1e20)) if side == "lower" else slice(0, -1)
            ds = ds.isel(indexers={dim_time: time_slice}, **kwargs_isel)
            tb = get_time_bounds(ds)
            if tb is None:
                break
            split_ta = _split_time_bound(str(tb[position]))
    return ds


def constant_mask(
        ds: Union[array_wrapper, dataset_wrapper],
        **kwargs) -> Union[array_wrapper, dataset_wrapper]:
    """
    Ensure that the mask is constant along the time dimension.
    https://docs.xarray.dev/en/latest/generated/xarray.DataArray.sum.html
    https://docs.xarray.dev/en/stable/generated/xarray.DataArray.where.html

    Input:
    ------
    :param ds: xarray.DataArray or xarray.Dataset
        DataArray or Dataset
    **kwargs - Discarded

    Output:
    -------
    :return: xarray.DataArray or xarray.Dataset
        Object (as input) with constant mask along the time dimension
    """
    # find time dimension
    dim_time = cf_dim_to_dim(ds, "T")
    # constant mask along the time dimension
    if isinstance(dim_time, str) is True:
        if isinstance(ds, array_wrapper) is True:
            # sum mask through time
            mask = ds.isnull().astype('f').sum(dim=dim_time)
            # mask input data where at least one value is masked
            ds = ds.where(mask == 0)
        else:
            # loop on each data_var of the dataset
            for data_var in list(ds.keys()):
                if "_bounds" in data_var or "_bnds" in data_var:
                    continue
                # sum mask through time
                mask = ds[data_var].isnull().astype('f').sum(dim=dim_time)
                # mask input data where at least one value is masked
                ds[data_var] = ds[data_var].where(mask == 0)
    return ds


def get_season(
        ds: Union[array_wrapper, dataset_wrapper],
        season: Literal["DJF", "JFM", "FMA", "MAM", "AMJ", "MJJ", "JJA", "JAS", "ASO", "SON", "OND", "NDJ"] = "NDJ",
        kwargs_groupby: dict = None,
        kwargs_isel: dict = None,
        **kwargs) -> Union[array_wrapper, dataset_wrapper, None]:
    """
    Get values for given season (the moving average over seasons must be performed beforehand).
    https://docs.xarray.dev/en/stable/generated/xarray.Dataset.groupby.html
    https://docs.xarray.dev/en/stable/generated/xarray.DataArray.groupby.html
    https://docs.xarray.dev/en/stable/generated/xarray.Dataset.isel.html
    https://docs.xarray.dev/en/stable/generated/xarray.DataArray.isel.html

    Input:
    ------
    :param ds: xarray.DataArray or xarray.Dataset
        DataArray or Dataset
    :param season: {"DJF", "JFM", "FMA", "MAM", "AMJ", "MJJ", "JJA", "JAS", "ASO", "SON", "OND", "NDJ"}
        Name of a season
        Default is 'NDJ'
    :param kwargs_groupby: dict, optional
        Key arguments passed to xarray groupby (see url above);
        e.g., kwargs_groupby = {
            'restore_coord_dims': bool,
        }
        Default is None
    :param kwargs_isel: dict, optional
        Key arguments for xarray isel (see url above);
        e.g., kwargs_sel = {
            'drop': bool,
            'missing_dims': {"raise", "warn", "ignore"},
        }
        Default is None
    **kwargs - Discarded

    Output:
    -------
    :return: xarray.DataArray or xarray.Dataset
        Object (as input) with given season only
    """
    kwargs_isel = tools.none_to_default(kwargs_isel, {})
    tools.remove_keys(kwargs_isel, desired_keys=["drop", "missing_dims"])
    kwargs_groupby = tools.none_to_default(kwargs_groupby, {})
    tools.remove_keys(kwargs_isel, desired_keys=["restore_coord_dims"])
    ds_o = None
    centered_month_per_season = {
        "DJF": 1, "JFM": 2, "FMA": 3, "MAM": 4, "AMJ": 5, "MJJ": 6, "JJA": 7, "JAS": 8, "ASO": 9, "SON": 10, "OND": 11,
        "NDJ": 12,
    }
    # time dimension name
    dim_time = cf_dim_to_dim(ds, "T")
    if dim_time is not None and isinstance(dim_time, (Hashable, str)) is True:
        # Use .groupby('time.month') to organize the data into months
        # then use .groups to extract the indices for each month
        month_idxs = ds.groupby(group=str(dim_time) + ".month", **kwargs_groupby).groups
        # Extract the time indices corresponding to all 'season'
        idx = month_idxs[centered_month_per_season[season]]
        # Extract the 'season' months by selecting the relevant indices
        ds_o = ds.isel(indexers={dim_time: idx}, **kwargs_isel)
        # get time index
        time_ind = ds_o[dim_time].to_index()
        years = time_ind.year
        if season == "DJF":
            years += 1
        # change dimension
        ds_o = ds_o.assign_coords({dim_time: numpy__array(list(years))})
        ds_o = ds_o.rename({dim_time: "year"})
        # remove first or last time step depending on the case
        # rolling computes the first time step as DJF and last time step as NDJ, fills them with nans
        time_slice = slice(1, int(1e20)) if season == "DJF" else slice(0, -1)
        ds_o = ds_o.isel(indexers={"year": time_slice}, **kwargs_isel)
    return ds_o


def get_time_bounds(
        ds: Union[array_wrapper, dataset_wrapper],
        **kwargs) -> Union[tuple[str, str], None]:
    """
    Return first and last time values of given xarray.DataArray or xarray.Dataset.

    Input:
    ------
    :param ds: xarray.DataArray or xarray.Dataset
        DataArray or Dataset
    **kwargs - Discarded

    Output:
    -------
    :return: tuple[str, str] or None
        First and last time values.
    """
    list_o = None
    dim_time = cf_dim_to_dim(ds, "T")
    if isinstance(dim_time, str) is True:
        time_initial = ds[dim_time][0].values.astype("datetime64[D]")
        time_final = ds[dim_time][-1].values.astype("datetime64[D]")
        list_o = (str(time_initial), str(time_final))
    return list_o


def get_variables(
        ds: Union[array_wrapper, dataset_wrapper],
        variable: list[str] = None,
        **kwargs) -> Union[list[str], None]:
    list_variables = None
    if isinstance(ds, dataset_wrapper) is True:
        if tools.is_variables(variable) is True:
            list_variables = copy__deepcopy(variable)
        else:
            list_variables = [k for k in list(ds.keys()) if "bound" not in k and "bnd" not in k]
    return list_variables


def netcdf_open(
        filename: Union[str, list[str]],
        variable: Union[str, list[str], None],
        kwargs_open_mfdataset: dict = None,
        **kwargs) -> dataset_wrapper:
    """
    Open file(s) as a single dataset and ensures that longitudes are set from 0 to 360E
    https://docs.xarray.dev/en/latest/generated/xarray.open_mfdataset.html
    https://docs.xarray.dev/en/latest/generated/xarray.Dataset.assign_coords.html
    https://docs.xarray.dev/en/latest/generated/xarray.Dataset.roll.html
    https://docs.xarray.dev/en/latest/generated/xarray.Dataset.where.html

    Input:
    ------
    :param filename: str or list[str]
        Paths to dataset files:
            - Directory path (e.g., "path/to/files"), which is converted to a string glob of *.nc files
            - String glob (e.g., "path/to/files/*.nc"), which is expanded to a 1-dimensional list of file paths
            - File path to dataset (e.g., "path/to/files/file1.nc")
            - List of file paths (e.g., ["path/to/files/file1.nc", ...])
        If multiple files, concatenation along the time dimension recommended
    :param variable: list[str] or None
        List of variables to read in filename; e.g., variable = ['sst']
        This param overrides the keyword 'data_vars' in kwargs_open_mfdataset
    :param kwargs_open_mfdataset: dict, optional
        Key arguments for xarray open_mfdataset (see url above);
        e.g., kwargs_open_mfdataset = {
            'attrs_file': str or path-like,
            'chunks': int or dict or 'auto' or None,
            'combine': {"by_coords", "nested"},
            'combine_attrs': {"drop", "identical", "no_conflicts", "drop_conflicts", "override"} or callable()
            'compat': {"identical", "equals", "broadcast_equals", "no_conflicts", "override"},
            'concat_dim': str or DataArray or Index / Sequence of these or None,
            'coords': {"minimal", "different", "all"} or list of str,
            'data_vars': {"minimal", "different", "all"},
            'engine': {"netcdf4", "scipy", "pydap", "h5netcdf", "zarr", None},
            'join': {"outer", "inner", "left", "right", "exact", "override"},
            'parallel': bool,
            'preprocess': callable(),
            **other_kwargs
        }
        Default is None
    **kwargs - Discarded

    Output:
    -------
    :return: xarray.Dataset
        Newly created dataset. Note that:
            T, X, Y dimensions will be renamed time, longitude, latitude
            longitude are set from 0 to 360E
            latitude are set from -90 to 90N
    """
    kwargs_open_mfdataset = tools.none_to_default(kwargs_open_mfdataset, {})
    if tools.is_variables(variable) is True:
        kwargs_open_mfdataset["data_vars"] = copy__deepcopy(variable)
    # create dataset
    ds = xarray.open_mfdataset(filename, **kwargs_open_mfdataset)
    if variable is not None and isinstance(variable, list) is True and \
            all([isinstance(k, str) is True for k in variable]) is True:
        for k in list(ds.keys()):
            if k not in variable:
                del ds[k]
    # update time, lat, lon dimensions
    dict_dim = {"T": "time", "X": "longitude", "Y": "latitude"}
    new_dims = {}
    for k in ["T", "X", "Y"]:
        dim = cf_dim_to_dim(ds, k)
        if tools.is_dim(dim) is True and dim != dict_dim[k]:
            new_dims[dim] = dict_dim[k]
    if len(list(new_dims.keys())) > 0:
        ds_o = {}
        for k in list(ds.keys()):
            ds_o[k] = ds[k].rename(new_name_or_name_dict=new_dims)
        ds = dataset_wrapper(data_vars=ds_o, attrs=ds.attrs)
    # update longitude
    dim_lon = cf_dim_to_dim(ds, "X")
    if tools.is_dim(dim_lon) is True:
        # ensure that longitude ranges from 0 to 360E
        ds = roll_longitude(ds)
    # update latitude
    dim_lat = cf_dim_to_dim(ds, "Y")
    if tools.is_dim(dim_lat) is True and len(ds[dim_lat].shape) == 1:
        # ensure that latitude ranges from -90 to 90N
        ds = ds.sortby(dim_lat)
    # HadISST has -1000 values... -> mask them
    if "hadisst" in filename.lower():
        ds = ds.where(ds != -1000.)
    return ds


def recreate_array(
        arr: numpy__ndarray,
        da: array_wrapper,
        attrs_added: dict[str, str] = None,
        attrs_removed: list[str] = None,
        axis_added: Union[list[int], tuple[int], None] = None,
        coords_added: dict[Union[Hashable, str], Union[numpy__ndarray, array_wrapper]] = None,
        dim_added: Union[list[Hashable], list[str], tuple[Hashable], tuple[str], None] = None,
        dim_removed: Union[list[Hashable], list[str], tuple[Hashable], tuple[str], None] = None,
        **kwargs) -> array_wrapper:
    """
    Recreate output xarray.DataArray from input xarray.DataArray.

    Input:
    ------
    :param arr: numpy.ndarray
        Array derived from 'ds' (e.g., a statistic was computed) that was transformed into a numpy.ndarray in the
        process
    :param da: xarray.DataArray
        Original xarray.DataArray from which 'arr' is derived
    :param attrs_added: dict[str, str] or None, optional
        Variable attributes to add to the DataArray; e.g, attrs_added = {"attr_name": "new attribute"}.
        Default is None (no attribute added)
    :param attrs_removed: list[str] or None, optional
        Variable attributes to remove from the DataArray; e.g, attrs_removed = ["attr_name"].
        Default is None (no attribute removed)
    :param axis_added: list[int] or tuple[int] or None
        Position(s) of added dimension(s) (if any); e.g, axis_added = [0] or axis_added = [0, 1].
        If given, both axis_added and dim_added must be provided.
        Default is None (no dimension has been added)
    :param coords_added: dict[str, numpy.ndarray or xarray.DataArray] or None, optional
        Coordinates (tick labels) to use for indexing along each dimension.
        If dim_added is not in coords_added, coordinates will be a sequence of numbers.
        Default is None
    :param dim_added: list[Hashable] or list[str] or tuple[Hashable] or tuple[str] or None, optional
        Dimension name(s) that has been added from ds to arr (if any);
        e.g, dim_added = ["x"] or dim_added = ["x", "y"].
        If given, both axis_added and dim_added must be provided.
        Default is None (no dimension has been added)
    :param dim_removed: list[Hashable] or list[str] or tuple[Hashable] or tuple[str] or None, optional
        Dimension name(s) that has been removed from ds to arr (e.g., to compute a statistic);
        e.g., dim_removed = ["x"] or dim_removed = ["x", "y"].
        Default is None (no dimension was removed)

    Output:
    -------
    :return: xarray.DataArray
        Input arr wrapped in a xarray.DataArray.
    """
    attrs_removed = tools.none_to_default(attrs_removed, [])
    dim_removed = tools.none_to_default(dim_removed, [])
    # list dimensions
    dimensions = list(da.dims)
    # delete removed dimension(s)
    for k in dim_removed:
        if isinstance(k, str) is True and k in dimensions:
            dimensions.remove(k)
    # get coordinates corresponding to dimensions
    coordinates = dict((k, da[k]) for k in dimensions)
    if check_multidimensional_coordinates(da) is True:
        for k1 in ["X", "Y"]:
            dim = cf_dim_to_dim(da, k1)
            if tools.is_dim(dim):
                coordinates[dim] = da[dim]
                for k2 in list(da[dim].dims):
                    if k2 in list(coordinates.keys()):
                        del coordinates[k2]
    # add given dimension(s)
    if isinstance(axis_added, (list, tuple)) is True and isinstance(dim_added, (list, tuple)) is True and \
            len(axis_added) == len(dim_added):
        for k1, k2 in zip(axis_added, dim_added):
            # add given dimension at given position
            dimensions.insert(k1, k2)
            # add coordinates in dictionary
            if isinstance(coords_added, dict) is True and k2 in coords_added.keys():
                coordinates[k2] = coords_added[k2]
            else:
                coordinates[k2] = array_wrapper(list(range(arr.shape[k1])))
    # get input attributes
    attributes = da.attrs
    # remove attributes
    for k in attrs_removed:
        if k in list(attributes.keys()):
            del attributes[k]
    # add given attribute(s)
    if isinstance(attrs_added, dict) is True:
        attributes.update(attrs_added)
    attributes = dict((k, attributes[k]) for k in sorted(list(attributes.keys()), key=lambda v: v.lower()))
    # numpy.ndarray to xarray.DataArray
    return array_wrapper(attrs=attributes, coords=coordinates, data=arr, dims=dimensions)


def remove_unused_coordinates(ds: Union[array_wrapper, dataset_wrapper]) -> Union[array_wrapper, dataset_wrapper]:
    """
    Remove coordinates that are not used in input object.

    Input:
    ------
    :param ds: xarray.DataArray or xarray.Dataset

    Output:
    -------
    :return: xarray.DataArray or xarray.Dataset
        Object (as input) with unused coordinates removed
    """
    # dimensions in object
    dims_in_ds = list(ds.coords)
    # dimensions used in object
    dims_used = []
    if isinstance(ds, array_wrapper) is True:
        dims_used = list(ds.dims)
    else:
        # loop on each data_var of the dataset
        for data_var in list(ds):
            dims_used += list(ds[data_var].dims)
    # check multidimensional coordinates
    if check_multidimensional_coordinates(ds) is True:
        for k in ["X", "Y"]:
            dim = cf_dim_to_dim(ds, k)
            if tools.is_dim(dim) is True:
                dims_used.append(dim)
    # remove unused coordinates
    for k in list(set(dims_in_ds) - set(dims_used)):
        del ds[k]
    return ds


def roll_longitude(
        ds: Union[array_wrapper, dataset_wrapper],
        new_lon_min: Union[float, int, None] = None) -> Union[array_wrapper, dataset_wrapper]:
    dim_lon = cf_dim_to_dim(ds, "X")
    if tools.is_dim(dim_lon) is True:
        # update longitude
        if isinstance(new_lon_min, (float, int)) is True:
            # add minimum value to dataset's longitude to shift the dimension
            # e.g., initial longitude = [0; 360], new_lon_min = -70, new longitude = [-70; 290]
            ds = ds.assign_coords({dim_lon: ds[dim_lon] + new_lon_min})
        else:
            # ensure that longitude ranges from 0 to 360E
            ds = ds.assign_coords({dim_lon: (360 + (ds[dim_lon] % 360)) % 360})
        # roll so that the first longitude of the dimension is the minimum longitude
        try:
            # normal roll method
            ds = ds.roll({dim_lon: -ds[dim_lon].argmin().values}, roll_coords=True)
        except:
            # for multidimensional coordinates (e.g., curvilinear grids)
            # average lon along Y
            arr_lon = ds[dim_lon]
            lon_x = arr_lon.to_numpy().mean(axis=0)
            # find minimum value
            min_x = lon_x.argmin()
            # roll
            ds = ds.roll({arr_lon.dims[-1]: -min_x}, roll_coords=True)
    return ds


def set_dim_as_first(
        ds: Union[array_wrapper, dataset_wrapper],
        dim: Union[Hashable, str],
        **kwargs) -> Union[array_wrapper, dataset_wrapper, None]:
    """
    Return a new object (as input) with all array dimensions transposed.
    https://docs.xarray.dev/en/stable/generated/xarray.Dataset.transpose.html
    https://docs.xarray.dev/en/stable/generated/xarray.DataArray.transpose.html

    Input:
    ------
    :param ds: xarray.DataArray or xarray.Dataset
    :param dim: Hashable or str
        Dimension name to transpose to the first position
    **kwargs - Discarded

    Output:
    -------
    :return: xarray.DataArray or xarray.Dataset
        Object (as input) transposed dimensions.
    """
    # get dimension name
    dim_name = check_dim(ds, dim)
    if dim_name is not None:
        if (isinstance(ds, dataset_wrapper) is True and len(list(ds.coords)) == 1) or (
                isinstance(ds, array_wrapper) is True and (list(ds.dims)[0] == dim_name or len(list(ds.dims)) == 1)):
            return ds
        else:
            # set dim as the first dimension of ds
            return ds.transpose(dim_name, "...")
    else:
        return None


def weights_time(ds: Union[array_wrapper, dataset_wrapper], **kwargs) -> Union[array_wrapper, None]:
    """
    Compute the number of days per months at each time steps (can be used to average time steps)

    Input:
    ------
    :param ds: xarray.DataArray or xarray.Dataset
    **kwargs - Discarded

    Output:
    -------
    :return: xarray.DataArray
        New object (DataArray), shape of input time dimension, with the number of days per months at each time steps
    """
    ds_o = None
    # get time dimension
    dim_time = cf_dim_to_dim(ds, "T")
    if tools.is_dim(dim_time) is True:
        # get time array, index and calendar
        time_arr = ds[dim_time]
        time_index = time_arr.to_index()
        calendar = time_arr.dt.calendar
        # get number of day per time steps
        ds_o = tt.get_days_per_month(time_index, calendar=calendar)
        # to data array
        ds_o = array_wrapper(ds_o, coords=[time_arr], name="month_length")
    return ds_o
# ---------------------------------------------------------------------------------------------------------------------#
