fio-planet
==========

fio-planet is a package of Fiona CLI plugins from Planet Labs.

Installation
------------

.. code-block:: console

   $ pip install fio-planet@https://github.com/planetlabs/fio-planet.git

Command line interface
----------------------

fio-planet
==========

fio-planet adds a "geomod" command to Fiona's ``fio`` program. The geomod
command is a filter for streams of compact or ASCII RS-delimited GeoJSON
features. For each feature read from stdin, geomod applies a transformation
pipeline of one or more steps described using methods from the Shapely library
in Lisp-like expressions wherein the feature's geometry is named ``g``, and
writes a copy of the feature, containing the modified geometry, to stdout.  For
example, polygonal features can be "cleaned" by using a ``(buffer g 0)``
pipeline.

.. code-block:: console

    $ fio cat zip+https://s3.amazonaws.com/fiona-testing/coutwildrnp.zip | fio geomod '(buffer g 0)'

Or we can replace polygons with their centroids using ``centroid``.

.. code-block:: console

    $ fio cat zip+https://s3.amazonaws.com/fiona-testing/coutwildrnp.zip | fio geomod '(centroid g)'

Or we can dilate and erode polyons and find those centroids, and combine with
the program ``jq`` to weed out unwanted features and properties.

.. code-block:: console

    fio cat zip+https://s3.amazonaws.com/fiona-testing/coutwildrnp.zip \
      | jq -c 'select(.properties.STATE == "CO")' \
      | jq -c '.properties |= {NAME}' \
      | fio geomod '(centroid (buffer (buffer g 0.1) -0.1))' \
      | jq
    {
    "geometry": {
        "type": "Point",
        "coordinates": [
        -106.69864626902294,
        40.764477220414065
        ]
    },
    "id": "2",
    "properties": {
        "NAME": "Mount Zirkel Wilderness"
    },
    "type": "Feature"
    }
    {
    "geometry": {
        "type": "Point",
        "coordinates": [
        -105.95025891510426,
        40.728674082430274
        ]
    },
    "id": "4",
    "properties": {
        "NAME": "Rawah Wilderness"
    },
    "type": "Feature"
    }
    {
    "geometry": {
        "type": "Point",
        "coordinates": [
        -105.65903404201194,
        40.58395201365962
        ]
    },
    "id": "6",
    "properties": {
        "NAME": "Comanche Peak Wilderness"
    },
    "type": "Feature"
    }
    ...
