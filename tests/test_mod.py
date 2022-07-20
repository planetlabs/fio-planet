import json

from fio_geomod import modulate


def test_modulate():
    with open("tests/data/trio.geojson") as src:
        collection = json.loads(src.read())

    feat = collection["features"][0]
    new_feat = modulate(feat, "buffer(0.01).simplify(0.001)")
    assert new_feat["geometry"]["type"] == "Polygon"
