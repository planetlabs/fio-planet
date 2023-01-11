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

"""Operations on GeoJSON feature and geometry objects."""

from collections import UserDict
import itertools
from typing import Generator, Iterable, Mapping

import shapely
from shapely.geometry import mapping, shape
from shapely.geometry.base import BaseGeometry, BaseMultipartGeometry

from . import snuggs


def vertex_count(obj) -> int:
    """Count the vertices of a GeoJSON-like geometry object.

    Parameters
    ----------
    obj: object
        A GeoJSON-like mapping or an object that provides
        __geo_interface__.

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
    """Resolves functions from names in pipeline expressions."""

    def __getitem__(self, key):
        """Get a function by its name."""
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


def dump(shp) -> Generator:
    """Get the individual parts of a geometry object.

    If the given geometry object has a single part, e.g., is an
    instance of LineString, Point, or Polygon, this function yields a
    single result, the geometry itself.

    Parameters
    ----------
    shp : object
        A shapely geometry object.

    Yields
    ------
    A shapely geometry object.

    """
    if hasattr(shp, "geoms"):
        parts = shp.geoms
    else:
        parts = [shp]
    for part in parts:
        yield part


def identity(obj):
    """Get back the given argument.

    To help in making expression lists, where the first item must be a
    callable object.

    Parameters
    ----------
    obj : objeect


    Returns
    -------
    obj

    """
    return obj


snuggs.func_map = FuncMapper(
    dump=dump,
    identity=identity,
    vertex_count=vertex_count,
    **{
        k: getattr(itertools, k)
        for k in dir(itertools)
        if not k.startswith("_") and callable(getattr(itertools, k))
    }
)


def map_feature(expression: str, feature: dict, dump_parts: bool = False) -> Generator:
    """Map a pipeline expression to a feature.

    Yields one or more values.

    Yields
    ------
    object

    """
    try:
        geom = shape(feature.get("geometry", None))
        if dump_parts and hasattr(geom, "geoms"):
            parts = geom.geoms
        else:
            parts = [geom]
    except (AttributeError, KeyError):
        parts = [None]

    for part in parts:
        result = snuggs.eval(expression, g=part, f=feature)
        if isinstance(result, str):
            yield result
        else:
            try:
                for item in result:
                    if isinstance(item, (BaseGeometry, BaseMultipartGeometry)):
                        item = mapping(item)
                    yield item
            except TypeError:
                if isinstance(result, (BaseGeometry, BaseMultipartGeometry)):
                    result = mapping(result)
                yield result


def reduce_features(pipeline: str, features: Iterable[Mapping]) -> Generator:
    """Reduce a collection of features to a single value.

    The pipeline is a string which, when evaluated by snuggs, produces
    a new value. The name of the input feature collection in the
    context of the pipeline is "c".

    Parameters
    ----------
    pipeline : str
        Geometry operation pipeline such as "(unary_union c)".
    features : iterable
        A sequence of Fiona feature objects.

    Yields
    ------
    object

    """
    collection = (shape(feat["geometry"]) for feat in features)
    result = snuggs.eval(pipeline, c=collection)
    if isinstance(result, str):
        yield result
    else:
        try:
            for item in result:
                if isinstance(item, (BaseGeometry, BaseMultipartGeometry)):
                    item = mapping(item)
                yield item
        except TypeError:
            if isinstance(result, (BaseGeometry, BaseMultipartGeometry)):
                result = mapping(result)
            yield result
