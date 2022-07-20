# fio_geomod

from copy import copy

from shapely.geometry import mapping, shape


def modulate(feature, pipeline):
    """Modulate the geometry of a feature by applying a pipeline.

    Parameters
    ----------
    feature : Feature
        A Fiona feature.
    pipeline : string
        Geometry operation pipeline such as "buffer(2.0).exterior".

    Returns
    -------
    Feature
        A copy of the input feature, with a modulated geometry.

    """
    geom = shape(feature["geometry"])  # deprecated usage.
    loc = {"geom": geom}
    exec(f"new_geom = geom.{pipeline}", globals(), loc)
    new_feat = copy(feature)
    new_feat["geometry"] = mapping(loc["new_geom"])
    return new_feat
