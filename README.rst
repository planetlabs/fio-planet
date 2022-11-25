fio-planet
==========

fio-planet is a package of Fiona CLI plugins from Planet Labs.

Installation
------------

.. code-block:: console

   $ python -m pip install fio-planet@https://github.com/planetlabs/fio-planet.git

Command line interface
----------------------

fio-planet
==========

fio-planet adds ``filter``, ``map``, and ```reduce`` commands to Fiona's
``fio`` program. fio-filter evaluates an expression for each feature in
a stream of GeoJSON features, passing those for which the expression is true.
fio-map maps an expression over a stream of GeoJSON features, producing
a stream of new features or other values. fio-reduce applies an expression to
a sequence of GeoJSON features, reducing them to a single feature or other
value.

Expressions take the form of parenthesized lists which may contain other
expressions. The first item in a list is the name of a function or method, or
an expression that evaluates to a function. The second item is the function's
first argument or the object to which the method is bound. The remaining list
items are the positional and keyword arguments for the named function or
method. The list of functions and callables available in expressions includes:

* Python builtins such as ``dict``, ``list``, and ``map``
* From functools ``attrgetter``, ``itemgetter``, ``methodcaller``, and
  ``reduce``
* All public functions from itertools, e.g., ``islice``, and ``repeat``
* All functions importable from Shapely 2.0, e.g., ``Point``, and
  ``unary_union``
* All methods of Shapely geometry classes.

Here's an expression that evaluates to a Shapely Point instance. ``Point`` is
a callable instance constructor and the pair of ``0`` values are positional
arguments.

.. code-block:: lisp

    (Point 0 0)

Here's an expression that evaluates to a Polygon, using ``buffer``. The inner
expression ``(Point 0 0)`` evaluates to a Shapely Point instance, ``buffer``
evaluates to its instance method, and ``:distance 1.0`` assigns a value of 1.0
to that method's ``distance`` keyword argument.

.. code-block:: lisp

    (buffer (Point 0 0) :distance 1.0)

fio-filter and fio-map evaluate expressions in the context of a GeoJSON feature
and its geometry attribute. These are named ``f`` and ``g``. For example, here
is an expression that tests whether the input feature is within a distance
``1.0`` of a given point.

.. code-block:: lisp

    (<= (distance g (Point 0 0)) 1.0)

fio-reduce evaluates expressions in the context of the sequence of all input
geometries, which is named ``c``. For example, this expression dissolves input
geometries using Shapely's ``unary_union``.

.. code-block:: lisp

    (unary_union c)

fio-map
-------

For each feature read from stdin, fio-map applies a transformation pipeline of
one or more steps described using methods from the Shapely library in Lisp-like
expressions and writes a copy of the feature, containing the modified geometry,
to stdout. For example, polygonal features can be "cleaned" by using
a ``(buffer g 0)`` pipeline.

.. code-block:: console

    $ fio cat zip+https://s3.amazonaws.com/fiona-testing/coutwildrnp.zip \
    | fio map '(buffer g 0)'

Or we can replace polygons with their centroids using ``centroid``.

.. code-block:: console

    $ fio cat zip+https://s3.amazonaws.com/fiona-testing/coutwildrnp.zip \
    | fio map '(centroid g)'

Or we can dilate and erode polyons and find those centroids, and combine with
the program ``jq`` to weed out unwanted features and properties.

.. code-block:: console

    fio cat zip+https://s3.amazonaws.com/fiona-testing/coutwildrnp.zip \
      | jq -c 'select(.properties.STATE == "CO")' \
      | jq -c '.properties |= {NAME}' \
      | fio map '(centroid (buffer (buffer g 0.1) -0.1))' \
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

