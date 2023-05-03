# CLI tests
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

from click.testing import CliRunner

from fiona.fio.main import main_group  # type: ignore
import pytest  # type: ignore


def test_map_count():
    """fio-map prints correct number of results."""
    with open("tests/data/trio.seq") as seq:
        data = seq.read()

    # Define our map arg using a mkdocs snippet.
    arg = """
    --8<-- [start:map]
    centroid (buffer g 1.0)
    --8<-- [end:map]
    """.splitlines()[
        2
    ].strip()

    runner = CliRunner()
    result = runner.invoke(
        main_group,
        ["map", arg],  # "centroid (buffer g 1.0)"],
        input=data,
    )

    assert result.exit_code == 0
    assert result.output.count('"type": "Point"') == 3


@pytest.mark.parametrize("raw_opt", ["--raw", "-r"])
def test_reduce_area(raw_opt):
    """Reduce features to their (raw) area."""
    with open("tests/data/trio.seq") as seq:
        data = seq.read()

    runner = CliRunner()
    result = runner.invoke(
        main_group,
        ["reduce", raw_opt, "area (unary_union c) :projected false"],
        input=data,
    )
    assert result.exit_code == 0
    assert 0 < float(result.output) < 1e-5


def test_reduce_union():
    """Reduce features to one single feature."""
    with open("tests/data/trio.seq") as seq:
        data = seq.read()

    # Define our reduce command using a mkdocs snippet.
    arg = """
    --8<-- [start:reduce]
    unary_union c
    --8<-- [end:reduce]
    """.splitlines()[
        2
    ].strip()

    runner = CliRunner()
    result = runner.invoke(main_group, ["reduce", arg], input=data)
    assert result.exit_code == 0
    assert result.output.count('"type": "Polygon"') == 1
    assert result.output.count('"type": "LineString"') == 1
    assert result.output.count('"type": "GeometryCollection"') == 1


def test_reduce_union_zip_properties():
    """Reduce features to one single feature, zipping properties."""
    with open("tests/data/trio.seq") as seq:
        data = seq.read()

    runner = CliRunner()
    result = runner.invoke(
        main_group, ["reduce", "--zip-properties", "unary_union c"], input=data
    )
    assert result.exit_code == 0
    assert result.output.count('"type": "Polygon"') == 1
    assert result.output.count('"type": "LineString"') == 1
    assert result.output.count('"type": "GeometryCollection"') == 1
    assert (
        """"name": ["Le ch\\u00e2teau d\'eau", "promenade du Peyrou"]"""
        in result.output
    )


def test_filter():
    """Filter features by distance."""
    with open("tests/data/trio.seq") as seq:
        data = seq.read()

    # Define our reduce command using a mkdocs snippet.
    arg = """
    --8<-- [start:filter]
    < (distance g (Point 4 43)) 62.5E3
    --8<-- [end:filter]
    """.splitlines()[
        2
    ].strip()

    runner = CliRunner()
    result = runner.invoke(
        main_group,
        ["filter", arg],
        input=data,
        catch_exceptions=False,
    )
    assert result.exit_code == 0
    assert result.output.count('"type": "Polygon"') == 1


@pytest.mark.parametrize("opts", [["--no-input", "--raw"], ["-rn"]])
def test_map_no_input(opts):
    runner = CliRunner()
    result = runner.invoke(main_group, ["map"] + opts + ["(Point 4 43)"])
    assert result.exit_code == 0
    assert result.output.count('"type": "Point"') == 1
