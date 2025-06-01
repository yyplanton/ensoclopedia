# -*- coding:UTF-8 -*-
# ---------------------------------------------------------------------------------------------------------------------#
# Basic tools
# ---------------------------------------------------------------------------------------------------------------------#


# ---------------------------------------------------#
# Import packages
# ---------------------------------------------------#
# basic python package
from typing import Any, Hashable, Literal, Union
from os.path import dirname as os__path__dirname
from os.path import join as os__path__join
# ---------------------------------------------------#


# ---------------------------------------------------------------------------------------------------------------------#
# Classes
# ---------------------------------------------------------------------------------------------------------------------#
class BackgroundColors:
    blue = '\033[94m'
    green = '\033[92m'
    orange = '\033[93m'
    red = '\033[91m'
    normal = '\033[0m'
# ---------------------------------------------------------------------------------------------------------------------#


# ---------------------------------------------------------------------------------------------------------------------#
# Functions
# ---------------------------------------------------------------------------------------------------------------------#
def default_figure_format(figure: dict) -> Literal["eps", "pdf", "png", "svg"]:
    # define figure name
    figure_format = "pdf"
    if isinstance(figure, dict) is True and "format" in list(figure.keys()) and \
            isinstance(figure["format"], str) is True and figure["format"] in ["eps", "pdf", "png", "svg"]:
        figure_format = figure["format"]
    return figure_format


def default_figure_name(figure: dict, filename: str) -> str:
    # define figure name
    if isinstance(figure, dict) is True and "filename" in list(figure.keys()) and \
            isinstance(figure["filename"], str) is True:
        figure_name = figure["filename"]
    else:
        # directory
        directory = "/".join(os__path__dirname(filename).split("/")[:-2]) + "/figures"
        # file name
        figure_name = filename.split("/")[-1].split(".")[0]
        figure_name = os__path__join(directory, figure_name)
    return figure_name


def default_panel_sizes(figure):
    # default values
    default = {
        "frac": {"x": 1, "y": 1},
        "panel": {"x_delt": 4, "x_size": 2, "y_delt": 2, "y_size": 4},
    }
    # define panel size dictionary
    panel_size = {}
    if isinstance(figure, dict) is True and "panel_size" in list(figure.keys()) and \
            isinstance(figure["panel_size"], dict) is True:
        panel_size = figure["panel_size"]
    # fill missing values
    if "frac" not in list(panel_size.keys()):
        panel_size["frac"] = default["frac"]
    else:
        for k in list(default["frac"].keys()):
            if k not in list(panel_size["frac"].keys()):
                put_in_dict(panel_size, default["frac"][k], "frac", k)
    return panel_size


def is_dim(dim: Any) -> bool:
    """
    Do a test on dimension type to decide if it is probably one

    Input:
    ------
    :param dim: Any
        Object to test, usually a string

    Output:
    -------
    :return: bool
    """
    return dim is not None and isinstance(dim, (Hashable, str)) is True


def is_variables(variable: Any) -> bool:
    """
    Do a test on variable type to decide if it is probably a list of variables (data_vars)

    Input:
    ------
    :param variable: Any
        Object to test, usually a list of string

    Output:
    -------
    :return: bool
    """
    bool_o = False
    if variable is not None and isinstance(variable, list) is True and \
            all([isinstance(k, str) is True for k in variable]) is True:
        bool_o = True
    return bool_o


def merge_dict(dict_a: dict, dict_b: dict, name_a: str, name_b: str) -> dict:
    """
    Merge keys and values from two dictionaries

    Input:
    ------
    :param dict_a: dict
        Dictionary to merge
    :param dict_b: dict
        Same as dict_a
    :param name_a: str
        Name of dict_a
    :param name_b: str
        Name of dict_b

    Output:
    -------
    :return: dict
        Dictionary with combined keys and values from both input dictionaries.
    """
    dict_o = {}
    # combine dictionaries
    for dd, nn in zip([dict_a, dict_b], [name_a, name_b]):
        for ki, vv in dd.items():
            ko = ki.lower()
            if ko in list(dict_o.keys()):
                dict_o[ko] += ";; " + str(nn) + ") " + str(vv)
            else:
                dict_o[ko] = str(nn) + ") " + str(vv)
            # if ko in list(dict_o.keys()):
            #     dict_o[ko] = dict_o[ko] + "\n", str(nn) + ") " + str(vv)
            # else:
            #     dict_o[ko] = str(nn) + ") " + str(vv)
    return dict_o


