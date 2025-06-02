# -*- coding:UTF-8 -*-
# ---------------------------------------------------------------------------------------------------------------------#
# Figure 1
# ---------------------------------------------------------------------------------------------------------------------#


# ---------------------------------------------------#
# Import packages
# ---------------------------------------------------#
# basic python package
from copy import deepcopy as copy__deepcopy
from json import dumps as json__dumps

# local functions
from ensoclopedia.plot.templates import fig_basic
from ensoclopedia.wrapper.time_tools import get_time_plot
from ensoclopedia.wrapper.tools import default_figure_format, default_figure_name, default_panel_sizes, \
    none_to_default_dict, put_in_dict
from ensoclopedia.wrapper.processors import netcdf_reader
# ---------------------------------------------------#


# ---------------------------------------------------------------------------------------------------------------------#
# Default arguments
# ---------------------------------------------------------------------------------------------------------------------#
defaults = {
    # input data
    "data": {
        "panel_a": {
            "filename": "data_output/figure_07a.nc",
            "variable": ["sossheig_n34e--cur_y", "sossheig_pequ--cur_y", "sossheig_peqw--cur_y"],
            "plot": {  # map
                "cur_c": ["k", "r", "b"],
                "cur_ls": ["-", "--", "-."],
                "cur_lw": [2, 2, 2],
                "cur_x": ["month", "month", "month"],
                "cur_y": ["sossheig_n34e--cur_y", "sossheig_pequ--cur_y", "sossheig_peqw--cur_y"],
                "cur_z": [4, 4, 4],
            },
        },
    },
    # add to plot
    "data_add": {
        "panel_a": {
            "plot": {  # lead-lag regression slope
                "cur_c": ["k", "k", "r", "b"],
                "cur_ls": [":", "-", "--", "-."],
                "cur_lw": [1, 2, 2, 2],
                "cur_x": [[0, 78], [0.5, 3], [0.5, 3], [0.5, 3]],
                "cur_y": [[0, 0], [-0.5, -0.5], [-0.7, -0.7], [-0.9, -0.9]],
                "cur_z": [1, 1, 1, 1],
                "sha_a": [0.5],
                "sha_c": ["grey"],
                "sha_x": [[22, 24]],
                "sha_y1": [[-1] * 2],
                "sha_y2": [[1] * 2],
                "text": ["ENSO\npeak", {"sossheig_n34e--cur_y": "short_name"}, {"sossheig_pequ--cur_y": "short_name"},
                         {"sossheig_peqw--cur_y": "short_name"},],
                "text_c": ["grey", "k", "r", "b"],
                "text_fs": [12, 12, 12, 12],
                "text_ha": ["right", "left", "left", "left"],
                "text_va": ["center", "center", "center", "center"],
                "text_x": [21.8, 3.5, 3.5, 3.5],
                "text_y": [0.5, -0.5, -0.7, -0.9],
            },
        },
    },
    # figure
    "figure": {
        # name
        "filename": "figures/figure_07",
        # figure format: eps, pdf, png, svg
        "format": "pdf",
        # size of each panel
        "panel_size": {
            "frac": {"x": 0.02, "y": 0.02},
            "panel_a": {"x_delt": 30, "x_size": 180, "y_delt": 60, "y_size": 120},
        },
        # axes
        "panel_axes":{
            "panel_a": {
                "x_lim": [0, 36],
                "x_lab": ["Jan$_{" + str((k - 24) // 12) + "}$" for k in range(0, 37, 12)],
                # "x_nam": {"f01c--cur_y": "x_nam"},
                "x_nam": "",
                "x_tic": list(range(0, 37, 12)),
                "y_lim": [-1, 1],
                # "y_nam": {"f01c--cur_y": "y_nam"},
                "y_nam": "correlations",
                "y_tic": [round(k / 10, 1) for k in range(-10, 11, 5)],
            },
        },
    },
}
# ---------------------------------------------------------------------------------------------------------------------#


# ---------------------------------------------------------------------------------------------------------------------#
# Main
# ---------------------------------------------------------------------------------------------------------------------#
def f07_plot(
        data: dict = None,
        data_add: dict = None,
        figure: dict = None,
        **kwargs):
    #
    # -- Set to default
    #
    data = none_to_default_dict(data, "data", defaults)
    data_add = none_to_default_dict(data_add, "data_add", defaults)
    figure = none_to_default_dict(figure, "figure", defaults)
    #
    # -- Organize panels
    #
    figure_axes, figure_data = {}, {}
    group = "f7"
    for panel in list(data.keys()):
        print(panel)
        print(str().ljust(5), data[panel]["filename"])
        print(str().ljust(5), data[panel]["variable"])
        # read netcdf
        ds = netcdf_reader(**data[panel])
        grp = str(group) + str(panel)
        # select data to plot
        for k1, k2 in data[panel]["plot"].items():
            list_k3 = [k2] if isinstance(k2, str) is True else copy__deepcopy(k2)
            for k3 in list_k3:
                arr = copy__deepcopy(k3)
                if k3 in list(ds.keys()) + list(ds.coords):
                    arr = ds[k3]
                    if k3 == "time":
                        # convert time to year fraction
                        arr = get_time_plot(arr.to_index())
                if "map_" not in k1:
                    arr = [arr]
                put_in_dict(figure_data, arr, grp, panel, k1)
        # data to add
        if isinstance(data_add, dict) is True and panel in list(data_add.keys()) and \
                isinstance(data_add[panel], dict) is True and "plot" in list(data_add[panel].keys()) and \
                isinstance(data_add[panel]["plot"], dict) is True:
            for k1, k2 in data_add[panel]["plot"].items():
                list_k3 = [k2] if isinstance(k2, str) is True else copy__deepcopy(k2)
                for k3 in list_k3:
                    if isinstance(k3, dict) is True:
                        for k4, k5 in k3.items():
                            put_in_dict(figure_data, [ds[k4].attrs[k5]], grp, panel, k1)
                    else:
                        put_in_dict(figure_data, [k3], grp, panel, k1)
        # select axes information
        if isinstance(figure, dict) is True and "panel_axes" in list(figure.keys()) and \
                isinstance(figure["panel_axes"], dict) is True and panel in list(figure["panel_axes"].keys()) and \
                isinstance(figure["panel_axes"][panel], dict) is True:
            put_in_dict(figure_axes, figure["panel_axes"][panel], grp, panel)
            # update axes using array attributes
            for k1 in list(figure["panel_axes"][panel].keys()):
                if isinstance(figure["panel_axes"][panel][k1], dict) is True:
                    for k2, k3 in figure["panel_axes"][panel][k1].items():
                        figure_axes[grp][panel][k1] = ds[k2].attrs[k3]
    #
    # -- Plot
    #
    # default outputs if not provided
    figure_format = default_figure_format(figure)
    figure_name = default_figure_name(figure, __file__)
    panel_sizes = default_panel_sizes(figure, figure_data)
    # plot using basic template
    list_groups = list(figure_data.keys())
    fig_basic(figure_data, list_groups, 1, figure_axes, figure_format, figure_name, panel_sizes)
# ---------------------------------------------------------------------------------------------------------------------#
