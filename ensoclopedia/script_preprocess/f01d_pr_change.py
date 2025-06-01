# -*- coding:UTF-8 -*-
# ---------------------------------------------------------------------------------------------------------------------#
# Compute precipitation change related to ENSO during JJA preceding ENSO
# ---------------------------------------------------------------------------------------------------------------------#


# ---------------------------------------------------#
# Import packages
# ---------------------------------------------------#
# basic python package
from copy import deepcopy as copy__deepcopy
from json import dumps as json__dumps

# local functions
from ensoclopedia.wrapper.dataarray_tools import linear_regression
from ensoclopedia.wrapper.processors import dataset_wrapper, netcdf_reader, netcdf_writer, processor
from ensoclopedia.wrapper.tools import merge_dict, none_to_default_dict
from ensoclopedia.wrapper.xarray_tools import get_time_bounds
# ---------------------------------------------------#


# ---------------------------------------------------------------------------------------------------------------------#
# Default arguments
# ---------------------------------------------------------------------------------------------------------------------#
defaults = {
    # input data
    "var1_data": {
        "bounds": {"T": ("1980-01-01", "2024-12-31"), "X": (190., 240.), "Y": (-5., 5.)}, # nino3.4 5S-5N, 120-170W
        "ensure_constant_mask": True,
        "dataset": "HadISST",
        "filename": "data_input/HadISST_sst.nc",
        "kwargs_netcdf_open": {},  # can contain kwargs_open_mfdataset to pass instructions to xarray open_mfdataset
        "kwargs_netcdf_selector": {},  # can contain keywords for relevant functions used by netcdf_selector
        "remove_regional_mean": {
            "bounds": {"X": (0., 360.), "Y": (-20., 20.)},
            "kwargs_mean_weighted": {"skipna": True, "weights": True},
            "kwargs_netcdf_selector": {},  # can contain keywords for relevant functions used by netcdf_selector
            "region": "tropics",
        },
        "variable": ["sst"],
    },
    "var2_data": {
        "bounds": {"T": ("1980-01-01", "2024-12-31"), "X": (0., 360.), "Y": (-90., 90.)}, # global
        "ensure_constant_mask": True,
        "dataset": "GPCPv2.3",
        "filename": "data_input/precip.mon.mean.nc",
        "kwargs_netcdf_open": {},  # can contain kwargs_open_mfdataset to pass instructions to xarray open_mfdataset
        "kwargs_netcdf_selector": {},  # can contain keywords for relevant functions used by netcdf_selector
        "remove_regional_mean": {},
        "variable": ["precip"],
    },
    # process
    "var1_preprocess": {
        "1--interannual_anomalies": {},
        "2--normalize": {},
        "3--season_mean": {"season": "NDJ"},
        "4--average": {"dim": ("X", "Y"), "kwargs_mean_weighted": {"skipna": True, "weights": True}},
    },
    "var2_preprocess": {
        "1--interannual_anomalies": {},
        "2--detrend": {"deg": 1},
        "3--season_mean": {"season": "JJA"},
    },
    "var3_preprocess": {
        "1--season_mean": {"season": "JJA"},
        "2--average": {"dim": "year", "kwargs_mean_weighted": {"skipna": True, "weights": False}},
    },
    # output data
    "output": {
        "filename": "data_output/figure_01d.nc",
        "kwargs_to_netcdf": {},
        "variable": {
            "slope": {
                "name": "f01d--map_c",
                "attributes": {
                    "short_name": "slope",
                    "units": "%",
                    "map_c_nam": "JJA PR change regressed on normalized NDJ N3.4 rSSTA (UNITS)",
                },
            },
        },
    },
}
# ---------------------------------------------------------------------------------------------------------------------#


