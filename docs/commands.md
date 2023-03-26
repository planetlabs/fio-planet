Commands
========

fio-filter
----------

For each feature read from stdin, fio-filter evaluates a pipeline of one or
more steps described using methods from the Shapely library in Lisp-like
expressions. If the pipeline expression evaluates to True, the feature passes
through the filter. Otherwise the feature does not pass.

For example, this pipeline expression

```
$ fio cat zip+https://s3.amazonaws.com/fiona-testing/coutwildrnp.zip \
| fio filter '< (distance g (Point -109.0 38.5)) 100'
```

lets through all features that are less than 100 meters from the given point
and filters out all other features.

fio-map
-------

For each feature read from stdin, fio-map applies a transformation pipeline and
writes a copy of the feature, containing the modified geometry, to stdout. For
example, polygonal features can be roughly "cleaned" by using a `buffer g 0`
pipeline.

```
$ fio cat zip+https://s3.amazonaws.com/fiona-testing/coutwildrnp.zip \
| fio map 'buffer g 0'
```

fio-reduce
----------

Given a sequence of GeoJSON features (RS-delimited or not) on stdin this prints
a single value using a provided transformation pipeline.  The set of geometries
of the input features in the context of these expressions is named "c".

For example, the pipeline expression

```
$ fio cat zip+https://s3.amazonaws.com/fiona-testing/coutwildrnp.zip \
| fio reduce 'unary_union c'
```

dissolves the geometries of input features.
