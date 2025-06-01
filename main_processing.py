# -*- coding:UTF-8 -*-
# ---------------------------------------------------------------------------------------------------------------------#
# Main program to analyze input data
# ---------------------------------------------------------------------------------------------------------------------#


# ---------------------------------------------------#
# Import packages
# ---------------------------------------------------#
# local functions
import ensoclopedia.script_preprocess as proc
# ---------------------------------------------------#


# collect process scripts
scripts = {
    "f1a": proc.f01a_sst_eof_process,
    "f1b": proc.f01b_ts_time_series_process,
    "f1c": proc.f01c_gsat_reg_on_enso_process,
    "f1d": proc.f01d_pr_change_process,
    "f1e": proc.f01e_pr_change_process,
    "f7a": proc.f07a_precursors_process,
    # "t1": proc.t01_ssta_process,
}

scripts_names = sorted(list(scripts.keys()), key=lambda v: v.lower())
scripts_names_print = ", ".join(scripts_names)

print(__name__)
if __name__ == '__main__':
    name = input("Which script do you want to run?\n     Please enter one of: %s\n" % scripts_names_print)
    while name not in scripts_names + ["all"]:
        name = input("Given value %s does not correspond to a script\n     Please enter one of: %s\n" % (
            name, scripts_names_print))
    if name == "all":
        for k in scripts_names:
            scripts[k]()
    else:
        scripts[name]()
