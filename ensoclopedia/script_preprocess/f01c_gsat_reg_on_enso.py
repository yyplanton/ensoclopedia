# -*- coding:UTF-8 -*-
# ---------------------------------------------------------------------------------------------------------------------#
# Compute ENSO influence on GSAT
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
        "bounds": {"T": ("1980-01-01", "2024-12-31")},
        "ensure_constant_mask": True,
        "dataset": "HadCRUT.5",
        "filename": "data_input/HadCRUT.5.0.2.0.analysis.summary_series.global.monthly.nc",
        "kwargs_netcdf_open": {},  # can contain kwargs_open_mfdataset to pass instructions to xarray open_mfdataset
        "kwargs_netcdf_selector": {},  # can contain keywords for relevant functions used by netcdf_selector
        "variable": ["tas_mean"],
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
        "3--reshape_lead_lag": {"window": 48},
    },
    # output data
    "output": {
        "filename": "data_output/figure_01c.nc",
        "kwargs_to_netcdf": {},
        "variable": {
            "slope": {
                "name": "f01c--cur_y",
                "attributes": {
                    "short_name": "slope",
                    "units": "degC",
                    "x_nam": "month",
                    "y_nam": "GSAT regressed on normalized N3.4 rSSTA (UNITS)",
                },
            },
        },
    },
}
# ---------------------------------------------------------------------------------------------------------------------#


# ---------------------------------------------------------------------------------------------------------------------#
# Main
# ---------------------------------------------------------------------------------------------------------------------#
def f01c_gsat_reg_on_enso_process(
        output: dict = None,
        var1_data: dict = None,
        var1_preprocess: dict = None,
        var2_data: dict = None,
        var2_preprocess: dict = None,
        **kwargs):
    #
    # -- Set to default
    #
    output = none_to_default_dict(output, "output", defaults)
    var1_data = none_to_default_dict(var1_data, "var1_data", defaults)
    var1_preprocess = none_to_default_dict(var1_preprocess, "var1_preprocess", defaults)
    var2_data = none_to_default_dict(var2_data, "var2_data", defaults)
    var2_preprocess = none_to_default_dict(var2_preprocess, "var2_preprocess", defaults)
    #
    # -- Read data
    #
    variable_x = None
    if isinstance(var1_data, dict) is True and "variable" in list(var1_data):
        variable_x = copy__deepcopy(var1_data["variable"])
    ds_x0 = netcdf_reader(**var1_data)
    variable_y = None
    if isinstance(var2_data, dict) is True and "variable" in list(var2_data):
        variable_y = copy__deepcopy(var2_data["variable"])
    ds_y = netcdf_reader(**var2_data)
    #
    # -- Process
    #
    # perform processing steps for ds_x
    ds_x = processor(ds_x0, var1_preprocess, variable=variable_x)
    # print("after processor ds_x")
    # print(json__dumps(ds_x.attrs, indent=4))
    # print(list(ds_x.keys()))
    # for k in list(ds_x.keys()):
    #     print(str(k).rjust(10), ds_x[k].shape, float(ds_x[k].min()), float(ds_x[k].max()))
    #     # print(ds_x[k]["year"])
    #     print(json__dumps(ds_x[k].attrs, indent=4))
    # stop
    # perform processing steps for ds_y
    ds_y = processor(ds_y, var2_preprocess, variable=variable_y)
    # print("after processor ds_y")
    # print(json__dumps(ds_y.attrs, indent=4))
    # print(list(ds_y.keys()))
    # for k in list(ds_y.keys()):
    #     print(str(k).rjust(10), ds_y[k].shape, float(ds_y[k].min()), float(ds_y[k].max()))
    #     # print(ds_y[k]["year"])
    #     print(json__dumps(ds_y[k].attrs, indent=4))
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
    #     print(str(k).rjust(10), ds_reg[k]["month"])
    #     print(json__dumps(ds_reg[k].attrs, indent=4))
    #
    # -- Save in netCDF
    #
    # select output variables
    ds_o = {}
    for var in output["variable"]:
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
