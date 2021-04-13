try:
    from pathlib import Path
except ImportError:  # pragma: no cover
    from pathlib2 import Path  # python 2

from click.testing import CliRunner
from genbadge.main import genbadge


TESTS_FOLDER = Path(__file__).parent


def test_help():
    """Test that `genbadge` provides the right help"""

    runner = CliRunner()
    result = runner.invoke(genbadge, [])

    assert result.exit_code == 0
    print(result.output)
    assert "\n" + result.output == """
Usage: genbadge [OPTIONS] COMMAND [ARGS]...

  Commandline utility to generate badges. To get help on each command use:

      genbadge <cmd> --help

Options:
  --help  Show this message and exit.

Commands:
  junit  :param junit_xml_file: :param dest_folder: :param threshold: :return:
"""


def test_junit(monkeypatch):
    """Test that `genbadge junit` works correctly"""

    # change the working directory to local
    monkeypatch.chdir(str(TESTS_FOLDER))

    runner = CliRunner()
    result = runner.invoke(genbadge, ["junit"])

    assert result.exit_code == 0
    print(result.output)

    infile = TESTS_FOLDER / "reports" / "junit" / "junit.xml"
    infile_abs_posix = infile.absolute().as_posix()

    outfile = TESTS_FOLDER / "junit-badge.svg"
    outfile_abs_posix = outfile.absolute().as_posix()

    assert "\n" + result.output == """
Test Stats parsed successfully.
 - Source file: %r
 - Nb tests: Total (6) = Success (2) + Skipped (1) + Failed (2) + Errors (1)
 - Success percentage: 33.00%%

JUnit badge created: %r
""" % (str(infile_abs_posix), str(outfile_abs_posix))

    assert outfile.exists()
