fio-geomod
==========

fio-geomod modulates the geometries of GeoJSON features.

Command line interface
----------------------

fio-geomod adds a "geomod" command to Fiona's "fio" program.

.. code-block:: console

    $ cat tests/data/trio.seq | fio geomod --operation concave_hull
