Simplifying shapes
==================

Here are a few examples related to the Planet Developers Blog deep dive into
`simplifying areas of interest
<https://developers.planet.com/blog/2022/Dec/15/simplifying-your-complex-area-of-interest-a-planet-developers-deep-dive/>`__.
The examples use a 25-feature shapefile. You can get it from `rmnp.zip
<https://github.com/planetlabs/fio-geomod/files/10045442/rmnp.zip>`__.

Counting vertices in a feature collection
-----------------------------------------

The builtin ``vertex_count`` function, in conjunction with fio-map's ``--raw``
option, prints out the number of vertices in each feature. The default for
fio-map is to wrap the result of every evaluated expression in a GeoJSON
feature; ``--raw`` disables this. The program jq provides a nice way of summing
the sequence of numbers.

.. code-block::

    fio cat Wilderness_Patrol_Zones.shp \
    | fio map 'vertex_count g' --raw \
    | jq -s 'add'
    28915

Here's what the RMNP wilderness patrol zones features look like in QGIS.

.. image:: https://user-images.githubusercontent.com/33697/202820493-2cae58f4-a968-4078-8a60-ba7e2cbe0434.png
   :width: 600

Counting vertices after making a simplified buffer
--------------------------------------------------

One traditional way of simplifying an area of interest is to buffer and
simplify. There's no need to use jq here because fio-reduce prints out a
sequence of exactly one feature. The effectiveness of this method depends a bit
on the nature of the data, especially the distance between vertices.

.. code-block::

    fio cat Wilderness_Patrol_Zones.shp \
    | fio reduce 'unary_union c' \
    | fio map 'simplify (buffer g 0.001) 0.001' \
    | fio map 'vertex_count g' --raw
    274

.. image:: https://user-images.githubusercontent.com/33697/202821086-5bfd4437-3c42-420e-84cf-d3e1287d2d8c.png
   :width: 600

Counting vertices after dissolving convex hulls of features
-----------------------------------------------------------

Convex hulls are an easy means of simplification. There are no distance
parameters to tweak. The ``--dump-parts`` option of fio-map turns the parts of
multi-part features into separate single-part features. This is one of the ways
in which fio-map can multiply its inputs, printing out more features than it
receives.

.. code-block::

    fio cat Wilderness_Patrol_Zones.shp \
    | fio map 'convex_hull g' --dump-parts \
    | fio reduce 'unary_union c' \
    | fio map 'vertex_count g' --raw
    157

.. image:: https://user-images.githubusercontent.com/33697/202820595-491c590c-0f5a-4cdb-89de-7cd2067cbf90.png
   :width: 600

Counting vertices after dissolving concave hulls of features
------------------------------------------------------------

Convex hulls simplify, but also dilate concave areas of interest. This can be
undesirable. Concave hulls inflate your areas less.

.. code-block::

    fio cat Wilderness_Patrol_Zones.shp \
    | fio map 'concave_hull g 0.4' --dump-parts \
    | fio reduce 'unary_union c' \
    | fio map 'vertex_count g' --raw
    301

.. image:: https://user-images.githubusercontent.com/33697/218189621-446b743e-daba-4e3c-bc24-7ce74771fb8a.png
   :width: 600
