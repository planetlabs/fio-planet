# cli.py: command line interface.
#
# Copyright 2022 Planet Labs PBC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from copy import copy
import json

import click
from cligj import use_rs_opt
from fiona.fio.helpers import obj_gen

from .features import map_feature, reduce_features


@click.command(
    "map",
    short_help="Map a pipeline expression over GeoJSON features.",
)
@click.argument("pipeline")
@click.option(
    "--raw",
    is_flag=True,
    default=False,
    help="Print raw result, do not wrap in a GeoJSON Feature.",
)
@click.option("--dump-parts", is_flag=True, default=False, help="Dump parts of geometries to create new inputs before evaluating pipeline.")
@use_rs_opt
def map_cmd(pipeline, raw, dump_parts, use_rs):
    """Map a pipeline expression over GeoJSON features, producing new
    GeoJSON features or, optionally, raw JSON values.

    Given a sequence of GeoJSON features (RS-delimited or not) on stdin
    this prints copies with geometries that are transformed using a
    provided transformation pipeline. In "raw" output mode, this
    command prints pipeline results without wrapping them in a feature
    object.

    The pipeline is a string which, when evaluated by fio-map, produces
    a new geometry object. The pipeline consists of expressions in the
    form of parenthesized lists which may contain other expressions.
    The first item in a list is the name of a function or method, or an
    expression that evaluates to a function. The second item is the
    function's first argument or the object to which the method is
    bound. The remaining list items are the positional and keyword
    arguments for the named function or method. The names of the input
    feature and its geometry in the context of these expressions are
    "f" and "g".

    For example, this pipeline expression

        '(simplify (buffer g 100.0) 5.0)'

    buffers input geometries and then simplifies them so that no
    vertices are closer than 5 units. Keyword arguments for the shapely
    methods are supported. A keyword argument is preceded by ':' and
    followed immediately by its value. For example:

        '(simplify g 5.0 :preserve_topology true)'

    and

        '(buffer g 100.0 :resolution 8 :join_style 1)'

    Numerical and string arguments may be replaced by expressions. The
    buffer distance could be a function of a geometry's area.

        '(buffer g (/ (area g) 100.0))'

    """
    stdin = click.get_text_stream("stdin")
    for feat in obj_gen(stdin):
        for i, value in enumerate(map_feature(pipeline, feat, dump_parts=dump_parts)):
            if use_rs:
                click.echo("\x1e", nl=False)
            if raw:
                click.echo(json.dumps(value))
            else:
                new_feat = copy(feat)
                new_feat["id"] = f"{feat.get('id', '0')}:{i}"
                new_feat["geometry"] = value
                click.echo(json.dumps(new_feat))


@click.command("reduce", short_help="Reduce a stream of GeoJSON features to one value.")
@click.argument("pipeline")
@click.option(
    "--raw",
    is_flag=True,
    default=False,
    help="Print raw result, do not wrap in a GeoJSON Feature.",
)
@use_rs_opt
def reduce_cmd(pipeline, raw, use_rs):
    """Reduce a stream of GeoJSON features to one value.

    Given a sequence of GeoJSON features (RS-delimited or not) on stdin
    this prints a single value using a provided transformation pipeline.

    The pipeline is a string which, when evaluated, produces
    a new geometry object. The pipeline consists of expressions in the
    form of parenthesized lists which may contain other expressions.
    The first item in a list is the name of a function or method, or an
    expression that evaluates to a function. The second item is the
    function's first argument or the object to which the method is
    bound. The remaining list items are the positional and keyword
    arguments for the named function or method. The set of geometries
    of the input features in the context of these expressions is named
    "c".

    For example, the pipeline expression

        '(unary_union c)'

    dissolves the geometries of input features.

    """
    stdin = click.get_text_stream("stdin")
    features = (feat for feat in obj_gen(stdin))
    for result in reduce_features(pipeline, features):
        if use_rs:
            click.echo("\x1e", nl=False)
        if raw:
            click.echo(json.dumps(result))
        else:
            click.echo(json.dumps({"type": "Feature", "properties": {}, "geometry": result, "id": "0"}))
