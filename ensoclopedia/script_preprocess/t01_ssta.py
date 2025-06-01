# -*- coding:UTF-8 -*-
# ---------------------------------------------------------------------------------------------------------------------#
# Compute surface temperature time series
# ---------------------------------------------------------------------------------------------------------------------#


# ---------------------------------------------------#
# Import packages
# ---------------------------------------------------#
# basic python package
from copy import deepcopy as copy__deepcopy
from json import dumps as json__dumps
from typing import Union

# local functions
from ensoclopedia.wrapper.tools import none_to_default_dict
from ensoclopedia.wrapper.processors import dataset_wrapper, detrend, average, interannual_anomalies, netcdf_reader, \
    netcdf_writer, season_mean
from ensoclopedia.wrapper.xarray_tools import get_time_bounds, remove_unused_coordinates
# ---------------------------------------------------#


# ---------------------------------------------------------------------------------------------------------------------#
# Default arguments
# ---------------------------------------------------------------------------------------------------------------------#
defaults = {
    # input data
    "filename1_input": "data_input/HadISST_sst.nc",
    "variable1_input": ["sst"],
    "bounds1": {"T": ("1925-01-01", "2024-12-31"), "X": (190., 240.), "Y": (-5., 5.)}, # nino3.4 5S-5N, 120-170W
    "bounds2": {"T": ("1925-01-01", "2024-12-31"), "X": (0., 360.), "Y": (-20., 20.)},  # tropic 20S-20N, 0-360E
    # process
    "kwargs1_anom": {},
    "kwargs1_detrend": {"deg": 1},
    "kwargs1_average": {"kwargs_mean": {"dim": ("X", "Y"), "skipna": True}},
    # output data
    "filename_output": "data_output/HadISST_n34_ssta_1925_2024.nc",
    "kwargs_to_netcdf": {},
    "variable_output": {
        "ds_1": {
            "sst": {
                "name": "rssta",
                "attributes": {
                    "method": "SST: 1) Tropic [20S-20N ; 0-360E] average removed;; 2) seasonal cycle removed;; 3) " +
                              "Nino3.4 [5S-5N ; 120-170W] average computed",
                    "long_name": "Relative Sea Surface Temperature Anomalies Averaged in Nino3.4",
                    "short_name": "N3.4 rSSTA",
                    "standard_name": "relative_sea_surface_temperature_anomalies_averaged_in_nino3.4",
                    "units": "degC",
                },
            },
        },
        "ds_2": {
            "sst": {
                "name": "ssta",
                "attributes": {
                    "method": "SST: 1) seasonal cycle removed;; 2) Nino3.4 [5S-5N ; 120-170W] average computed",
                    "long_name": "Sea Surface Temperature Anomalies Averaged in Nino3.4",
                    "short_name": "N3.4 SSTA",
                    "standard_name": "sea_surface_temperature_anomalies_averaged_in_nino3.4",
                    "units": "degC",
                },
            },
        },
        "ds_3": {
            "sst": {
                "name": "ssta_det",
                "attributes": {
                    "method": "SST: 1) seasonal cycle removed;; 2) time series linearly detrended;; 3) Nino3.4 " +
                              "[5S-5N ; 120-170W] average computed",
                    "long_name": "Detrended Sea Surface Temperature Anomalies Averaged in Nino3.4",
                    "short_name": "det N3.4 SSTA",
                    "standard_name": "detrended_sea_surface_temperature_anomalies_averaged_in_nino3.4",
                    "units": "degC",
                },
            },
        },
    },
}
# ---------------------------------------------------------------------------------------------------------------------#