def none_to_default(input_value: Any, default_value: Any) -> Any:
    """
    Set input_value to given default_value if input_value is None.

    Input:
    ------
    :param input_value: Any
        Input variable, can be anything
    :param default_value: Any
        Default value for input_value, can be anything

    Output:
    -------
    :return: Any
        default_value if input_value is None, else input_value
    """
    if input_value is None:
        return default_value
    else:
        return input_value


def none_to_default_dict(input_value: Any, name: str, defaults: dict) -> Any:
    """
    Set input_value to given defaults[name] if input_value is None (and is name is in defaults).

    Input:
    ------
    :param input_value: Any
        Input variable, can be anything
    :param name: str
        Name in defaults dictionary
    :param defaults: dict
        Dictionary of default values

    Output:
    -------
    :return: Any
        If input_value is None, defaults[name], else input_value
    """
    if input_value is None and isinstance(defaults, dict) is True and name in list(defaults.keys()):
        return defaults[name]
    else:
        return input_value


def plural_s(list_i: Union[list, tuple]) -> str:
    """
    Return 's' if there are multiple values in the list

    Input:
    ------
    :param list_i: list

    Output:
    -------
    :return: str
        's' if there are multiple values in the list else ''
    """
    return "s" if isinstance(list_i, (list, tuple)) is True and len(list_i) > 1 else ""


def print_fail(stack_i: list, error_i: str, fail_i: bool = True):
    """
    Print error message and, if asked, stop the code

    Input:
    ------
    :param stack_i: list
        Given by inspect.stack()
    :param error_i: str
        Encountered errors
    :param fail_i: bool
        True to stop the code
    """
    if isinstance(error_i, str) and error_i != "":
        tmp = "ERROR: file " + str(stack_i[0][1]) + " ; fct " + str(stack_i[0][3]) + " ; line " + str(stack_i[0][2])
        if fail_i is True:
            raise ValueError(BackgroundColors.red + str(tmp) + "\n" + str(error_i) + BackgroundColors.normal)
        else:
            print(BackgroundColors.orange + str(tmp) + "\n" + str(error_i) + BackgroundColors.normal)


def put_in_dict(dict_i: dict, value: Any, *args):
    """
    Put value in the dictionary

    Input:
    ------
    :param dict_i: dict
        Dictionary in which the value must be added
    :param value: Any
        Value to add in the dictionary
        If it is a list, it will be appended to the list already inside the dictionary
    :param args: str
        Non keyword arguments used as keys in the dictionary
    """
    # put value in the dictionary
    _dict = dict_i
    for k in args:
        if k == args[-1]:
            if k in list(_dict.keys()) and isinstance(_dict[k], list) is True and isinstance(value, list) is True:
                _dict[k] += value
            else:
                _dict[k] = value
        else:
            if k not in list(_dict.keys()):
                _dict[k] = {}
            _dict = _dict[k]


def remove_keys(dict_i: dict, desired_keys: list[str] = None, keys_to_remove: list[str] = None):
    """
    Prune input dictionary (remove not desired keys or remove given keys).

    Input:
    ------
    :param dict_i: dict
        Dictionary to prune; e.g., dict_i = ['a': 0, 'b': 1]
    :param desired_keys: list[str], optional
        List of keys that should be kept if present in the input dictionary; e.g., desired_keys = ['a']
    :param keys_to_remove: list[str], optional
        List of keys that should be removed if present in the input dictionary; e.g., desired_keys = ['b']
    """
    for k in list(dict_i.keys()):
        if (isinstance(desired_keys, list) is True and k not in desired_keys) or (
                isinstance(keys_to_remove, list) is True and k in keys_to_remove):
            del dict_i[k]


def unknown_formater(name: str, unknown: str, known: Union[list, tuple]):
    """
    Format error/warning message when a given string is not among the defined (known).

    Input:
    ------
    :param name: str
        Name of the tested value
    :param unknown: str
        Unknown keyword
    :param known: list or tuple
        Listed defined (known) keywords

    Output:
    -------
    :return: str
        Formated error/warning message
    """
    str_o = str().ljust(5) + "unknown " + str(name) + " " + str(unknown)
    str_o += "\n" + str().ljust(5) + str(name) + str(plural_s(known)) + ": " + ", ".join([repr(k) for k in known])
    return str_o
# ---------------------------------------------------------------------------------------------------------------------#
