from codecs import open as codecs_open
from setuptools import setup, find_packages


# Get the long description from the relevant file
with codecs_open("README.rst", encoding="utf-8") as f:
    long_description = f.read()


setup(
    name="fio-geomod",
    version="1.0.0",
    description=u"Modulate geometries of GeoJSON features",
    long_description=long_description,
    classifiers=[],
    keywords="",
    author=u"Sean Gillies",
    author_email="sean.gillies@planet.com",
    # url=TBD,
    license="MIT",
    packages=find_packages(exclude=["ez_setup", "examples", "tests"]),
    include_package_data=True,
    zip_safe=False,
    install_requires=["click", "cligj", "fiona", "shapely"],
    extras_require={
        "test": ["pytest"],
    },
    entry_points="""
      [fiona.fio_commands]
      geomod=fio_geomod.scripts.cli:geomod
      """,
)
