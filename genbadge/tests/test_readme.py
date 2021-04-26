from shutil import copy

import pytest

try:
    from pathlib import Path
except ImportError:  # pragma: no cover
    from pathlib2 import Path  # python 2

from click.testing import CliRunner
from genbadge.main import genbadge


TESTS_FOLDER = Path(__file__).parent.absolute()


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


@pytest.mark.parametrize("variant", ["default", "custom", "custom_shortargs", "custom_absolute"])
def test_junit(monkeypatch, tmpdir, variant):
    """Test that `genbadge junit` works correctly"""

    # change the working directory to tmpdir
    currentfolder = Path(str(tmpdir))  # TESTS_FOLDER
    monkeypatch.chdir(str(currentfolder))

    # create the various arguments
    args = ["junit"]
    if variant == "default":
        infile = currentfolder / "reports" / "junit" / "junit.xml"
        outfile = currentfolder / "junit-badge.svg"
        infile_path_for_msg = str(infile.absolute().as_posix())
    elif variant in ("custom", "custom_shortargs", "custom_absolute"):
        shortargs = "shortargs" in variant
        absolute = "absolute" in variant
        infile_path_for_msg = "foo/foo.xml"
        infile = currentfolder / infile_path_for_msg
        if absolute:
            infile_path_for_msg = infile.absolute().as_posix()
        outfile = currentfolder / "bar" / "bar-badge.svg"
        args += ["-i" if shortargs else "--input_file", infile_path_for_msg]
        args += ["-o" if shortargs else "--output_file", "bar/bar-badge.svg"]
    else:
        raise ValueError(variant)
    outfile_path_for_msg = str(outfile.absolute().as_posix())

    # copy the file from source
    infile.parent.mkdir(parents=True, exist_ok=True)
    infile_source = TESTS_FOLDER / "reports" / "junit" / "junit.xml"
    copy(str(infile_source), str(infile))

    # execute "genbadge junit" with the appropriate arguments
    runner = CliRunner()
    print("Executing command in tmp folder %s" % (currentfolder,))
    print("\n> genbadge %s\n" % (" ".join(args),))
    result = runner.invoke(genbadge, args)
    print(result.output)
    assert result.exit_code == 0

    # verify the output message
    assert "\n" + result.output == """
Test Stats parsed successfully.
 - Source file: %r
 - Nb tests: Total (6) = Success (2) + Skipped (1) + Failed (2) + Errors (1)
 - Success percentage: 33.00%%

JUnit badge created: %r
""" % (infile_path_for_msg, outfile_path_for_msg)

    assert outfile.exists()
