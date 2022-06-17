# layout.py
#
# Còdixi chi serbit po cuncordai is màginis de sa pròpriu manera.
#
# Copyright 2022 Sustainable Sardinia
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import matplotlib.pyplot as plt
import matplotlib
import matplotlib.gridspec as gridspec
import copy
import sigfig
import matplotlib.transforms
import matplotlib.colors
import numpy as np


def break_text(text, num_characters) -> str:
    """Break the text into lines of max the given number of characters."""
    words = text.split(" ")
    output_string = ""
    length_current_line = 0
    for index, curr_word in enumerate(words):
        length_curr_word = len(curr_word)

        if index == 0:
            length_current_line = length_curr_word
            curr_separator = ""
        elif length_current_line + 1 + length_curr_word <= num_characters:
            length_current_line += 1 + length_curr_word
            curr_separator = " "
        else:
            length_current_line = length_curr_word
            curr_separator = "\n"
        output_string += curr_separator + curr_word
    return output_string


def set_style() -> dict():
    """Set the default style for an infographic."""
    style_options = {
        "edge_color": "#666A6D",
        "foreground_color": "white",
        "background_color": "black",
        "missing_color": "#A9A9A9",
        "description_text_color": "#BFBFBF",
        "title_size": 26,
        "axis_label_size": 18,
        "tick_label_size": 15,
        "description_text_size": 12,
        "small_text_size": 10,
        "max_description_text_characters": 100,
    }
    matplotlib.rcParams["font.family"] = "sans-serif"
    matplotlib.rcParams["font.sans-serif"] = "Source Sans Pro"
    matplotlib.rcParams["text.color"] = style_options["foreground_color"]
    matplotlib.rcParams["axes.edgecolor"] = style_options["foreground_color"]
    return style_options


def create_default_image_canvas(style_options, num_parts=3):
    """Create an image canvas of the correct size"""
    fig = plt.figure(
        figsize=(7.8, 10),
        dpi=300,
        facecolor=style_options["background_color"],
        tight_layout=True,
    )
    if num_parts == 3:
        width_ratios = [0.75, 0.15]
        num_cols = 2
    else:
        width_ratios = [0.1, 0.8, 0.1]
        num_cols = 3

    grid = gridspec.GridSpec(
        3,
        num_cols,
        height_ratios=[0.90, 0.03, 0.07],
        width_ratios=width_ratios,
        hspace=0.22,
    )

    if num_parts == 2:
        axes = [fig.add_subplot(grid[0, :]), fig.add_subplot(grid[1, 1])]
        fig.add_subplot(grid[1, 0], facecolor=style_options["background_color"]).axis(
            "off"
        )

        fig.add_subplot(grid[1, 2], facecolor=style_options["background_color"]).axis(
            "off"
        )

    else:
        axes = [
            fig.add_subplot(grid[0, :]),
            fig.add_subplot(grid[1, 0]),
            fig.add_subplot(grid[1, 1]),
        ]
    return (fig, axes)


def plot_main_map(
    map_axis, data, data_column, classes, missing_label, style_options, cmap="Reds"
):
    """Plot the main map in the infographics"""
    plt.tick_params(left=False, bottom=False, labelleft=False, labelbottom=False)

    num_classes = len(classes) - 1

    _ = data.plot(
        column=data_column,
        cmap=cmap,
        ax=map_axis,
        linewidth=0.5,
        edgecolor=style_options["edge_color"],
        k=num_classes,
        scheme="EqualInterval",
        legend=False,
        missing_kwds={"color": style_options["missing_color"], "label": missing_label},
    )

    # No box around plot
    map_axis.axis("off")


def _format_float_values(value):
    return sigfig.round(value, 3)


def _create_base_colorbar(fig, colorbar_axis, main_ticks, cmap):
    norm = matplotlib.colors.BoundaryNorm(main_ticks, cmap.N, extend="neither")

    colorbar = fig.colorbar(
        matplotlib.cm.ScalarMappable(norm=norm, cmap=cmap),
        cax=colorbar_axis,
        orientation="horizontal",
        drawedges=True,
    )
    return colorbar


