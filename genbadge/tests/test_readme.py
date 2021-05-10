from shutil import copy

import pytest

try:
    from pathlib import Path
except ImportError:  # pragma: no cover
    from pathlib2 import Path  # python 2

from click.testing import CliRunner
from genbadge.main import genbadge as genbadge_cmd


TESTS_FOLDER = Path(__file__).parent.absolute()
EXAMPLE_JUNIT_XML = (TESTS_FOLDER / "reports" / "junit" / "junit.xml").as_posix()
EXAMPLE_OUTPUT = """
Test Stats parsed successfully.
 - Source file: %r
 - Nb tests: Total (6) = Success (2) + Skipped (1) + Failed (2) + Errors (1)
 - Success percentage: 40.00%% (2 / 5) (Skipped tests are excluded)

Tests badge created: %r
"""

def test_help():
    """Test that `genbadge` provides the right help"""

    runner = CliRunner()
    result = runner.invoke(genbadge_cmd, [], catch_exceptions=False)

    assert result.exit_code == 0
    print(result.output)
    assert "\n" + result.output == """
Usage: genbadge [OPTIONS] COMMAND [ARGS]...

  Commandline utility to generate badges. To get help on each command use:

      genbadge <cmd> --help

Options:
  --help  Show this message and exit.

Commands:
  tests  Generate a badge for the test results (e.g. from a junit.xml).
"""


@pytest.mark.parametrize("variant", ["default", "custom", "custom_shortargs", "custom_absolute"])
def test_junit(monkeypatch, tmpdir, variant):
    """Test that `genbadge tests` works correctly"""

    # from pytest path to pathlib path
    currentfolder = Path(str(tmpdir))  # TESTS_FOLDER

    # change the working directory to tmpdir
    # Note: this has a side-effect on python 2 with pip install in dev mode where the module absolute paths seem lost
    # so the "local" mode (using the svg template) is not available
    monkeypatch.chdir(str(currentfolder))

    # create the various arguments
    args = ["tests"]
    if variant == "default":
        infile = currentfolder / "reports" / "junit" / "junit.xml"
        outfile = currentfolder / "tests-badge.svg"
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
    copy(str(EXAMPLE_JUNIT_XML), str(infile))

    # execute "genbadge tests" with the appropriate arguments
    runner = CliRunner()
    print("Executing command in tmp folder %s" % (currentfolder,))
    print("\n> genbadge %s\n" % (" ".join(args),))
    result = runner.invoke(genbadge_cmd, args, catch_exceptions=False)
    print(result.output)
    assert result.exit_code == 0

    # verify the output message
    assert "\n" + result.output == EXAMPLE_OUTPUT % (infile_path_for_msg, outfile_path_for_msg)

    assert outfile.exists()


@pytest.mark.parametrize("use_shields,shortarg",
                         [(None, None), (False, False), (False, True), (True, False), (True, True)])
def test_local_remote(use_shields, shortarg, tmpdir):

    # from pytest path to pathlib path
    destfolder = Path(str(tmpdir))
    badge_path = destfolder / "tests-badge.svg"

    # define cli args (explicit input so that we do not fall into the python 2 issue with CliRunner IOError
    args = ["tests", "-i", str(EXAMPLE_JUNIT_XML), "-o", "%s" % badge_path]
    if use_shields is False:
        args.append("-l" if shortarg else "--local")
    if use_shields is True:
        args.append("-w" if shortarg else "--webshields")

    # execute "genbadge tests" with the appropriate arguments
    runner = CliRunner()
    print("\n> genbadge %s\n" % (" ".join(args),))
    result = runner.invoke(genbadge_cmd, args, catch_exceptions=False)
    print(result.output)
    assert result.exit_code == 0

    # verify the output message
    assert "\n" + result.output == EXAMPLE_OUTPUT % (str(EXAMPLE_JUNIT_XML), str(badge_path.as_posix()))

    assert badge_path.exists()
