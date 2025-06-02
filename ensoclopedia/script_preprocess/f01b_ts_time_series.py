# -*- coding:UTF-8 -*-
# ---------------------------------------------------------------------------------------------------------------------#
# Compute GSAT time series
# ---------------------------------------------------------------------------------------------------------------------#


# ---------------------------------------------------#
# Import packages
# ---------------------------------------------------#
# basic python package
from copy import deepcopy as copy__deepcopy

# local functions
from ensoclopedia.wrapper.tools import none_to_default_dict
from ensoclopedia.wrapper.processors import dataset_wrapper, netcdf_reader, netcdf_writer, processor
from ensoclopedia.wrapper.xarray_tools import get_time_bounds
# ---------------------------------------------------#


# ---------------------------------------------------------------------------------------------------------------------#
# Default arguments
# ---------------------------------------------------------------------------------------------------------------------#
defaults = {
    # input data
    "var1_data": {
        "bounds": {"T": ("1850-01-01", "2024-12-31")},
        "dataset": "HadCRUT.5",
        "filename": "data_input/HadCRUT.5.0.2.0.analysis.summary_series.global.monthly.nc",
        "kwargs_netcdf_open": {},  # can contain kwargs_open_mfdataset to pass instructions to xarray open_mfdataset
        "kwargs_netcdf_selector": {},  # can contain keywords for relevant functions used by netcdf_selector
        "remove_regional_mean": {},
        "variable": ["tas_mean", "tas_lower", "tas_upper"],
    },
    # process
    "var1_preprocess": {
        "1--average_moving": {"dim": "T", "window": 12},
    },
    # output data
    "output": {
        "filename": "data_output/figure_01b.nc",
        "kwargs_to_netcdf": {},
        "variable": {
            "tas_mean": {
                "name": "f01b--cur_y",
                "attributes": {
                    "short_name": "mean",
                    "units": "degC",
                    "x_nam": "time",
                    "y_nam": "GSAT relative to 1961-1990 (UNITS)",
                },
            },
            "tas_lower": {
                "name": "f01b--sha_y1",
                "attributes": {
                    "short_name": "2.5",
                    "units": "degC",
                    "x_nam": "time",
                    "y_nam": "GSAT relative to 1961-1990 (UNITS)",
                },
            },
            "tas_upper": {
                "name": "f01b--sha_y2",
                "attributes": {
                    "short_name": "97.5",
                    "units": "degC",
                    "x_nam": "time",
                    "y_nam": "GSAT relative to 1961-1990 (UNITS)",
                },
            },
        },
    },
}
# ---------------------------------------------------------------------------------------------------------------------#


# ---------------------------------------------------------------------------------------------------------------------#
# Main
# ---------------------------------------------------------------------------------------------------------------------#
def f01b_ts_time_series_process(
        output: dict = None,
        var1_data: dict = None,
        var1_preprocess: dict = None,
        **kwargs):
    #
    # -- Set to default
    #
    output = none_to_default_dict(output, "output", defaults)
    var1_data = none_to_default_dict(var1_data, "var1_data", defaults)
    var1_preprocess = none_to_default_dict(var1_preprocess, "var1_preprocess", defaults)
    #
    # -- Read data
    #
    variable = None
    if isinstance(var1_data, dict) is True and "variable" in list(var1_data):
        variable = copy__deepcopy(var1_data["variable"])
    ds = netcdf_reader(**var1_data)
    #
    # -- Process
    #
    # perform processing steps
    ds = processor(ds, var1_preprocess, variable=variable)
    #
    # -- Diagnostic
    #
    #
    # -- Save in netCDF
    #
    # select output variables
    ds_o = {}
    for var in output["variable"]:
        # output array
        da = ds[var]
        # remove unused coordinates
        for k in list(set(list(da.coords.keys())) - set(da.dims)):
            del da[k]
        # variable attributes
        att_v = dict((k1, k2) for k1, k2 in da.attrs.items() if k1 in ["long_name"])
        att_v.update(**output["variable"][var]["attributes"])
        att_v["epoch"] = ""
        for k in get_time_bounds(ds):
            if att_v["epoch"] != "":
                att_v["epoch"] += " to "
            att_v["epoch"] += "-".join(k.split("-")[:2])
        # update attributes
        if "units" in list(att_v.keys()):
            for k1, k2 in att_v.items():
                att_v[k1] = k2.replace(" (UNITS)", " (" + str(att_v["units"]) + ")").replace(" ()", "")
        att_v = dict(sorted(att_v.items()))
        # remove attributes
        for k in list(da.attrs.keys()):
            del da.attrs[k]
        # update attributes
        da.attrs.update(**att_v)
        # rename variable
        da = da.rename(output["variable"][var]["name"])
        ds_o[output["variable"][var]["name"]] = da
    # global attributes
    att_g = {}
    for k1, k2 in ds.attrs.items():
        if k1 not in ["Conventions", "history"]:
            att_g[k1] = copy__deepcopy(k2)
    # save dataset
    ds_o = dataset_wrapper(data_vars=ds_o, attrs=att_g)
    filename = output["filename"]
    kwargs_to_netcdf = {}
    if "kwargs_to_netcdf" in list(output) and isinstance(output["kwargs_to_netcdf"], dict) is True:
        kwargs_to_netcdf = output["kwargs_to_netcdf"]
    netcdf_writer(ds_o, filename, **kwargs_to_netcdf)
# ---------------------------------------------------------------------------------------------------------------------#
