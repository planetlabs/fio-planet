# Python module tests
#
# Copyright 2023 Planet Labs PBC
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

"""Tests of the snuggs module."""

import pytest

from fio_planet import snuggs


@pytest.mark.parametrize("arg", ["''", "null", "false", 0])
def test_truth_false(arg):
    """Expression is not true."""
    assert not snuggs.eval(f"(truth {arg})")


@pytest.mark.parametrize("arg", ["'hi'", "true", 1])
def test_truth(arg):
    """Expression is true."""
    assert snuggs.eval(f"(truth {arg})")


@pytest.mark.parametrize("arg", ["''", "null", "false", 0])
def test_not(arg):
    """Expression is true."""
    assert snuggs.eval(f"(not {arg})")
