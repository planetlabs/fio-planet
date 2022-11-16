# geomcalc.py: module supporting "fio coords".
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

from collections import UserDict

import shapely
from shapely.geometry import shape

from . import snuggs


def vertex_count(obj) -> int:
    """ "Count the vertices of a GeoJSON-like geometry object.
    Parameters
    ----------
    obj: a GeoJSON-like mapping or an object that provides __geo_interface__

    Returns
    -------
    int

    """
    shp = shape(obj)
    if hasattr(shp, "geoms"):
        return sum(vertex_count(part) for part in shp.geoms)
    elif hasattr(shp, "exterior"):
        return vertex_count(shp.exterior) + sum(
            vertex_count(ring) for ring in shp.interiors
        )
    else:
        return len(shp.coords)


# Patch snuggs' func_map, extending it with Python builtins, geometry
# methods and attributes, and functions exported in the shapely module
# (such as set_precision).


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


func_map = dict(vertex_count=vertex_count)
snuggs.func_map = FuncMapper(func_map)


def calculate(expression, feature):
    try:
        geom = shape(feature.get("geometry", None))
    except (AttributeError, KeyError):
        geom = None
    return snuggs.eval(expression, g=geom, f=feature)
