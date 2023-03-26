fio-planet
==========

A package of Fiona CLI plugins from Planet Labs.

[![](https://github.com/planetlabs/fio-planet/actions/workflows/check.yml/badge.svg)](https://github.com/planetlabs/fio-planet/actions/workflows/check.yml)
[![](https://github.com/planetlabs/fio-planet/actions/workflows/test.yml/badge.svg)](https://github.com/planetlabs/fio-planet/actions/workflows/test.yml)

These CLI commands are for creating Unix pipelines which manipulate streams of
GeoJSON features. Such pipelines provide a subset of the functionality of more
complicated tools such as GeoPandas, PostGIS, or QGIS, and are intended for use
with streams — not rivers — of hundreds of features, where the overhead of JSON
serialization between pieces of a pipeline is tolerable.

Installation
------------

```
python -m pip install --user --pre fio-planet
```

Usage
-----

fio-planet adds `filter`, `map`, and `reduce` commands to Fiona's `fio`
program. These commands afford some of the capabilities of spatial SQL, but act
on features of a GeoJSON feature sequence instead of rows of a spatial RDBMS
table.  fio-filter decimates a seqence of features, fio-map multiplies and
transforms features, and fio-reduce turns a sequence of many features into a
sequence of exactly one.  In combination, many transformations are possible.

Expressions take the form of parenthesized lists which may contain other
expressions. The first item in a list is the name of a function or method, or
an expression that evaluates to a function. The second item is the function's
first argument or the object to which the method is bound. The remaining list
items are the positional and keyword arguments for the named function or
method. The list of functions and callables available in an expression
includes:

* Python builtins such as `dict`, `list`, and `map`
* From functools: `reduce`.
* All public functions from itertools, e.g. `islice`, and `repeat`
* All functions importable from Shapely 2.0, e.g. `Point`, and
  `unary_union`
* All methods of Shapely geometry classes.

Here's an expression that evaluates to a Shapely Point instance.

```lisp
(Point 0 0)
```

`Point` is a callable instance constructor and the pair of `0` values are
positional arguments. Note that the outermost parentheses of an expression are
optional.

Here's an expression that evaluates to a Polygon, using `buffer`.

```lisp
buffer (Point 0 0) :distance 1.0
```

The inner expression `(Point 0 0)` evaluates to a Shapely Point instance,
`buffer` evaluates to `shapely.buffer()`, and `:distance 1.0` assigns a value
of 1.0 to that method's `distance` keyword argument.

In a fio-planet expression, all coordinates and geometry objects are in the
`OGC:CRS84` reference system, like GeoJSON. However, function arguments related
to length or area, such as buffer's distance argument, are understood to have
units of meters.

fio-filter and fio-map evaluate expressions in the context of a GeoJSON feature
and its geometry attribute. These are named `f` and `g`. For example, here is
an expression that tests whether the input feature is within 50 meters of the
given point.

```lisp
<= (distance g (Point -105.0 39.753056)) 50.0
```

fio-reduce evaluates expressions in the context of the sequence of all input
geometries, which is named `c`. For example, this expression dissolves input
geometries using Shapely's `unary_union`.

```lisp
unary_union c
```

Support
-------

For usage help, please use the project discussion forum or email
developers@planet.com.

If you think you've found a bug, please use the project issue tracker.

Roadmap
-------

Version 1.0 adds `filter`, `map`, and `reduce` to Fiona's `fio` CLI.

Note that there are no conditional forms in 1.0's expressions. The project will
likely add a `cond` after 1.0.

Contributing
------------

Before 1.0  the project is looking for feedback on the existing commands more
than it is looking for new commands.

The project uses black, flake8, mypy, and tox for static checks
and testing.

```
black src tests && flake8 && mypy && tox
```

Authors and acknowledgment
--------------------------

Contributors to this project are

* Sean Gillies <sean.gillies@planet.com>

License
-------

Apache License, Version 2.0.
