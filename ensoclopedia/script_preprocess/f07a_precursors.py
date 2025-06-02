# -*- coding:UTF-8 -*-
# ---------------------------------------------------------------------------------------------------------------------#
# Oceanic precursors of ENSO (lead-lag correlations)
# ---------------------------------------------------------------------------------------------------------------------#


# ---------------------------------------------------#
# Import packages
# ---------------------------------------------------#
# basic python package
from copy import deepcopy as copy__deepcopy

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
        "dataset": "ORAS5",
        "filename": "data_input/sossheig_control_monthly_highres_2D_*_v0.1.nc",
        "kwargs_netcdf_open": {},  # can contain kwargs_open_mfdataset to pass instructions to xarray open_mfdataset
        "kwargs_netcdf_selector": {},  # can contain keywords for relevant functions used by netcdf_selector
        "remove_regional_mean": {
            "bounds": {"X": (0., 360.), "Y": (-20., 20.)},
            "kwargs_mean_weighted": {"skipna": True, "weights": True},
            "kwargs_netcdf_selector": {},  # can contain keywords for relevant functions used by netcdf_selector
            "region": "tropics",
        },
        "variable": ["sossheig"],
    },
    # process
    "var1_preprocess": {
        "1--interannual_anomalies": {},
        "2--normalize": {},
        "3--season_mean": {"season": "NDJ"},
        "4--average": {"dim": ("X", "Y"), "kwargs_mean_weighted": {"skipna": True, "weights": True}},
    },
    "var2_preprocess": {
        "1--netcdf_selector": {"bounds": {"X": (120., 280.), "Y": (-5., 5.)}},  # equatorial Pacific
        "2--interannual_anomalies": {},
        "3--reshape_lead_lag": {"window": 48},
    },
    "var3_preprocess": {
        "n34e": {
            "1--netcdf_selector": {"bounds": {"X": (190., 240.), "Y": (-5., 5.)}},  # nino3.4 5S-5N, 120-170W
            "2--average": {"dim": ("X", "Y"), "kwargs_mean_weighted": {"skipna": True, "weights": True}},
        },
        "pequ": {
            "1--netcdf_selector": {"bounds": {"X": (120., 280.), "Y": (-5., 5.)}},  # equatorial Pacific
            "2--average": {"dim": ("X", "Y"), "kwargs_mean_weighted": {"skipna": True, "weights": True}},
        },
        "peqw": {
            "1--netcdf_selector": {"bounds": {"X": (120., 205.), "Y": (-5., 5.)}},  # western equatorial Pacific
            "2--average": {"dim": ("X", "Y"), "kwargs_mean_weighted": {"skipna": True, "weights": True}},
        },
    },
    # output data
    "output": {
        "filename": "data_output/figure_07a.nc",
        "kwargs_to_netcdf": {},
        "variable": {
            "sst--sossheig_n34e": {
                "name": "sossheig_n34e--cur_y",
                "attributes": {
                    "short_name": "N3.4 rSSHA",
                    "units": "",
                    "x_nam": "month",
                    "y_nam": "N3.4 rSSHA correlated with on normalized N3.4 rSSTA (UNITS)",
                },
                "variable": "rvalue",
            },
            "sst--sossheig_pequ": {
                "name": "sossheig_pequ--cur_y",
                "attributes": {
                    "short_name": "EP rSSHA",
                    "units": "",
                    "x_nam": "month",
                    "y_nam": "EP rSSHA correlated with on normalized N3.4 rSSTA (UNITS)",
                },
                "variable": "rvalue",
            },
            "sst--sossheig_peqw": {
                "name": "sossheig_peqw--cur_y",
                "attributes": {
                    "short_name": "WEP rSSHA",
                    "units": "",
                    "x_nam": "month",
                    "y_nam": "WEP rSSHA correlated with on normalized N3.4 rSSTA (UNITS)",
                },
                "variable": "rvalue",
            },
        },
    },
}
# ---------------------------------------------------------------------------------------------------------------------#


# ---------------------------------------------------------------------------------------------------------------------#
# Main
# ---------------------------------------------------------------------------------------------------------------------#
def f07a_precursors_process(
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
    variable_y = None
    if isinstance(var2_data, dict) is True and "variable" in list(var2_data):
        variable_y = copy__deepcopy(var2_data["variable"])
    ds_y0 = netcdf_reader(**var2_data)
    for k1 in list(ds_y0.keys()):
        for k2 in list(ds_y0[k1].attrs):
            if k2 in ["_FillValue", "interval_operation", "interval_write", "missing_value"]:
                del ds_y0[k1].attrs[k2]
    #
    # -- Process
    #
    # perform processing steps for ds_x
    ds_x = processor(ds_x0, var1_preprocess, variable=variable_x)
    # perform processing steps for ds_y
    ds_y1 = processor(ds_y0, var2_preprocess, variable=variable_y)
    ds_y = {}
    for reg in list(var3_preprocess.keys()):
        # process region
        ds_yt = processor(ds_y1, var3_preprocess[reg], variable=variable_y)
        # save in dict
        for var in list(ds_yt.keys()):
            ds_y[str(var) + "_" + str(reg)] = ds_yt[var]
    ds_y = dataset_wrapper(data_vars=ds_y, attrs=ds_y0.attrs)
    #
    # -- Diagnostic
    #
    # regress ds_y onto ds_x
    ds_reg = {}
    for var_x in list(ds_x.keys()):
        for var_y in list(ds_y.keys()):
            ds_reg[str(var_x) + "--" + str(var_y)] = linear_regression(ds_x[var_x], ds_y[var_y], dim="year")
    #
    # -- Save in netCDF
    #
    # select output variables
    ds_o = {}
    for var in list(output["variable"].keys()):
        # output array
        da = ds_reg[var]
        if isinstance(da, dataset_wrapper) is True and "variable" in list(output["variable"][var].keys()):
            da = da[output["variable"][var]["variable"]]
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
    att_g = merge_dict(ds_x0.attrs, ds_y0.attrs, var1_data["dataset"], var2_data["dataset"])
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
