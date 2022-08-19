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
from . import snuggs

__version__ = "1.0dev"


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
    localvars = {"g": geom}

    # TODO: add more shapely methods.
    snuggs.func_map["area"] = lambda g: g.area
    snuggs.func_map["buffer"] = lambda g, *args, **kwargs: g.buffer(*args, **kwargs)
    snuggs.func_map["centroid"] = lambda g: g.centroid
    snuggs.func_map["simplify"] = lambda g, *args, **kwargs: g.simplify(*args, **kwargs)
    new_geom = snuggs.eval(pipeline, g=geom)

    new_feat = copy(feature)
    new_feat["geometry"] = mapping(new_geom)
    return new_feat
