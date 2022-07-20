# Skeleton of a CLI

import json

import click
from cligj import use_rs_opt
from fiona.fio.helpers import obj_gen

from fio_geomod import modulate


@click.command(
    "geomod", short_help="Modulate the geometries of a stream of GeoJSON features."
)
@click.option(
    "--pipeline",
    help="A shapely geometry pipeline such as 'buffer(100.0).simplify(5.0)'.",
)
@use_rs_opt
@click.pass_context
def geomod(ctx, pipeline, use_rs):
    """Modulate the geometries of a stream of GeoJSON features.

    Given a sequence of GeoJSON features (RS-delimited or not) on stdin
    this prints copies with geometries that are modulated, transformed,
    using a provided transformation pipeline.

    """
    stdin = click.get_text_stream("stdin")
    for feat in obj_gen(stdin):
        new_feat = modulate(feat, pipeline)
        if use_rs:
            click.echo("\x1e", nl=False)
        click.echo(json.dumps(new_feat))
