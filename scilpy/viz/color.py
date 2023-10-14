# -*- coding: utf-8 -*-

import matplotlib.pyplot as plt
from matplotlib import colors
import numpy as np

from scilpy.viz.backends.vtk import get_color_by_name
from scilpy.viz.backends.fury import (distinguishable_colormap,
                                      numpy_to_vtk_colors)


def convert_color_names_to_rgb(names):
    """
    Convert a list of VTK color names to RGB
    """

    return [get_color_by_name(name) for name in names]


BASE_10_COLORS = convert_color_names_to_rgb(["Blue",
                                             "Yellow",
                                             "Purple",
                                             "Green",
                                             "Orange",
                                             "White",
                                             "Brown",
                                             "Grey"])
    

def generate_n_colors(n, generator=distinguishable_colormap, 
                      pick_from_base10=True, shuffle=False):
    """
    Generate a set of N colors (unicity not guaranteed, based on the generator)

    Parameters
    ----------
    n : int
        Number of colors to generate.
    generator : function
        Color generating function f(n, exclude=[...]) -> [color, color, ...],
        accepting an optional list of colors to exclude from the generation.
    pick_from_base10 : bool
        When True, start picking from the base 10 colors before using 
        the generator funtion (see BASE_COLORS_10).
    shuffle : bool
        Shuffle the color list before returning.

    Returns
    -------
    colors : np.ndarray
        A list of Nx3 RGB colors
    """

    _colors = []

    if pick_from_base10:
        _colors = np.array(BASE_10_COLORS[:min(n, 10)])

    if n - len(_colors):
        _colors = np.concatenate(
            (_colors, generator(n - len(_colors), exclude=_colors)), axis=0)

    if shuffle:
        np.random.shuffle(_colors)

    return numpy_to_vtk_colors(_colors)


def get_colormap(name):
    """Get a matplotlib colormap from a name or a list of named colors.

    Parameters
    ----------
    name : str
        Name of the colormap or a list of named colors (separated by a -).

    Returns
    -------
    matplotlib.colors.Colormap
        The colormap
    """

    if '-' in name:
        name_list = name.split('-')
        colors_list = [colors.to_rgba(color)[0:3] for color in name_list]
        cmap = colors.LinearSegmentedColormap.from_list('CustomCmap',
                                                        colors_list)
        return cmap

    return plt.colormaps.get_cmap(name)