# ---------------------------------------------------------------------------------------------------------------------#
# Main
# ---------------------------------------------------------------------------------------------------------------------#
def f01d_pr_change_process(
        output: dict = None,
        var1_data: dict = None,
        var1_preprocess: dict = None,
        var2_data: dict = None,
        var2_preprocess: dict = None,
        var3_preprocess: dict = None,
        **kwargs):
    #
    # -- Set to default
    #
    output = none_to_default_dict(output, "output", defaults)
    var1_data = none_to_default_dict(var1_data, "var1_data", defaults)
    var1_preprocess = none_to_default_dict(var1_preprocess, "var1_preprocess", defaults)
    var2_data = none_to_default_dict(var2_data, "var2_data", defaults)
    var2_preprocess = none_to_default_dict(var2_preprocess, "var2_preprocess", defaults)
    var3_preprocess = none_to_default_dict(var3_preprocess, "var3_preprocess", defaults)
    #
    # -- Read data
    #
    variable_x = None
    if isinstance(var1_data, dict) is True and "variable" in list(var1_data):
        variable_x = copy__deepcopy(var1_data["variable"])
    ds_x0 = netcdf_reader(**var1_data)
    # print("after netcdf_reader ds_x0")
    # print(json__dumps(ds_x0.attrs, indent=4))
    # print(list(ds_x0.keys()))
    # for k in list(ds_x0.keys()):
    #     print(str(k).rjust(10), ds_x0[k].shape)
    #     print(json__dumps(ds_x0[k].attrs, indent=4))
    variable_y = None
    if isinstance(var2_data, dict) is True and "variable" in list(var2_data):
        variable_y = copy__deepcopy(var2_data["variable"])
    ds_y0 = netcdf_reader(**var2_data)
    for k1 in list(ds_y0.keys()):
        for k2 in list(ds_y0[k1].attrs):
            if k2 in ["actual_range", "add_offset", "precision", "scale_factor", "valid_range"]:
                del ds_y0[k1].attrs[k2]
    # print("after netcdf_reader ds_y0")
    # print(json__dumps(ds_y0.attrs, indent=4))
    # print(list(ds_y0.keys()))
    # for k in list(ds_y0.keys()):
    #     print(str(k).rjust(10), ds_y0[k].shape, ds_y0[k].dims)
    #     print(json__dumps(ds_y0[k].attrs, indent=4))
    # for k1 in list(ds_y0.coords):
    #     print(str(k1).rjust(10), ds_y0[k1].shape)
    #     print(str(k1).rjust(10), ds_y0[k1].values[:10])
    #     for k2 in list(ds_y0[k1].attrs):
    #         print(str(k2).rjust(20), ds_y0[k1].attrs[k2])
    # stop
    #
    # -- Process
    #
    # perform processing steps for ds_x
    ds_x = processor(ds_x0, var1_preprocess, variable=variable_x)
    # print("after processor ds_x")
    # print(json__dumps(ds_x.attrs, indent=4))
    # print(list(ds_x.keys()))
    # for k in list(ds_x.keys()):
    #     print(str(k).rjust(10), ds_x[k].shape)
    #     print(ds_x[k]["year"])
    #     print(json__dumps(ds_x[k].attrs, indent=4))
    # perform processing steps for ds_y
    ds_y1 = processor(ds_y0, var2_preprocess, variable=variable_y)
    ds_y2 = processor(ds_y0, var3_preprocess, variable=variable_y)
    # print("after processor ds_y1")
    # print(json__dumps(ds_y1.attrs, indent=4))
    # print(list(ds_y1.keys()))
    # for k in list(ds_y1.keys()):
    #     print(str(k).rjust(10), ds_y1[k].shape)
    #     print(ds_y1[k]["year"])
    #     print(json__dumps(ds_y1[k].attrs, indent=4))
    # for k1 in list(ds_y1.coords):
    #     print(str(k1).rjust(10), ds_y1[k1].shape)
    #     print(str(k1).rjust(10), ds_y1[k1].values[:10])
    #     for k2 in list(ds_y1[k1].attrs):
    #         print(str(k2).rjust(20), ds_y1[k1].attrs[k2])
    # stop
    # print("after processor ds_y2")
    # print(json__dumps(ds_y2.attrs, indent=4))
    # print(list(ds_y2.keys()))
    # for k in list(ds_y2.keys()):
    #     print(str(k).rjust(10), ds_y2[k].shape)
    #     print(ds_y2[k]["year"])
    #     print(json__dumps(ds_y2[k].attrs, indent=4))
    # for k1 in list(ds_y2.coords):
    #     print(str(k1).rjust(10), ds_y2[k1].shape)
    #     for k2 in list(ds_y2[k1].attrs):
    #         print(str(k2).rjust(20), ds_y2[k1].attrs[k2])
    ds_y = ds_y1 * 100 / ds_y2
    # print("after processor ds_y")
    # print(json__dumps(ds_y.attrs, indent=4))
    # print(list(ds_y.keys()))
    # for k in list(ds_y.keys()):
    #     print(str(k).rjust(10), ds_y[k].shape)
    #     print(ds_y[k]["year"])
    #     print(json__dumps(ds_y[k].attrs, indent=4))
    # for k1 in list(ds_y.coords):
    #     print(str(k1).rjust(10), ds_y[k1].shape)
    #     print(str(k1).rjust(10), ds_y[k1].values[:10])
    #     for k2 in list(ds_y[k1].attrs):
    #         print(str(k2).rjust(20), ds_y[k1].attrs[k2])
    # stop
    #
    # -- Diagnostic
    #
    # regress ds_y onto ds_x
    var_x, var_y = variable_x[0], variable_y[0]
    ds_reg = linear_regression(ds_x[var_x], ds_y[var_y], dim="year")
    # print("after linear_regression ds_reg")
    # print(json__dumps(ds_reg.attrs, indent=4))
    # print(list(ds_reg.keys()))
    # for k in list(ds_reg.keys()):
    #     print(str(k).rjust(10), ds_reg[k].shape)
    #     print(str(k).rjust(10), ds_reg[k].dims)
    #     print(json__dumps(ds_reg[k].attrs, indent=4))
    # for k1 in list(ds_reg.coords):
    #     print(str(k1).rjust(10), ds_reg[k1].shape)
    #     for k2 in list(ds_reg[k1].attrs):
    #         print(str(k2).rjust(20), ds_reg[k1].attrs[k2])
    # stop
    #
    # -- Save in netCDF
    #
    # select output variables
    ds_o = {}
    for var in list(output["variable"].keys()):
        # output array
        da = ds_reg[var]
        # remove unused coordinates
        for k in list(set(list(da.coords.keys())) - set(da.dims)):
            del da[k]
        # variable attributes
        att_v = copy__deepcopy(output["variable"][var]["attributes"])
        att_v["epoch"] = ""
        for k in get_time_bounds(ds_x0):
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
        print(json__dumps(da.attrs, indent=4))
        ds_o[output["variable"][var]["name"]] = da
    # global attributes
    att_g = merge_dict(ds_x0.attrs, ds_y.attrs, var1_data["dataset"], var2_data["dataset"])
    for k in list(att_g):
        if k.lower() in ["comment", "conventions", "history", "licence", "supplementary_information"]:
            del att_g[k]
    # save dataset
    ds_o = dataset_wrapper(data_vars=ds_o, attrs=att_g)
    filename = output["filename"]
    kwargs_to_netcdf = {}
    if "kwargs_to_netcdf" in list(output) and isinstance(output["kwargs_to_netcdf"], dict) is True:
        kwargs_to_netcdf = output["kwargs_to_netcdf"]
    netcdf_writer(ds_o, filename, **kwargs_to_netcdf)
# ---------------------------------------------------------------------------------------------------------------------#
