# Python module tests
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

import json

import pytest
import shapely
from shapely.geometry import LineString, MultiPoint, Point, mapping

from fio_planet.calculate import calculate, vertex_count
from fio_planet.modulate import modulate


def test_modulate_simple():
    """Set a feature's geometry."""
    feat = modulate({"type": "Feature"}, "(Point 0 0)")
    assert "Feature" == feat["type"]
    assert "Point" == feat["geometry"]["type"]
    assert (0.0, 0.0) == feat["geometry"]["coordinates"]


def test_modulate_complex():
    """Exercise a fairly complicated pipeline."""
    bufkwd = "resolution" if shapely.__version__.startswith("1") else "quadsegs"

    with open("tests/data/trio.geojson") as src:
        collection = json.loads(src.read())

    feat = collection["features"][0]
    new_feat = modulate(
        feat,
        f"(simplify (buffer g (* 0.1 2) :{bufkwd} (- 4 3)) 0.001 :preserve_topology false)",
    )
    assert new_feat["geometry"]["type"] == "Polygon"
    assert len(new_feat["geometry"]["coordinates"][0]) == 5


@pytest.mark.parametrize(
    "obj, count",
    [
        (Point(0, 0), 1),
        (MultiPoint([(0, 0), (1, 1)]), 2),
        (Point(0, 0).buffer(10.0).difference(Point(0, 0).buffer(1.0)), 130),
    ],
)
def test_vertex_count(obj, count):
    """Check vertex counting correctness."""
    assert count == vertex_count(obj)


@pytest.mark.parametrize(
    "obj, count",
    [
        (Point(0, 0), 1),
        (MultiPoint([(0, 0), (1, 1)]), 2),
        (Point(0, 0).buffer(10.0).difference(Point(0, 0).buffer(1.0)), 130),
    ],
)
def test_calculate_vertex_count(obj, count):
    """Confirm vertex counting is in func_map."""
    feat = {"type": "Feature", "properties": {}, "geometry": mapping(obj)}
    assert count == calculate(feat, "(vertex_count g)")


def test_calculate_builtin():
    """Confirm builtin function evaluation."""
    assert 42 == calculate(None, "(int '42')")


def test_calculate_feature_attr():
    """Confirm feature attr evaluation."""
    assert "LOLWUT" == calculate("lolwut", "(upper f)")
