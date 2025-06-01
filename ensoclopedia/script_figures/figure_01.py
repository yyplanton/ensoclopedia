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
            "filename": "data_output/figure_01a.nc",
            "variable": ["f01a--map_c"],
            "plot": {  # map
                "map_c": ["f01a--map_c"],
            },
        },
        "panel_b": {
            "filename": "data_output/figure_01b.nc",
            "variable": ["f01b--cur_y", "f01b--sha_y1", "f01b--sha_y2"],
            "plot": {  # time series
                "cur_c": ["k"],
                "cur_ls": ["-"],
                "cur_x": ["time"],
                "cur_y": ["f01b--cur_y"],
                "cur_z": [4],
                "sha_a": [0.5],
                "sha_c": ["grey"],
                "sha_x": ["time"],
                "sha_y1": ["f01b--sha_y1"],
                "sha_y2": ["f01b--sha_y2"],
                "sha_z": [3],
            },
        },
        "panel_c": {
            "filename": "data_output/figure_01c.nc",
            "variable": ["f01c--cur_y"],
            "plot": {  # lead-lag regression slope
                "cur_c": ["k"],
                "cur_ls": ["-"],
                "cur_x": ["month"],
                "cur_y": ["f01c--cur_y"],
                "cur_z": [4],
            },
        },
        "panel_d": {
            "filename": "data_output/figure_01d.nc",
            "variable": ["f01d--map_c"],
            "plot": {  # map of regression slope ratio
                "map_c": ["f01d--map_c"],
            },
        },
        "panel_e": {
            "filename": "data_output/figure_01e.nc",
            "variable": ["f01e--map_c"],
            "plot": {  # map of regression slope ratio
                "map_c": ["f01e--map_c"],
            },
        },
    },
    # add to plot
    "data_add": {
        "panel_a": {
            "plot": {  # lead-lag regression slope
                "region": ["insert"],
                "text": ["EOF1", "EOF2", "EOF3", "EOF4", "EOF5", "23.0", "6.7", "4.5", "4.0", "3.8"],
                "text_c": ["k"] * 10,
                "text_ha": ["center"] * 10,
                "text_va": ["top"] * 5 + ["bottom"] * 5,
                "text_x": [k - 180 for k in range(25, 191, 40)] * 2,
                "text_y": [-57] * 5 + [-85] * 5,
                "text_z": [6] * 10,
            },
        },
        "panel_b": {
            "plot": {  # time series
                "cur_c": ["k"],
                "cur_ls": [":"],
                "cur_x": [[1850, 2025]],
                "cur_y": [[0, 0]],
                "cur_z": [1],
                "sha_a": [0.2] * 43,
                "sha_c": ["r"] * 23 + ["b"] * 20,
                "sha_x": [[1951.4136986301369, 1952.0846994535518], [1953.0849315068492, 1954.1616438356164],
                          [1957.2465753424658, 1959.2465753424658], [1963.4136986301369, 1964.1639344262296],
                          [1965.3287671232877, 1966.3287671232877], [1968.7486338797814, 1969.4136986301369],
                          [1969.5808219178082, 1970.0849315068492], [1972.3306010928961, 1973.2465753424658],
                          [1976.6666666666667, 1977.1616438356164], [1977.6657534246576, 1978.0849315068492],
                          [1979.7479452054795, 1980.1639344262296], [1982.2465753424658, 1983.495890410959],
                          [1986.6657534246576, 1988.1639344262296], [1991.3287671232877, 1992.4972677595629],
                          [1994.6657534246576, 1995.2465753424658], [1997.3287671232877, 1998.4136986301369],
                          [2002.4136986301369, 2003.1616438356164], [2004.4972677595629, 2005.1616438356164],
                          [2006.6657534246576, 2007.0849315068492], [2009.495890410959, 2010.2465753424658],
                          [2014.7479452054795, 2016.3306010928961], [2018.6657534246576, 2019.495890410959],
                          [2023.3287671232877, 2024.3306010928961], [1950.0, 1950.5808219178082],
                          [1954.3287671232877, 1956.7486338797814], [1964.3306010928961, 1965.0849315068492],
                          [1970.495890410959, 1972.0846994535518], [1973.3287671232877, 1974.5808219178082],
                          [1974.7479452054795, 1976.3306010928961], [1983.6657534246576, 1984.0846994535518],
                          [1984.7486338797814, 1985.6657534246576], [1988.3306010928961, 1989.4136986301369],
                          [1995.5808219178082, 1996.2486338797814], [1998.495890410959, 2001.1616438356164],
                          [2005.8328767123287, 2006.2465753424658], [2007.4136986301369, 2008.4972677595629],
                          [2008.8333333333333, 2009.2465753424658], [2010.4136986301369, 2011.4136986301369],
                          [2011.495890410959, 2012.3306010928961], [2016.5819672131147, 2017.0],
                          [2017.7479452054795, 2018.3287671232877], [2020.5819672131147, 2021.4136986301369],
                          [2021.5808219178082, 2023.0849315068492]],
                "sha_y1": [[-1] * 2] * 43,
                "sha_y2": [[2] * 2] * 43,
                "sha_z": [2] * 43,
            },
        },
        "panel_c": {
            "plot": {  # lead-lag regression slope
                "cur_c": ["k"],
                "cur_ls": [":"],
                "cur_x": [[0, 78]],
                "cur_y": [[0, 0]],
                "cur_z": [1],
                "sha_a": [0.5],
                "sha_c": ["grey"],
                "sha_x": [[22, 24]],
                "sha_y1": [[-0.06] * 2],
                "sha_y2": [[0.12] * 2],
                "text": ["ENSO\npeak"],
                "text_c": ["grey"],
                "text_ha": ["left"],
                "text_va": ["center"],
                "text_x": [25],
                "text_y": [-0.03],
            },
        },
    },
    # figure
    "figure": {
        # name
        "filename": "figures/figure_01",
        # figure format: eps, pdf, png, svg
        "format": "pdf",
        # size of each panel
        "panel_size": {
            "frac": {"x": 0.02, "y": 0.02},
            "panel_a": {"x_delt": 30, "x_size": 360, "y_delt": 90, "y_size": 180},
            "panel_b": {"x_delt": 30, "x_size": 360, "y_delt": 60, "y_size": 120},
            "panel_c": {"x_delt": 30, "x_size": 180, "y_delt": 60, "y_size": 120},
            "panel_d": {"x_delt": 30, "x_size": 360, "y_delt": 40, "y_size": 180},
            "panel_e": {"x_delt": 30, "x_size": 360, "y_delt": 90, "y_size": 180},
        },
        # axes
        "panel_axes":{
            "panel_a": {
                "legend_position": "bottom",
                "map_c_cbar": "cmo.balance",
                "map_c_land": "dimgrey",
                "map_c_nam": {"f01a--map_c": "map_c_nam"},
                "map_c_tic": [round(k / 10, 1) for k in range(-10, 11, 5)],
                "x_lim": [0, 360],
                "x_tic": list(range(0, 361, 90)),
                "y_lim": [-90, 90],
                "y_tic": list(range(-90, 91, 45)),
            },
            "panel_b": {
                "x_lim": [1950, 2025],
                "x_nam": {"f01b--cur_y": "x_nam"},
                "x_tic": list(range(1860, 2026, 20)),
                "y_lim": [-0.7, 1.4],
                # "y_nam": {"f01b--cur_y": "y_nam"},
                "y_nam": "GSAT ($^\circ$C)",
                "y_tic": [round(k / 10, 1) for k in range(-7, 15, 7)],
            },
            "panel_c": {
                "x_lim": [12, 36],
                "x_lab": ["Jan$_{" + str((k - 24) // 12) + "}$" for k in range(12, 37, 12)],
                # "x_nam": {"f01c--cur_y": "x_nam"},
                "x_nam": "",
                "x_tic": list(range(12, 37, 12)),
                "y_lim": [-0.06, 0.12],
                # "y_nam": {"f01c--cur_y": "y_nam"},
                "y_nam": "ENSO influence\non GSAT ($^\circ$C)",
                "y_tic": [round(k / 100, 2) for k in range(-6, 13, 6)],
            },
            "panel_d": {
                "legend_position": None,
                "map_c_cbar": "cmo.balance",
                "map_c_land": None,
                "map_c_nam": "attribute--map_c_nam",
                "map_c_tic": list(range(-100, 101, 50)),
                "x_lim": [0, 360],
                "x_tic": list(range(0, 361, 90)),
                "y_lim": [-90, 90],
                "y_tic": list(range(-90, 91, 45)),
            },
            "panel_e": {
                "legend_position": "bottom",
                "map_c_cbar": "cmo.balance",
                "map_c_land": None,
                # "map_c_nam": {"f01e--map_c": "map_c_nam"},
                "map_c_nam": "ENSO influence on PR (%)",
                "map_c_tic": list(range(-100, 101, 50)),
                "x_lim": [0, 360],
                "x_tic": list(range(0, 361, 90)),
                "y_lim": [-90, 90],
                "y_tic": list(range(-90, 91, 45)),
            },
        },
    },
}
# ---------------------------------------------------------------------------------------------------------------------#


# ---------------------------------------------------------------------------------------------------------------------#
# Main
# ---------------------------------------------------------------------------------------------------------------------#
def f01_plot(
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
    group = "f1"
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
                        arr = get_time_plot(arr.to_index(), arr.dt.calendar)
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
        if panel == "panel_b":
            print("a", len(figure_data[grp][panel]["sha_a"]), "c", len(figure_data[grp][panel]["sha_c"]),
                  "x", len(figure_data[grp][panel]["sha_x"]), "y1", len(figure_data[grp][panel]["sha_y1"]),
                  "y2", len(figure_data[grp][panel]["sha_y2"]), "z", len(figure_data[grp][panel]["sha_z"]))
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
    panel_sizes = default_panel_sizes(figure)
    # plot using basic template
    list_groups = list(figure_data.keys())
    fig_basic(figure_data, list_groups, 1, figure_axes, figure_format, figure_name, panel_sizes)
# if ' ':
#     d_en = {
#         1951: {"a": {"year": 1951, "month": 6}, "b": {"year": 1952, "month": 2},},
#         1953: {"a": {"year": 1953, "month": 2}, "b": {"year": 1954, "month": 3},},
#         1957: {"a": {"year": 1957, "month": 4}, "b": {"year": 1959, "month": 4},},
#         1963: {"a": {"year": 1963, "month": 6}, "b": {"year": 1964, "month": 3},},
#         1965: {"a": {"year": 1965, "month": 5}, "b": {"year": 1966, "month": 5},},
#         1968: {"a": {"year": 1968, "month": 10}, "b": {"year": 1969, "month": 6},},
#         1969: {"a": {"year": 1969, "month": 8}, "b": {"year": 1970, "month": 2},},
#         1972: {"a": {"year": 1972, "month": 5}, "b": {"year": 1973, "month": 4},},
#         1976: {"a": {"year": 1976, "month": 9}, "b": {"year": 1977, "month": 3},},
#         1977: {"a": {"year": 1977, "month": 9}, "b": {"year": 1978, "month": 2},},
#         1979: {"a": {"year": 1979, "month": 10}, "b": {"year": 1980, "month": 3},},
#         1982: {"a": {"year": 1982, "month": 4}, "b": {"year": 1983, "month": 7},},
#         1986: {"a": {"year": 1986, "month": 9}, "b": {"year": 1988, "month": 3},},
#         1991: {"a": {"year": 1991, "month": 5}, "b": {"year": 1992, "month": 7},},
#         1994: {"a": {"year": 1994, "month": 9}, "b": {"year": 1995, "month": 4},},
#         1997: {"a": {"year": 1997, "month": 5}, "b": {"year": 1998, "month": 6},},
#         2002: {"a": {"year": 2002, "month": 6}, "b": {"year": 2003, "month": 3},},
#         2004: {"a": {"year": 2004, "month": 7}, "b": {"year": 2005, "month": 3},},
#         2006: {"a": {"year": 2006, "month": 9}, "b": {"year": 2007, "month": 2},},
#         2009: {"a": {"year": 2009, "month": 7}, "b": {"year": 2010, "month": 4},},
#         2014: {"a": {"year": 2014, "month": 10}, "b": {"year": 2016, "month": 5},},
#         2018: {"a": {"year": 2018, "month": 9}, "b": {"year": 2019, "month": 7},},
#         2023: {"a": {"year": 2023, "month": 5}, "b": {"year": 2024, "month": 5},},
#     }
#     d_ln = {
#         1950: {"a": {"year": 1950, "month": 1}, "b": {"year": 1950, "month": 8},},
#         1954: {"a": {"year": 1954, "month": 5}, "b": {"year": 1956, "month": 10},},
#         1964: {"a": {"year": 1964, "month": 5}, "b": {"year": 1965, "month": 2},},
#         1970: {"a": {"year": 1970, "month": 7}, "b": {"year": 1972, "month": 2},},
#         1973: {"a": {"year": 1973, "month": 5}, "b": {"year": 1974, "month": 8},},
#         1974: {"a": {"year": 1974, "month": 10}, "b": {"year": 1976, "month": 5},},
#         1983: {"a": {"year": 1983, "month": 9}, "b": {"year": 1984, "month": 2},},
#         1984: {"a": {"year": 1984, "month": 10}, "b": {"year": 1985, "month": 9},},
#         1988: {"a": {"year": 1988, "month": 5}, "b": {"year": 1989, "month": 6},},
#         1995: {"a": {"year": 1995, "month": 8}, "b": {"year": 1996, "month": 4},},
#         1998: {"a": {"year": 1998, "month": 7}, "b": {"year": 2001, "month": 3},},
#         2005: {"a": {"year": 2005, "month": 11}, "b": {"year": 2006, "month": 4},},
#         2007: {"a": {"year": 2007, "month": 6}, "b": {"year": 2008, "month": 7},},
#         2008: {"a": {"year": 2008, "month": 11}, "b": {"year": 2009, "month": 4},},
#         2010: {"a": {"year": 2010, "month": 6}, "b": {"year": 2011, "month": 6},},
#         2011: {"a": {"year": 2011, "month": 7}, "b": {"year": 2012, "month": 5},},
#         2016: {"a": {"year": 2016, "month": 8}, "b": {"year": 2017, "month": 1},},
#         2017: {"a": {"year": 2017, "month": 10}, "b": {"year": 2018, "month": 5},},
#         2020: {"a": {"year": 2020, "month": 8}, "b": {"year": 2021, "month": 6},},
#         2021: {"a": {"year": 2021, "month": 8}, "b": {"year": 2023, "month": 2},},
#     }
#     from datetime import datetime as datetime__datetime
#     arr_x = []
#     for k1, d1 in d_en.items():
#         arr_t = []
#         for k2, d2 in d1.items():
#             # year and month
#             year, month = d2["year"], d2["month"]
#             # create datetime for this year and the current time
#             year_start = datetime__datetime(year, 1, 1, 0, 0, 0)
#             year_end = datetime__datetime(year + 1, 1, 1, 0, 0, 0)
#             year_now = datetime__datetime(year, month, 1, 0, 0, 0)
#             # number of seconds from the beginning of the year and total number of seconds during this year
#             sec_now = (year_now - year_start).total_seconds()
#             sec_tot = (year_end - year_start).total_seconds()
#             # time is year + second fraction
#             arr_t.append(year + sec_now / sec_tot)
#         arr_x.append(arr_t)
#     for k1, d1 in d_ln.items():
#         arr_t = []
#         for k2, d2 in d1.items():
#             # year and month
#             year, month = d2["year"], d2["month"]
#             # create datetime for this year and the current time
#             year_start = datetime__datetime(year, 1, 1, 0, 0, 0)
#             year_end = datetime__datetime(year + 1, 1, 1, 0, 0, 0)
#             year_now = datetime__datetime(year, month, 1, 0, 0, 0)
#             # number of seconds from the beginning of the year and total number of seconds during this year
#             sec_now = (year_now - year_start).total_seconds()
#             sec_tot = (year_end - year_start).total_seconds()
#             # time is year + second fraction
#             arr_t.append(year + sec_now / sec_tot)
#         arr_x.append(arr_t)
#     print("en", len(list(d_en.keys())))
#     print("ln", len(list(d_ln.keys())))
#     print("to", len(list(d_en.keys()) + list(d_ln.keys())))
#     d = 2
#     for k in range(0, len(arr_x), d):
#         print(arr_x[k: k + d])
# ---------------------------------------------------------------------------------------------------------------------#
