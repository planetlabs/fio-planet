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

from fiona.fio.main import main_group


def test_geomod_count():
    """fio-geomod prints correct number of results."""
    with open("tests/data/trio.seq") as seq:
        data = seq.read()

    runner = CliRunner()
    result = runner.invoke(
        main_group, ["geomod", "(centroid (buffer g 1.0))"], input=data
    )
    assert result.exit_code == 0
    assert result.output.count('"type": "Point"') == 3


def test_reduce_area():
    """Reduce features to their (raw) area."""
    with open("tests/data/trio.seq") as seq:
        data = seq.read()

    runner = CliRunner()
    result = runner.invoke(
        main_group, ["reduce", "--raw", "(area (unary_union c))"], input=data
    )
    assert result.exit_code == 0
    assert 0 < float(result.output) < 1e-5


def test_reduce_union():
    """Reduce features to one single feature."""
    with open("tests/data/trio.seq") as seq:
        data = seq.read()

    runner = CliRunner()
    result = runner.invoke(main_group, ["reduce", "(unary_union c)"], input=data)
    assert result.exit_code == 0
    assert result.output.count('"type": "Polygon"') == 1
    assert result.output.count('"type": "LineString"') == 1
    assert result.output.count('"type": "GeometryCollection"') == 1
