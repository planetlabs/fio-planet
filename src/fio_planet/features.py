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
from typing import Generator, Iterable, Mapping, Union

from fiona.transform import transform_geom  # type: ignore
import shapely  # type: ignore
from shapely.geometry import mapping, shape  # type: ignore
from shapely.geometry.base import BaseGeometry, BaseMultipartGeometry  # type: ignore

from .errors import ReduceError
from . import snuggs

# Patch snuggs's func_map, extending it with Python builtins, geometry
# methods and attributes, and functions exported in the shapely module
# (such as set_precision).


class FuncMapper(UserDict, Mapping):
    """Resolves functions from names in pipeline expressions."""

    def __getitem__(self, key):
        """Get a function by its name."""
        if key in self.data:
            return self.data[key]
        elif key in __builtins__ and not key.startswith("__"):
            return __builtins__[key]
        elif key in dir(shapely):
            return lambda g, *args, **kwargs: getattr(shapely, key)(g, *args, **kwargs)
        else:
            return (
                lambda g, *args, **kwargs: getattr(g, key)(*args, **kwargs)
                if callable(getattr(g, key))
                else getattr(g, key)
            )


def area(geom: Union[BaseGeometry, BaseMultipartGeometry], projected=True) -> float:
    """The cartesian or projected area of a geometry.

    If reproject is True (the default), the input geometry will be
    reprojected to the EASE grid system before computing its area and
    the value will have units of m**2. Otherwise a unitless Cartesian
    area will be returned.

    Parameters
    ----------
    geom : a shapely geometry object
    projected : bool, optional (default: True)
        If True, reproject to EASE grid system with units of m**2. Else
        return a unitless Cartesian area.

    Returns
    -------
    float

    Notes
    -----
    This function shadows Shapely's area().

    """
    if projected:
        geom = shape(transform_geom("OGC:CRS84", "EPSG:6933", mapping(geom)))

    return geom.area


def buffer(
    geom: Union[BaseGeometry, BaseMultipartGeometry],
    distance: float,
    projected=True,
    **kwargs,
) -> Union[BaseGeometry, BaseMultipartGeometry]:
    """The cartesian or projected distance buffer of a geometry.

    If reproject is True (the default), the input geometry will be
    reprojected to the EASE grid system before computing its buffer and
    the distance and mitre_limit values will have units of meters.
    Otherwise unitless Cartesian values will be assumed.

    Parameters
    ----------
    geom : a shapely geometry object
    distance : float
        If projected is True, the units are meters.
    projected : bool, optional (default: True)
        If True, reproject to EASE grid system.
    kwargs : dict
        The other keyword arguments of shapely.buffer().

    Returns
    -------
    A new Shapely geometry object

    Notes
    -----
    This function shadows Shapely's buffer().

    """
    if projected:
        geom = shape(transform_geom("OGC:CRS84", "EPSG:6933", mapping(geom)))

    return geom.buffer(distance, **kwargs)


def collect(geoms: Iterable) -> object:
    """Turn a sequence of geometries into a single GeometryCollection.

    Parameters
    ----------
    geoms : Iterable
        A sequence of geometry objects.

    Returns
    -------
    Geometry

    """
    return shapely.GeometryCollection(list(geoms))


def distance(
    geom1: Union[BaseGeometry, BaseMultipartGeometry],
    geom2: Union[BaseGeometry, BaseMultipartGeometry],
    projected=True,
) -> float:
    """The cartesian or projected distance between two geometries.

    If reproject is True (the default), the input geometries will be
    reprojected to the EASE grid system before computing distance and
    the value will have units of meters. Otherwise a unitless Cartesian
    distance will be returned.

    Parameters
    ----------
    geom1 : a shapely geometry object
    geom2 : a shapely geometry object
    projected : bool, optional (default: True)
        If True, reproject to EASE grid system with units of m**2. Else
        return a unitless Cartesian area.

    Returns
    -------
    float

    Notes
    -----
    This function shadows Shapely's distance().

    """
    if projected:
        geom1 = shape(transform_geom("OGC:CRS84", "EPSG:6933", mapping(geom1)))
        geom2 = shape(transform_geom("OGC:CRS84", "EPSG:6933", mapping(geom2)))

    return geom1.distance(geom2)


def dump(geom: Union[BaseGeometry, BaseMultipartGeometry]) -> Generator:
    """Get the individual parts of a geometry object.

    If the given geometry object has a single part, e.g., is an
    instance of LineString, Point, or Polygon, this function yields a
    single result, the geometry itself.

    Parameters
    ----------
    geom : a shapely geometry object.

    Yields
    ------
    A shapely geometry object.

    """
    if hasattr(geom, "geoms"):
        parts = geom.geoms
    else:
        parts = [geom]
    for part in parts:
        yield part


def identity(obj: object) -> object:
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


def length(geom: Union[BaseGeometry, BaseMultipartGeometry], projected=True) -> float:
    """The cartesian or projected length of a geometry.

    If reproject is True (the default), the input geometry will be
    reprojected to the EASE grid system before computing its length and
    the value will have units of meters. Otherwise a unitless Cartesian
    length will be returned.

    Parameters
    ----------
    geom : a shapely geometry object
    projected : bool, optional (default: True)
        If True, reproject to EASE grid system and give a length with
        units of meters. Else return a unitless length.

    Returns
    -------
    float

    Notes
    -----
    This function shadows Shapely's length().

    """
    if projected:
        geom = shape(transform_geom("OGC:CRS84", "EPSG:6933", mapping(geom)))

    return geom.length


def vertex_count(obj: object) -> int:
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


snuggs.func_map = FuncMapper(
    area=area,
    buffer=buffer,
    collect=collect,
    distance=distance,
    dump=dump,
    identity=identity,
    length=length,
    vertex_count=vertex_count,
    **{
        k: getattr(itertools, k)
        for k in dir(itertools)
        if not k.startswith("_") and callable(getattr(itertools, k))
    },
)


def map_feature(
    expression: str, feature: Mapping, dump_parts: bool = False
) -> Generator:
    """Map a pipeline expression to a feature.

    Yields one or more values.

    Parameters
    ----------
    expression : str
        A snuggs expression. The outermost parentheses are optional.
    feature : dict
        A Fiona feature object.
    dump_parts : bool, optional (default: False)
        If True, the parts of the feature's geometry are turned into
        new features.

    Yields
    ------
    object

    """
    if not (expression.startswith("(") and expression.endswith(")")):
        expression = f"({expression})"

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
        if isinstance(result, (str, float, int, Mapping)):
            yield result
        elif isinstance(result, (BaseGeometry, BaseMultipartGeometry)):
            yield mapping(result)
        else:
            try:
                for item in result:
                    if isinstance(item, (BaseGeometry, BaseMultipartGeometry)):
                        item = mapping(item)
                    yield item
            except TypeError:
                yield result


def reduce_features(expression: str, features: Iterable[Mapping]) -> Generator:
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

    Raises
    ------
    ReduceError

    """
    if not (expression.startswith("(") and expression.endswith(")")):
        expression = f"({expression})"

    collection = (shape(feat["geometry"]) for feat in features)
    result = snuggs.eval(expression, c=collection)

    if isinstance(result, (str, float, int, Mapping)):
        yield result
    elif isinstance(result, (BaseGeometry, BaseMultipartGeometry)):
        yield mapping(result)
    else:
        raise ReduceError("Expression failed to reduce to a single value.")
