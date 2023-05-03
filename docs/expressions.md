Expressions and functions
=========================

Expressions take the form of parenthesized lists that may contain other
expressions. The first item in a list is the name of a function or method, or
an expression that evaluates to a function. The second item is the function's
first argument or the object to which the method is bound. The remaining list
items are the positional and keyword arguments for the named function or
method. The list of functions and callables available in an expression
includes:

* Python operators such as `+`, `/`, and `<=`
* Python builtins such as `dict`, `list`, and `map`
* All public functions from itertools, e.g. `islice`, and `repeat`
* All functions importable from Shapely 2.0, e.g. `Point`, and `unary_union`
* All methods of Shapely geometry classes
* Functions specific to fio-planet

Expressions are evaluated by `fio_planet.features.snuggs.eval()`. Let's look at
some examples using that function.

!!! note

    The outer parentheses are not optional within `snuggs.eval()`.

!!! note

    `snuggs.eval()` does not use Python's builtin `eval()` but isn't intended
    to be a secure computing environment. Expressions which access the
    computer's filesystem and create new processes are possible.

## Builtin Python functions

`bool`:

```python
>>> snuggs.eval('(bool 0)')
False

```

`range`:

```python
>>> snuggs.eval('(range 1 4)')
range(1, 4)

```

`list`:

```python
>>> snuggs.eval('(list (range 1 4))')
[1, 2, 3]

```

Values can be bound to names for use in expressions.

```python
>>> snuggs.eval('(list (range start stop))', start=0, stop=5)
[0, 1, 2, 3, 4]

```

## Itertools functions

Here's an example of using `itertools.repeat()`.

```python
>>> snuggs.eval('(list (repeat "*" times))', times=6)
['*', '*', '*', '*', '*', '*']

```

## Shapely functions

Here's an expression that evaluates to a Shapely Point instance.

```python
>>> snuggs.eval('(Point 0 0)')
<POINT (0 0)>

```

The expression below evaluates to a MultiPoint instance.

```python
>>> snuggs.eval('(union (Point 0 0) (Point 1 1))')
<MULTIPOINT (0 0, 1 1)>

```

## Functions specific to fio-planet

The fio-planet package introduces four new functions not available in Python's
standard library, Fiona, or Shapely: `collect`, `dump`, `identity`, and
`vertex_count`.

The `collect` function turns a list of geometries into a geometry collection
and `dump` does the inverse, turning a geometry collection into a sequence of
geometries.

```python
>>> snuggs.eval('(collect (Point 0 0) (Point 1 1))')
<GEOMETRYCOLLECTION (POINT (0 0), POINT (1 1))>
>>> snuggs.eval('(list (dump (collect (Point 0 0) (Point 1 1))))')
[<POINT (0 0)>, <POINT (1 1)>]

```

The `identity` function returns its single argument.

```python
>>> snuggs.eval('(identity 42)')
42

```

To count the number of vertices in a geometry, use `vertex_count`.

```python
>>> snuggs.eval('(vertex_count (Point 0 0))')
1

```

The `area`, `buffer`, `distance`, `length`, `simplify`, and `set_precision`
functions shadow, or override, functions from the shapely module. They
automatically reproject geometry objects from their natural coordinate
reference system (CRS) of `OGC:CRS84` to `EPSG:6933` so that the shapes can be
measured or modified using meters as units.

`buffer` dilates (or erodes) a given geometry, with coordinates in decimal
longitude and latitude degrees, by a given distance in meters.

```python
>>> snuggs.eval('(buffer (Point 0 0) :distance 100)')
<POLYGON ((0.001 0, 0.001 0, 0.001 0, 0.001 0, 0.001 -0.001, 0.001 -0.001, 0...>

```

The `area` and `length` of this polygon have units of square meter and meter.

```python
>>> snuggs.eval('(area (buffer (Point 0 0) :distance 100))')
31214.451487413342
>>> snuggs.eval('(length (buffer (Point 0 0) :distance 100))')
627.3096977558143

```

The `distance` between two geometries is in meters.

```python
>>> snuggs.eval('(distance (Point 0 0) (Point 0.1 0.1))')
15995.164946207413

```

A geometry can be simplified to a tolerance value in meters using `simplify`.
There are more examples of this function under
[topics:simplification](topics/simplification/).

```python
>>> snuggs.eval('(simplify (buffer (Point 0 0) :distance 100) :tolerance 100)')
<POLYGON ((0.001 0, 0 -0.001, -0.001 0, 0 0.001, 0.001 0))>

```

The `set_precision` function snaps a geometry to a fixed precision grid with a
size in meters.

```python
>>> snuggs.eval('(set_precision (Point 0.001 0.001) :grid_size 500)')
<POINT (0 0)>

```

## Feature and geometry context for expressions

`fio-filter` and `fio-map` evaluate expressions in the context of a GeoJSON
feature and its geometry attribute. These are named `f` and `g`. For example,
here is an expression that tests whether the input feature is within 62.5
kilometers of the given point.

```lisp
--8<-- "tests/test_cli.py:filter"
```

`fio-reduce` evaluates expressions in the context of the sequence of all input
geometries, named `c`. For example, this expression dissolves input
geometries using Shapely's `unary_union`.

```lisp
--8<-- "tests/test_cli.py:reduce"
```
