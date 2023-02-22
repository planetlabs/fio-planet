fio-planet
==========

A package of Fiona CLI plugin commands from Planet Labs.

.. image:: https://github.com/planetlabs/fio-planet/actions/workflows/check.yml/badge.svg
   :target: https://github.com/planetlabs/fio-planet/actions/workflows/check.yml

.. image:: https://github.com/planetlabs/fio-planet/actions/workflows/test.yml/badge.svg
   :target: https://github.com/planetlabs/fio-planet/actions/workflows/test.yml

These commands are for creating Unix pipelines which manipulate streams of
GeoJSON features. Such pipelines provide a subset of the functionality of more
complicated tools such as PostGIS or GeoPandas and are intended for use with
streams of hundreds to thousands of features, where the overhead of JSON
serialization between pieces of a pipeline is tolerable.

Installation
------------

.. code-block::

   python -m pip install --user fio-planet@https://github.com/planetlabs/fio-planet.git

Usage
-----

fio-planet adds ``filter``, ``map``, and ``reduce`` commands to Fiona's ``fio``
program. fio-filter evaluates an expression for each feature in a stream of
GeoJSON features, passing those for which the expression is true. fio-map maps
an expression over a stream of GeoJSON features, producing a stream of new
features or other values. fio-reduce applies an expression to a sequence of
GeoJSON features, reducing them to a single feature or other value.

These commands provide some of the features of spatial SQL, but act on
features in a GeoJSON feature sequence instead of rows in a spatial table.
fio-filter decimates a seqence of features, fio-map multiplies features, and
fio-reduce turns a sequence of many features into a sequence of exactly one.
In combination, many transformations are possible.

Expressions take the form of parenthesized lists which may contain other
expressions. The first item in a list is the name of a function or method, or
an expression that evaluates to a function. The second item is the function's
first argument or the object to which the method is bound. The remaining list
items are the positional and keyword arguments for the named function or
method. The list of functions and callables available in expressions includes:

* Python builtins such as ``dict``, ``list``, and ``map``
* From functools: ``reduce``.
* All public functions from itertools, e.g., ``islice``, and ``repeat``
* All functions importable from Shapely 2.0, e.g., ``Point``, and
  ``unary_union``
* All methods of Shapely geometry classes.

Here's an expression that evaluates to a Shapely Point instance. ``Point`` is a
callable instance constructor and the pair of ``0`` values are positional
arguments. Note that the outermost parentheses of an expression are optional.

.. code-block:: lisp

    (Point 0 0)

Here's an expression that evaluates to a Polygon, using ``buffer``. The inner
expression ``(Point 0 0)`` evaluates to a Shapely Point instance, ``buffer``
evaluates to its instance method, and ``:distance 1.0`` assigns a value of 1.0
to that method's ``distance`` keyword argument.

.. code-block:: lisp

    buffer (Point 0 0) :distance 1.0

fio-filter and fio-map evaluate expressions in the context of a GeoJSON feature
and its geometry attribute. These are named ``f`` and ``g``. For example, here
is an expression that tests whether the input feature is within a distance
``1.0`` of a given point.

.. code-block:: lisp

    <= (distance g (Point 0 0)) 1.0

fio-reduce evaluates expressions in the context of the sequence of all input
geometries, which is named ``c``. For example, this expression dissolves input
geometries using Shapely's ``unary_union``.

.. code-block:: lisp

    unary_union c

fio-filter
----------

For each feature read from stdin, fio-filter evaluates a pipeline of one or
more steps described using methods from the Shapely library in Lisp-like
expressions. If the pipeline expression evaluates to True, the feature passes
through the filter. Otherwise the feature does not pass.

For example, this pipeline expression

.. code-block::

    $ fio cat zip+https://s3.amazonaws.com/fiona-testing/coutwildrnp.zip \
    | fio filter '< (distance g (Point -109.0 38.5)) 1'

lets through all features that are less than one unit from the given point and
filters out all other features.

fio-map
-------

For each feature read from stdin, fio-map applies a transformation pipeline and
writes a copy of the feature, containing the modified geometry, to stdout. For
example, polygonal features can be "cleaned" by using a ``buffer g 0``
pipeline.

.. code-block::

    $ fio cat zip+https://s3.amazonaws.com/fiona-testing/coutwildrnp.zip \
    | fio map 'buffer g 0'

fio-reduce
----------

Given a sequence of GeoJSON features (RS-delimited or not) on stdin this prints
a single value using a provided transformation pipeline.  The set of geometries
of the input features in the context of these expressions is named "c".

For example, the pipeline expression

.. code-block::

    $ fio cat zip+https://s3.amazonaws.com/fiona-testing/coutwildrnp.zip \
    | fio reduce 'unary_union c'

dissolves the geometries of input features.

Support
-------

For usage help, please use the project discussion forum or email
developers@planet.com.

If you think you've found a bug, please use the project issue tracker.

Roadmap
-------

Version 1.0 adds ``filter``, ``map``, and ``reduce`` to Fiona's ``fio`` CLI.

Note that there are no conditional forms in 1.0's expressions. The project will
likely add a ``cond`` after 1.0.

Contributing
------------

Before 1.0, the project is looking for feedback on the existing commands more
than it is looking for new commands.

The project uses ``black``, ``flake8``, ``mypy``, and ``tox`` for static checks
and testing.

.. code-block::

    $ black src tests && flake8 && mypy && tox

Authors and acknowledgment
--------------------------

Contributors to this project are

* Sean Gillies <sean.gillies@planet.com>

License
-------

Apache License, Version 2.0.
