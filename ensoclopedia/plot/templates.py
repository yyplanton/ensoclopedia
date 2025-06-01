# -*- coding:UTF-8 -*-
# ---------------------------------------------------------------------------------------------------------------------#
# Figure templates
# ---------------------------------------------------------------------------------------------------------------------#


# ---------------------------------------------------#
# Import packages
# ---------------------------------------------------#
# basic python package
from typing import Literal

# cartopy
import cartopy.crs as ccrs

# matplotlib
from matplotlib.gridspec import GridSpec
import matplotlib.pyplot as plt

# local package
from . panels import plot_main, plot_map
from . plot_tools import figure_axis, panel_numbering
from ensoclopedia.wrapper.tools import none_to_default
# ---------------------------------------------------#


# ---------------------------------------------------------------------------------------------------------------------#
# Figure templates
# ---------------------------------------------------------------------------------------------------------------------#
def fig_basic(
        dict_i: dict[str, dict[str, dict[str, list[float | int] | list[list[float | int]] | str]]],
        list_panel_group: list[str],
        n_panel_per_line: int,
        fig_axes: dict[str, dict[str, dict[str, float | int | list[float | int] | str | None]]],
        fig_format: Literal["eps", "pdf", "png", "svg"],
        fig_name: str,
        fig_panel_size: dict[str, dict[str, float | int]],
        fig_title_bool: bool = True,
        panel_position: Literal["bottom", "right"] = "right",
        panel_param: dict = None):
    # set None input to its default value
    panel_param = none_to_default(panel_param, {})
    # plot initialization
    x_frac, y_frac = fig_panel_size["frac"]["x"], fig_panel_size["frac"]["y"]
    panel_names = sorted([k for k in list(fig_panel_size.keys()) if k != "frac"], key=lambda s: s.lower())
    nbr_c, nbr_l = 0, 0
    for ii, grp in enumerate(list_panel_group):
        tmp_c, tmp_l = 0, 0
        for jj, pan in enumerate(list(dict_i[grp].keys())):
            if panel_position == "bottom":
                # panels are place in columns (i.e., panel 2 under panel 1)
                # number of columns (width) is the maximum panel width (x_size)
                tmp_c = max(tmp_c, fig_panel_size[pan]["x_size"])
                if jj + 1 == len(list(dict_i[grp].keys())) and (ii + 1) % n_panel_per_line != 0:
                    tmp_c += fig_panel_size[pan]["x_delt"]
                # number of lines (length) is the sum of panel length and space between (y_size + y_delt)
                tmp_l += fig_panel_size[pan]["y_delt"] + fig_panel_size[pan]["y_size"]
            else:
                # panels are place in lines (i.e., panel 2 on the right of panel 1)
                # number of columns (width) is the sum of panel width and space between (x_size + x_delt)
                tmp_c += fig_panel_size[pan]["x_delt"] + fig_panel_size[pan]["x_size"]
                # number of lines (length) is the maximum panel length (y_size)
                tmp_l = max(tmp_l, fig_panel_size[pan]["y_size"])
                if jj + 1 == len(list(dict_i[grp].keys())):
                    tmp_l += fig_panel_size[pan]["y_delt"]
        if (ii + 1) % n_panel_per_line == 0:
            # the maximum number of panel groups in a line has been reached, now only the number of lines is increased
            nbr_c = max(nbr_c, tmp_c)
            nbr_l += tmp_l
        else:
            nbr_c += tmp_c
            nbr_l += tmp_l
    plt.figure(0, figsize=(nbr_c * x_frac, nbr_l * y_frac))
    gs = GridSpec(nbr_l, nbr_c)
    numbering = panel_numbering(sum([1 for grp in list(dict_i.keys()) for _ in list(dict_i[grp].keys())]))
    x_position, y_position = 0, 0
    counter = 0
    for ii, grp in enumerate(list_panel_group):
        list_panels = [k for k in panel_names if k in list(dict_i[grp].keys())]
        for jj, pan in enumerate(list_panels):
            x_delt, y_delt = fig_panel_size[pan]["x_delt"], fig_panel_size[pan]["y_delt"]
            x_size, y_size = fig_panel_size[pan]["x_size"], fig_panel_size[pan]["y_size"]
            kwarg = {**panel_param, **{"x_size": x_size * x_frac, "y_size": y_size * y_frac}}
            if grp in list(dict_i.keys()) and pan in list(dict_i[grp].keys()):
                # data to plot
                kwarg.update(dict_i[grp][pan])
                # panel number
                if fig_title_bool is True:
                    kwarg["title"] = numbering[counter]
                # panel axes
                kwarg.update(fig_axes[grp][pan])
                # check if a map is plotted
                if "map_c" in list(kwarg.keys()):
                    # x-y axes
                    kwarg["x_lab"], _, = figure_axis(kwarg["x_tic"], axis_name="longitude")
                    kwarg["y_lab"], _, = figure_axis(kwarg["y_tic"], axis_name="latitude")
                    # projection
                    kwarg["projection"] = ccrs.PlateCarree(central_longitude=0)
                    crs180 = ccrs.PlateCarree(central_longitude=180)
                    # plot
                    ax = plt.subplot(
                        gs[y_position: y_position + y_size, x_position: x_position + x_size], projection=crs180)
                    plot_map(ax, **kwarg)
                else:
                    # check x/y axes
                    for k1 in ["x", "y", "y2", "y3"]:
                        if str(k1) + "_lab" not in list(kwarg.keys()) or str(k1) + "_tic" not in list(kwarg.keys()) or (
                                str(k1) + "_lab" in list(kwarg.keys()) and kwarg[str(k1) + "_lab"] is None) or (
                                str(k1) + "_tic" in list(kwarg.keys()) and kwarg[str(k1) + "_tic"] is None):
                            tic = None if str(k1) + "_tic" not in list(kwarg.keys()) else kwarg[str(k1) + "_tic"]
                            val = []
                            list_val = ["box", "cur", "den", "mar", "sha"]
                            if k1 == "y2":
                                list_val = [str(k2) + "2" for k2 in list_val]
                            elif k1 == "y3":
                                list_val = [str(k2) + "3" for k2 in list_val]
                            for k2 in list_val:
                                if str(k2) + "_" + str(k1) in list(kwarg.keys()):
                                    val.append(kwarg[str(k2) + "_" + str(k1)])
                                elif k2 == "sha":
                                    for k3 in ["1", "2"]:
                                        if str(k2) + "_" + str(k1) + str(k3) in list(kwarg.keys()):
                                            val.append(kwarg[str(k2) + "_" + str(k1) + str(k3)])
                            if tic is not None or len(val) > 0:
                                kwarg[str(k1) + "_lab"], kwarg[str(k1) + "_tic"] = figure_axis(tic, arr_i=val)
                    # plot
                    ax = plt.subplot(
                        gs[y_position: y_position + y_size, x_position: x_position + x_size])
                    plot_main(ax, **kwarg)
            if len(list_panels) > 1 and panel_position == "bottom":
                y_position += y_size + y_delt
            else:
                x_position += x_size + x_delt
            if (ii + 1) % n_panel_per_line == 0 and (jj + 1) == len(list_panels):
                x_position = 0
                y_position += y_size + y_delt
            counter += 1
    # save
    plt.savefig(str(fig_name) + "." + str(fig_format), bbox_inches="tight", format=fig_format)
    plt.close()
# ---------------------------------------------------------------------------------------------------------------------#
