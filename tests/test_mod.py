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
from shapely.geometry import MultiPoint, Point, mapping

from fio_planet.calculate import calculate, vertex_count
from fio_planet.modulate import modulate, reduce


def test_modulate_simple():
    """Set a feature's geometry."""
    feat = modulate("(Point 0 0)", {"type": "Feature"})
    assert "Feature" == feat["type"]
    assert "Point" == feat["geometry"]["type"]
    assert (0.0, 0.0) == feat["geometry"]["coordinates"]


def test_modulate_complex():
    """Exercise a fairly complicated pipeline."""
    bufkwd = "resolution" if shapely.__version__.startswith("1") else "quad_segs"

    with open("tests/data/trio.geojson") as src:
        collection = json.loads(src.read())

    feat = collection["features"][0]
    new_feat = modulate(
        f"(simplify (buffer g (* 0.1 2) :{bufkwd} (- 4 3)) 0.001 :preserve_topology false)",
        feat,
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
    assert count == calculate("(vertex_count g)", feat)


def test_calculate_builtin():
    """Confirm builtin function evaluation."""
    assert 42 == calculate("(int '42')", None)


def test_calculate_feature_attr():
    """Confirm feature attr evaluation."""
    assert "LOLWUT" == calculate("(upper f)", "lolwut")


def test_reduce_len():
    """Reduce can count the number of input features."""
    with open("tests/data/trio.seq") as seq:
        data = [json.loads(line) for line in seq.readlines()]

    assert 3 == reduce("(len c)", data, raw=True)


def test_reduce_union():
    """Reduce yields one feature by default."""
    with open("tests/data/trio.seq") as seq:
        data = [json.loads(line) for line in seq.readlines()]

    result = reduce("(unary_union c)", data)
    assert "Feature" == result["type"]
    assert "GeometryCollection" == result["geometry"]["type"]
    assert 2 == len(result["geometry"]["geometries"])


def test_reduce_union_area():
    """Reduce can yield total area using raw output."""
    with open("tests/data/trio.seq") as seq:
        data = [json.loads(line) for line in seq.readlines()]

    result = reduce("(area (unary_union c))", data, raw=True)
    assert isinstance(result, float)
    assert 0 < result < 1e-5
