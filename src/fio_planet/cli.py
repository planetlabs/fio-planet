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
from shapely.geometry import mapping, shape

from fio_planet.modulate import modulate, reduce
from fio_planet.calculate import calculate


@click.command(
    "geomod", short_help="Modulate the geometries of a stream of GeoJSON features."
)
@click.argument("pipeline")
@use_rs_opt
def geomod_cmd(pipeline, use_rs):
    """Modulate the geometries of a stream of GeoJSON features.

    Given a sequence of GeoJSON features (RS-delimited or not) on stdin
    this prints copies with geometries that are modulated, transformed,
    using a provided transformation pipeline.

    The pipeline is a string which, when evaluated by fio-geomod,
    produces a new geometry object. The pipeline consists of expressions
    in the form of parenthesized lists, which may contain other
    expressions.  The first item in a list is the name of a Shapely
    geometry attribute or method. The second is the name of a Shapely
    geometry object or an expression that evaluates to a geometry
    object.  The remaining list items are the positional and keyword
    arguments for the named method. The name of the input feature's
    geometry in the context of these expressions is "g".

    For example,

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
        new_feat = modulate(feat, pipeline)
        if use_rs:
            click.echo("\x1e", nl=False)
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

    The pipeline is a string which, when evaluated by fio-reduce,
    produces a new JSON object. The pipeline consists of expressions
    in the form of parenthesized lists, which may contain other
    expressions.  The first item in a list is the name of a Shapely
    geometry attribute or method. The second is the name of a Shapely
    geometry object or an expression that evaluates to a geometry
    object.  The remaining list items are the positional and keyword
    arguments for the named method. The name of the set of input
    features in the context of these expressions is "c".

    For example,

        '(unary_union c)'

    dissolves the geometries of input features.

    """
    stdin = click.get_text_stream("stdin")
    features = (feat for feat in obj_gen(stdin))
    result = reduce(pipeline, features, raw=raw)
    if use_rs:
        click.echo("\x1e", nl=False)
    click.echo(json.dumps(result))


@click.command(
    "geocalc",
    short_help="Evaluate expressions involving GeoJSON features and their geometries.",
)
@click.argument("expression")
@use_rs_opt
def geomcalc_cmd(expression, use_rs):
    """Evaluate expressions involving GeoJSON features and their geometries."""
    stdin = click.get_text_stream("stdin")
    for feat in obj_gen(stdin):
        result = calculate(feat, expression)
        if use_rs:
            click.echo("\x1e", nl=False)
        click.echo(json.dumps(result))


@click.command(
    "geodump",
    short_help="Dump GeoJSON features, producing feature with single-part geometries.",
)
@use_rs_opt
def geodump_cmd(use_rs):
    """Dump GeoJSON features, producing feature with single-part geometries."""
    stdin = click.get_text_stream("stdin")
    for feat in obj_gen(stdin):
        geom = shape(feat["geometry"])
        if hasattr(geom, "geoms"):
            for i, part in enumerate(geom.geoms, 1):
                if use_rs:
                    click.echo("\x1e", nl=False)
                new_feat = copy(feat)
                new_feat["id"] = f"{feat.get('id', '0')}:{i}"
                new_feat["geometry"] = mapping(part)
                click.echo(json.dumps(new_feat))
        else:
            if use_rs:
                click.echo("\x1e", nl=False)
            click.echo(json.dumps(feat))