def _set_colorbar_ticks_style(colorbar_axis, style_options):
    colorbar_axis.tick_params(
        axis="x",
        colors=style_options["foreground_color"],
        labelcolor=style_options["foreground_color"],
        grid_color=style_options["edge_color"],
        labelsize=style_options["tick_label_size"],
    )


def _format_colorbar_scale(axis, classes, label_title, style_options):
    foreground_color = style_options["foreground_color"]

    _set_colorbar_ticks_style(axis, style_options)

    axis.set_xlabel(
        label_title,
        color=foreground_color,
        size=style_options["axis_label_size"],
        labelpad=10,
    )

    axis.set_xticks(list(np.linspace(0, 1, len(classes))))

    bottom_labels = [_format_float_values(l) for l in classes]
    axis.set_xticklabels(bottom_labels)
    return axis


def _format_reference_countries(
    axis,
    xlim,
    countries_data,
    values_column,
    date_column,
    lang_column,
    min_data,
    style_options,
):
    countries_data = countries_data.loc[countries_data[values_column] >= min_data]

    countries_labels = countries_data.apply(
        lambda r: f"{r[lang_column]}\n{_format_float_values(r[values_column])} ({r[date_column]})",
        axis=1,
    )

    axis.set_xlim(xlim)
    axis.set_xticks(ticks=countries_data[values_column].to_numpy())
    axis.set_xticklabels(
        countries_labels, rotation=-40, ha="left", rotation_mode="anchor"
    )

    axis.tick_params(
        axis="x",
        length=10,
        colors=style_options["foreground_color"],
        labelcolor=style_options["foreground_color"],
        grid_color=style_options["edge_color"],
        labelsize=style_options["description_text_size"],
    )


def plot_colorbar(
    fig,
    colorbar_axis,
    countries_data,
    values_column,
    year_column,
    lang_column,
    min_data,
    classes,
    label_title,
    colormap,
    style_options,
):
    """Plot the colorbar for the data, adding all the information
    from other countries."""
    top_color_axis = colorbar_axis.twiny()
    bottom_color_axis = copy.copy(colorbar_axis)

    colorbar = _create_base_colorbar(
        fig, colorbar_axis, main_ticks=classes, cmap=colormap
    )

    _format_colorbar_scale(top_color_axis, classes, label_title, style_options)

    _format_reference_countries(
        bottom_color_axis,
        bottom_color_axis.get_xlim(),
        countries_data,
        values_column,
        year_column,
        lang_column,
        min_data,
        style_options,
    )
    colorbar.dividers.set_linewidth(1)


def plot_empty_data_colorbar(fig, colorbar_axis, missing_label, style_options):
    """Plot the colorbar that refers to empty data"""
    foreground_color = style_options["foreground_color"]

    cmap = matplotlib.colors.ListedColormap([style_options["missing_color"]])

    colorbar = fig.colorbar(
        matplotlib.cm.ScalarMappable(cmap=cmap),
        cax=colorbar_axis,
        orientation="horizontal",
        drawedges=True,
    )

    _set_colorbar_ticks_style(colorbar_axis, style_options)
    colorbar_axis.tick_params(size=0)
    colorbar.set_ticks([])
    colorbar.set_label(
        missing_label,
        size=style_options["tick_label_size"],
        labelpad=7.2,
        color=foreground_color,
    )

    return colorbar


def _get_classes(data, values_column, num_classes):
    actual_min = data[values_column].min()
    actual_max = data[values_column].max()

    classes = np.linspace(actual_min, actual_max, num_classes + 1).tolist()
    return sorted(classes)


def _assign_value_to_class(v, classes):
    for index in range(0, len(classes)):
        if v >= classes[index] and v < classes[index + 1]:
            return index
        if v == classes[-1]:
            return len(classes) - 1
    return None


def divide_data_into_classes(data, values_column, num_classes):
    """Divide the values in a dataframe column into classes"""
    classes = _get_classes(data, values_column, num_classes)
    classes_assignment = data[values_column].apply(
        lambda g: _assign_value_to_class(g, classes)
    )
    return (classes_assignment, classes)
