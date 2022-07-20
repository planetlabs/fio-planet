from click.testing import CliRunner

from fiona.fio.main import main_group


def test_cli_count():
    with open("tests/data/trio.seq") as seq:
        data = seq.read()

    runner = CliRunner()
    result = runner.invoke(main_group, ["geomod", "buffer(1.0).centroid"], input=data)
    assert result.exit_code == 0
    assert result.output.count('"type": "Point"') == 3
