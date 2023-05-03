import pytest

from fio_planet import snuggs


@pytest.fixture(autouse=True)
def add_snuggs(doctest_namespace):
    doctest_namespace["snuggs"] = snuggs
