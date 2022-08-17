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

from fio_geomod import modulate


def test_modulate():
    """Exercise a fairly complicated pipeline."""
    with open("tests/data/trio.geojson") as src:
        collection = json.loads(src.read())

    feat = collection["features"][0]
    new_feat = modulate(
        feat,
        "(simplify (buffer g (* 0.1 2) :resolution (- 4 3)) 0.001 :preserve_topology false)",
    )
    assert new_feat["geometry"]["type"] == "Polygon"
    assert len(new_feat["geometry"]["coordinates"][0]) == 5
