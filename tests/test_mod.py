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

import pytest  # type: ignore
import shapely  # type: ignore
from shapely.geometry import MultiPoint, Point, mapping  # type: ignore

from fio_planet.errors import ReduceError
from fio_planet.features import (  # type: ignore
    map_feature,
    reduce_features,
    vertex_count,
    collect,
    dump,
    identity,
)


def test_modulate_simple():
    """Set a feature's geometry."""
    # map_feature() is a generator. list() materializes the values.
    feat = list(map_feature("Point 0 0", {"type": "Feature"}))
    assert len(feat) == 1

    feat = feat[0]
    assert "Point" == feat["type"]
    assert (0.0, 0.0) == feat["coordinates"]


def test_modulate_complex():
    """Exercise a fairly complicated pipeline."""
    bufkwd = "resolution" if shapely.__version__.startswith("1") else "quad_segs"

    with open("tests/data/trio.geojson") as src:
        collection = json.loads(src.read())

    feat = collection["features"][0]
    results = list(
        map_feature(
            f"simplify (buffer g (* 0.1 2) :{bufkwd} (- 4 3)) 0.001 :preserve_topology false",
            feat,
        )
    )
    assert 1 == len(results)

    geom = results[0]
    assert geom["type"] == "Polygon"
    assert len(geom["coordinates"][0]) == 5


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
    assert count == list(map_feature("vertex_count g", feat))[0]


def test_calculate_builtin():
    """Confirm builtin function evaluation."""
    assert 42 == list(map_feature("int '42'", None))[0]


def test_calculate_feature_attr():
    """Confirm feature attr evaluation."""
    assert "LOLWUT" == list(map_feature("upper f", "lolwut"))[0]


def test_calculate_point():
    """Confirm feature attr evaluation."""
    result = list(map_feature("Point 0 0", None))[0]
    assert "Point" == result["type"]


def test_calculate_points():
    """Confirm feature attr evaluation."""
    result = list(map_feature("list (Point 0 0) (buffer (Point 1 1) 1)", None))
    assert 2 == len(result)
    assert "Point" == result[0]["type"]
    assert "Polygon" == result[1]["type"]


def test_reduce_len():
    """Reduce can count the number of input features."""
    with open("tests/data/trio.seq") as seq:
        data = [json.loads(line) for line in seq.readlines()]

    # reduce() is a generator. list() materializes the values.
    assert 3 == list(reduce_features("len c", data))[0]


def test_reduce_union():
    """Reduce yields one feature by default."""
    with open("tests/data/trio.seq") as seq:
        data = [json.loads(line) for line in seq.readlines()]

    # reduce() is a generator. list() materializes the values.
    result = list(reduce_features("unary_union c", data))
    assert len(result) == 1

    val = result[0]
    assert "GeometryCollection" == val["type"]
    assert 2 == len(val["geometries"])


def test_reduce_union_area():
    """Reduce can yield total area using raw output."""
    with open("tests/data/trio.seq") as seq:
        data = [json.loads(line) for line in seq.readlines()]

    # reduce() is a generator.
    result = list(reduce_features("area (unary_union c)", data))
    assert len(result) == 1

    val = result[0]
    assert isinstance(val, float)
    assert 0 < val < 1e-5


def test_reduce_union_geom_type():
    """Reduce and print geom_type using raw output."""
    with open("tests/data/trio.seq") as seq:
        data = [json.loads(line) for line in seq.readlines()]

    # reduce() is a generator.
    result = list(reduce_features("geom_type (unary_union c)", data))
    assert len(result) == 1
    assert "GeometryCollection" == result[0]


def test_reduce_error():
    """Raise ReduceError when expression doesn't reduce."""
    with open("tests/data/trio.seq") as seq:
        data = [json.loads(line) for line in seq.readlines()]

    with pytest.raises(ReduceError):
        list(reduce_features("(identity c)", data))


@pytest.mark.parametrize(
    "obj, count",
    [
        (MultiPoint([(0, 0), (1, 1)]), 2),
    ],
)
def test_dump_eval(obj, count):
    feature = {"type": "Feature", "properties": {}, "geometry": mapping(obj)}
    result = map_feature("identity g", feature, dump_parts=True)
    assert len(list(result)) == count


def test_collect():
    """Collect two points."""
    geom = collect((Point(0, 0), Point(1, 1)))
    assert geom.type == "GeometryCollection"


def test_dump():
    """Dump a point."""
    geoms = list(dump(Point(0, 0)))
    assert len(geoms) == 1
    assert geoms[0].type == "Point"


def test_dump_multi():
    """Dump two points."""
    geoms = list(dump(MultiPoint([(0, 0), (1, 1)])))
    assert len(geoms) == 2
    assert all(g.type == "Point" for g in geoms)


def test_identity():
    """Check identity."""
    geom = Point(1.1, 2.2)
    assert geom == identity(geom)