# ---------------------------------------------------------------------------------------------------------------------#
# Main
# ---------------------------------------------------------------------------------------------------------------------#
def t01_ssta_process(
        bounds1: dict = None,
        bounds2: dict = None,
        ensure_constant_mask: bool = None,
        filename1_input: str = None,
        filename_output: str = None,
        kwargs1_anom: dict = None,
        kwargs1_average: dict = None,
        kwargs1_detrend: dict = None,
        kwargs_to_netcdf: dict = None,
        variable1_input: str = None,
        variable_output: dict[str, dict[str, Union[str, dict[str, str]]]] = None,
        **kwargs):
    #
    # -- Set to default
    #
    bounds1 = none_to_default_dict(bounds1, "bounds1", defaults)
    bounds2 = none_to_default_dict(bounds2, "bounds2", defaults)
    ensure_constant_mask = none_to_default_dict(ensure_constant_mask, "ensure_constant_mask", defaults)
    filename1_input = none_to_default_dict(filename1_input, "filename1_input", defaults)
    filename_output = none_to_default_dict(filename_output, "filename_output", defaults)
    kwargs1_anom = none_to_default_dict(kwargs1_anom, "kwargs1_anom", defaults)
    kwargs1_average = none_to_default_dict(kwargs1_average, "kwargs1_average", defaults)
    kwargs1_detrend = none_to_default_dict(kwargs1_detrend, "kwargs1_detrend", defaults)
    kwargs_to_netcdf = none_to_default_dict(kwargs_to_netcdf, "kwargs_to_netcdf", defaults)
    variable1_input = none_to_default_dict(variable1_input, "variable1_input", defaults)
    variable_output = none_to_default_dict(variable_output, "variable_output", defaults)
    #
    # -- Read data
    #
    ds_n34 = netcdf_reader(filename1_input, bounds=bounds1, ensure_constant_mask=ensure_constant_mask,
                           kwargs_open_mfdataset={"data_vars": variable1_input})
    ds_tro = netcdf_reader(filename1_input, bounds=bounds2, ensure_constant_mask=ensure_constant_mask,
                           kwargs_open_mfdataset={"data_vars": variable1_input})
    #
    # -- Process
    #
    # spatial average
    ds_tro = average(ds_tro, variable=variable1_input, **kwargs1_average)
    # remove tropical mean
    ds_1 = ds_n34.copy(deep=True) - ds_tro.copy(deep=True)
    # compute anomalies
    ds_1 = interannual_anomalies(ds_1, **kwargs1_anom)
    ds_2 = interannual_anomalies(ds_n34, **kwargs1_anom)
    # detrend
    ds_3 = detrend(ds_2.copy(deep=True), variable=variable1_input, **kwargs1_detrend)
    # spatial average
    ds_1 = average(ds_1, variable=variable1_input, **kwargs1_average)
    ds_2 = average(ds_2, variable=variable1_input, **kwargs1_average)
    ds_3 = average(ds_3, variable=variable1_input, **kwargs1_average)
    #
    # -- Diagnostic
    #
    #
    # -- Save in netCDF
    #
    # print("global")
    # print(json__dumps(ds_1.attrs, indent=4))
    # print("variable")
    # print(list(ds_1.keys()))
    # for k in variable1_input:
    #     print(k.ljust(10), ds_1[k].shape)
    #     print(json__dumps(ds_1[k].attrs, indent=4))
    # stop
    # select output variables
    ds_o = {}
    for d1, v1 in zip([ds_1, ds_2, ds_3], ["ds_1", "ds_2", "ds_3"]):
        d1 = remove_unused_coordinates(d1)
        for var in variable1_input:
            # output array
            da = d1[var]
            # variable attributes
            att_v = copy__deepcopy(variable_output[v1][var]["attributes"])
            att_v["epoch"] = ""
            for k in get_time_bounds(da):
                if att_v["epoch"] != "":
                    att_v["epoch"] += " to "
                att_v["epoch"] += "-".join(k.split("-")[:2])
            att_v = dict(sorted(att_v.items()))
            # remove attributes
            for k in list(da.attrs.keys()):
                del da.attrs[k]
            # update attributes
            da.attrs.update(**att_v)
            # rename variable
            da = da.rename(variable_output[v1][var]["name"])
            ds_o[variable_output[v1][var]["name"]] = da
    # global attributes
    att_g = {}
    for k1, k2 in ds_1.attrs.items():
        if k1 not in ["comment", "Conventions", "history", "supplementary_information"]:
            att_g[k1] = copy__deepcopy(k2)
    # save dataset
    ds_o = dataset_wrapper(data_vars=ds_o, attrs=att_g)
    netcdf_writer(ds_o, filename_output, **kwargs_to_netcdf)
# ---------------------------------------------------------------------------------------------------------------------#
