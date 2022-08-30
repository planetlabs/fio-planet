# geomod.py: module supporting "fio geomod".
#
# Copyright 2022 Planet Labs PBC
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

from copy import copy
from collections import UserDict

import shapely
from shapely.geometry import mapping, shape

from . import snuggs

# Patch snuggs' func_map, extending it with Python builtins, geometry
# methods and attributes, and functions exported in the shapely module
# (such as set_precision).


def _explode(coords):
    if hasattr(coords, "geoms"):
        for part in coords.geoms:
            yield from _explode(part)
    elif hasattr(coords, "exterior"):
        yield from _explode(coords.exterior)
        for ring in coords.interiors:
            yield from _explode(ring)
    else:
        for coord in coords.coords:
            yield coord


class FuncMapper(UserDict):
    def __getitem__(self, key):
        if key in self.data:
            return self.data[key]
        elif key in __builtins__:
            return __builtins__[key]
        elif key in dir(shapely):
            return lambda g, *args, **kwargs: getattr(shapely, key)(g, *args, **kwargs)
        else:
            return (
                lambda g, *args, **kwargs: getattr(g, key)(*args, **kwargs)
                if callable(getattr(g, key))
                else getattr(g, key)
            )


func_map = dict(vertex_count=lambda g: sum(1 for coord in _explode(g)))

snuggs.func_map = FuncMapper(func_map)


def modulate(feature, pipeline):
    """Modulate the geometry of a feature by applying a pipeline of
    transformations.

    The pipeline is a string which, when evaluated by fio-geomod,
    produces a new geometry object. The pipeline consists of
    expressions in the form of parenthesized lists, which may contain
    other expressions. The first item in a list is the name of a
    Shapely geometry attribute or method. The second is the name of a
    Shapely geometry object or an expression that evaluates to a
    geometry object. The remaining list items are the positional and
    keyword arguments for the named method. The name of the input
    feature's geometry in the context of these expressions is "g".

    Parameters
    ----------
    feature : Feature
        A Fiona feature.
    pipeline : string
        Geometry operation pipeline such as
        "(exterior (buffer g 2.0))".

    Returns
    -------
    Feature
        A copy of the input feature, with a modulated geometry.

    """

    # Set up the expression evaluation context. We might extend this
    # using something like timeit's "--setup" statements, allowing a
    # user to define clip geometries, other things.
    geom = shape(feature["geometry"])
    new_geom = snuggs.eval(pipeline, g=geom, f=feature)
    new_feat = copy(feature)
    new_feat["geometry"] = mapping(new_geom)
    return new_feat
