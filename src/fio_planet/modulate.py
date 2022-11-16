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

from shapely.geometry import mapping, shape

# Import calculate to patch snuggs.
from . import calculate  # noqa: F401
from . import snuggs


def modulate(pipeline, feature):
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
    pipeline : string
        Geometry operation pipeline such as
        "(exterior (buffer g 2.0))".
    feature : Feature
        A Fiona feature object.

    Returns
    -------
    Feature
        A copy of the input feature, with a modulated geometry.

    """

    # Set up the expression evaluation context. We might extend this
    # using something like timeit's "--setup" statements, allowing a
    # user to define clip geometries, other things.
    try:
        geom = shape(feature.get("geometry", None))
    except (AttributeError, KeyError):
        geom = None
    new_geom = snuggs.eval(pipeline, g=geom, f=feature)
    new_feat = copy(feature)
    new_feat["geometry"] = mapping(new_geom)
    return new_feat


def reduce(pipeline, features, raw=False):
    """Reduce a collection of features to a single value by applying a
    pipeline of transformations.

    The pipeline is a string which, when evaluated by snuggs, produces
    a new value. The name of the input feature collection in the
    context of the pipeline is "c".

    By default, the new value will become the geometry property of a
    new feature object. If raw is True, the new value will be returned
    as-is.

    Parameters
    ----------
    pipeline : string
        Geometry operation pipeline such as "(unary_union c)".
    features : iterable
        A sequence of Fiona feature objects.
    raw : bool (optional, default: False)
        If True, results will not be wrapped in a Feature.

    Returns
    -------
    Feature or obj
        A new Fiona feature object (the default) carrying the reduced
        value as its geometry, or the reduced value itself.

    """
    collection = (shape(feat["geometry"]) for feat in features)
    result = snuggs.eval(pipeline, c=collection)
    if raw:
        return result
    else:
        return {"type": "Feature", "properties": {}, "geometry": mapping(result), "id": "0"}
