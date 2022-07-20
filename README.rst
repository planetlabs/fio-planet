fio-geomod
==========

fio-geomod modulates the geometries of GeoJSON features.

Command line interface
----------------------

fio-geomod adds a "geomod" command to Fiona's "fio" program.

.. code-block:: console

    fio cat tests/data/trio.geojson | fio geomod 'buffer(0.01).simplify(0.01).centroid'
    {"geometry": {"type": "Point", "coordinates": [3.869011402130127, 43.61140112858711]}, "id": "0", "properties": {...}, "type": "Feature"}
    {"geometry": {"type": "Point", "coordinates": [3.866082808514709, 43.611667519514526]}, "id": "1", "properties": {...}, "type": "Feature"}
    {"geometry": {"type": "Point", "coordinates": [3.8705445602623776, 43.61139894113176]}, "id": "2", "properties": {...}, "type": "Feature"}
