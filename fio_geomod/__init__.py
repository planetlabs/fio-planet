# fio_geomod
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

__version__ = "1.0dev"


def modulate(feature, pipeline):
    """Modulate the geometry of a feature by applying a pipeline of
    transformations.

    The pipeline is a string which, when evaluated by fio-geomod,
    produces a new geometry object. The syntax is essentially a Python
    expression beginning with an optional "g.", where g is a Shapely
    geometry object constructed from the feature's GeoJSON geometry.

    Parameters
    ----------
    feature : Feature
        A Fiona feature.
    pipeline : string
        Geometry operation pipeline such as "buffer(2.0).exterior".

    Returns
    -------
    Feature
        A copy of the input feature, with a modulated geometry.

    """
    # The "g." is optional.
    pipeline = pipeline.lstrip("g.")

    # Set up the expression evaluation context. We might extend this
    # using something like timeit's "--setup" statements, allowing a
    # user to define clip geometries, other things.
    geom = shape(feature["geometry"])
    localvars = {"g": geom}

    exec(f"new_geom = g.{pipeline}", {}, localvars)

    new_feat = copy(feature)
    new_feat["geometry"] = mapping(localvars["new_geom"])
    return new_feat
