# -*- coding:UTF-8 -*-
# ---------------------------------------------------------------------------------------------------------------------#
# Compute EOFs of sea surface temperature
# ---------------------------------------------------------------------------------------------------------------------#


# ---------------------------------------------------#
# Import packages
# ---------------------------------------------------#
# basic python package
from copy import deepcopy as copy__deepcopy
from json import dumps as json__dumps

# local functions
from ensoclopedia.wrapper.tools import none_to_default_dict
from ensoclopedia.wrapper.processors import dataset_wrapper, netcdf_reader, netcdf_writer, processor
from ensoclopedia.wrapper.xarray_tools import get_time_bounds
from ensoclopedia.wrapper.xeofs_base import eofs
# ---------------------------------------------------#


# ---------------------------------------------------------------------------------------------------------------------#
# Default arguments
# ---------------------------------------------------------------------------------------------------------------------#
defaults = {
    # input data
    "var1_data": {
        "bounds": {"T": ("1980-01-01", "2024-12-31"), "X": (0., 360.), "Y": (-90., 90.)}, # global
        "ensure_constant_mask": True,
        "dataset": "HadISST",
        "filename": "data_input/HadISST_sst.nc",
        "kwargs_netcdf_open": {},  # can contain kwargs_open_mfdataset to pass instructions to xarray open_mfdataset
        "kwargs_netcdf_selector": {},  # can contain keywords for relevant functions used by netcdf_selector
        "remove_regional_mean": {},
        "variable": ["sst"],
    },
    # process
    "var1_preprocess": {
        "1--interannual_anomalies": {},
        "2--detrend": {"deg": 1},
    },
    # diagnostic
    "kwargs_eof": {"dim": "T", "kwargs_xeofs": {"n_modes": 5, "use_coslat": True}},
    # output data
    "output": {
        "filename": "data_output/figure_01a.nc",
        "kwargs_to_netcdf": {},
        "variable": {
            "sst": {
                "name": "f01a--map_c",
                "attributes": {
                    "short_name": "EOF1 SSTA",
                    "units": "",
                    "map_c_nam": "first principal pattern from an EOF analysis on SSTA (UNITS)",
                },
            },
        },
    },
}
# ---------------------------------------------------------------------------------------------------------------------#


# ---------------------------------------------------------------------------------------------------------------------#
# Main
# ---------------------------------------------------------------------------------------------------------------------#
def f01a_sst_eof_process(
        output: dict = None,
        var1_data: dict = None,
        var1_preprocess: dict = None,
        kwargs_eof: dict = None,
        **kwargs):
    #
    # -- Set to default
    #
    kwargs_eof = none_to_default_dict(kwargs_eof, "kwargs_eof", defaults)
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
    # compute eof
    ds_eof = eofs(ds, **kwargs_eof)
    # print("after eofs ds_eof")
    # print(json__dumps(ds_eof.attrs, indent=4))
    # print(list(ds_eof.keys()))
    # for k in list(ds_eof.keys()):
    #     print(str(k).rjust(10), ds_eof[k].shape)
    #     print(json__dumps(ds_eof[k].attrs, indent=4))
    # for k1 in list(ds_eof.coords):
    #     print(str(k1).rjust(10), ds_eof[k1].shape)
    #     for k2 in list(ds_eof[k1].attrs):
    #         print(str(k2).rjust(20), ds_eof[k1].attrs[k2])
    #
    # -- Save in netCDF
    #
    # select output variables
    ds_o = {}
    for var in list(output["variable"].keys()):
        # output array
        da = ds_eof[var]
        # select first EOF
        da = da[0].squeeze(drop=True)
        # remove unused coordinates
        for k in list(set(list(da.coords.keys())) - set(da.dims)):
            del da[k]
        # variable attributes
        att_v = copy__deepcopy(output["variable"][var]["attributes"])
        att_v["epoch"] = ""
        for k in get_time_bounds(ds):
            if att_v["epoch"] != "":
                att_v["epoch"] += " to "
            att_v["epoch"] += "-".join(k.split("-")[:2])
        if "explained_variance" in list(da.attrs.keys()):
            att_v["explained_variance"] = copy__deepcopy(da.attrs["explained_variance"])
        # update attributes
        if "units" in list(att_v.keys()):
            for k1, k2 in att_v.items():
                if isinstance(k2, str) is True:
                    att_v[k1] = k2.replace(" (UNITS)", " (" + str(att_v["units"]) + ")")
                    att_v[k1] = att_v[k1].replace(" ()", "")
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
    for k1, k2 in ds_eof.attrs.items():
        if k1.lower() not in ["comment", "conventions", "history", "supplementary_information"]:
            att_g[k1.lower()] = copy__deepcopy(k2)
    att_g = dict(sorted(att_g.items()))
    # save dataset
    ds_o = dataset_wrapper(data_vars=ds_o, attrs=att_g)
    filename = output["filename"]
    kwargs_to_netcdf = {}
    if "kwargs_to_netcdf" in list(output) and isinstance(output["kwargs_to_netcdf"], dict) is True:
        kwargs_to_netcdf = output["kwargs_to_netcdf"]
    netcdf_writer(ds_o, filename, **kwargs_to_netcdf)
# ---------------------------------------------------------------------------------------------------------------------#
