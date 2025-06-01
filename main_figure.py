# -*- coding:UTF-8 -*-
# ---------------------------------------------------------------------------------------------------------------------#
# Main program to plot figures
# ---------------------------------------------------------------------------------------------------------------------#


# ---------------------------------------------------#
# Import packages
# ---------------------------------------------------#
# local functions
import ensoclopedia.script_figures as fig
# ---------------------------------------------------#


# collect figure scripts
figures = {
    "f1": fig.f01_plot,
    "f7": fig.f07_plot,
}

figure_names = sorted(list(figures.keys()), key=lambda v: v.lower())
figure_names_print = ", ".join(figure_names)

print(__name__)
if __name__ == '__main__':
    name = input("Which figure do you want to plot?\n     Please enter one of: %s\n" % figure_names_print)
    while name not in figure_names + ["all"]:
        name = input("Given value %s does not correspond to a script\n     Please enter one of: %s\n" % (
            name, figure_names_print))
    if name == "all":
        for k in figure_names:
            figures[k]()
    else:
        figures[name]()
