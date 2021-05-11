import platform
import sys
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
Test statistics parsed successfully from %r
 - Nb tests: Total (6) = Success (2) + Skipped (1) + Failed (2) + Errors (1)
 - Success percentage: 40.00%% (2 / 5) (Skipped tests are excluded)

SUCCESS - Tests badge created: %r
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


def test_junit_file_not_found(monkeypatch, tmpdir):
    """Test that the error message is nice when the input file is not found"""

    currentfolder = Path(str(tmpdir))
    monkeypatch.chdir(str(currentfolder))

    # default input file: the error is raised by us as a click.exceptions.FileError (exit code 1)
    result = _invoke_genbadge(["tests"])
    assert result.exit_code == 1
    assert "\n" + result.output == """
Error: Could not open file reports/junit/junit.xml: File not found
"""

    # different non-existent input file: the error is raised by click from click.File as a BadParameterError (code 2)
    result = _invoke_genbadge(["tests", "-i", "unknown.file"])
    assert result.exit_code == 2
    assert "\n" + result.output == """
Usage: genbadge tests [OPTIONS]
Try 'genbadge tests --help' for help.

Error: Invalid value for '-i' / '--input-file': Could not open file: unknown.file: No such file or directory
"""


@pytest.mark.parametrize("variant", ["default", "custom", "custom_shortargs", "custom_absolute"])
def test_junit(monkeypatch, tmpdir, variant):
    """Test that `genbadge tests` works correctly"""

    # from pytest path to pathlib path
    currentfolder = Path(str(tmpdir))  # TESTS_FOLDER

    # change the working directory to tmpdir
    monkeypatch.chdir(str(currentfolder))

    # create the various arguments. Use local template for faster exec
    args = ["tests", "-l"]
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
        args += ["-i" if shortargs else "--input-file", infile_path_for_msg]
        args += ["-o" if shortargs else "--output-file", "bar/bar-badge.svg"]
    else:
        raise ValueError(variant)
    outfile_path_for_msg = str(outfile.absolute().as_posix())

    # copy the file from source
    infile.parent.mkdir(parents=True, exist_ok=True)
    copy(str(EXAMPLE_JUNIT_XML), str(infile))

    # execute "genbadge tests" with the appropriate arguments
    print("Executing command in tmp folder %s" % (currentfolder,))
    result = _invoke_genbadge(args)
    assert result.exit_code == 0

    # verify the output message
    assert "\n" + result.output == EXAMPLE_OUTPUT % (infile_path_for_msg, outfile_path_for_msg)

    assert outfile.exists()


@pytest.mark.parametrize("threshold", [-1, 0, 40, 40.1, 100, 101])
@pytest.mark.parametrize("shortarg", [False, True])
def test_threshold(threshold, shortarg, tmpdir):

    # from pytest path to pathlib path
    destfolder = Path(str(tmpdir))
    badge_path = destfolder / "tests-badge.svg"

    # define cli args (explicit input so that we do not fall into the python 2 issue with CliRunner IOError
    args = ["tests", "-i", str(EXAMPLE_JUNIT_XML), "-o", "%s" % badge_path]
    args += ["-t" if shortarg else "--threshold", str(threshold)]

    # execute "genbadge tests" with the appropriate arguments
    result = _invoke_genbadge(args)

    if 40.0 < threshold:
        assert result.exit_code == 1

        # verify the output message
        assert "\n" + result.output == """
Test statistics parsed successfully from '{}'
 - Nb tests: Total (6) = Success (2) + Skipped (1) + Failed (2) + Errors (1)
 - Success percentage: 40.00% (2 / 5) (Skipped tests are excluded)

Error: Success percentage 40.0% is strictly lower than required threshold {}%
""".format(str(EXAMPLE_JUNIT_XML), float(threshold))

        assert not badge_path.exists()

    else:
        assert result.exit_code == 0

        # verify the output message
        assert "\n" + result.output == EXAMPLE_OUTPUT % (str(EXAMPLE_JUNIT_XML), str(badge_path.as_posix()))

        assert badge_path.exists()


@pytest.mark.parametrize("use_shields,shortarg",
                         [(None, None), (False, False), (False, True), (True, False), (True, True)])
def test_local_remote(use_shields, shortarg, tmpdir):

    if use_shields is False and sys.version_info < (3,) and platform.system != "Windows":
        pytest.skip("On Linux the embedded ttf font file is needed, and because of the path change pkg_resources does"
                    "not manage to find the file on python 2")

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
    result = _invoke_genbadge(args)
    assert result.exit_code == 0

    # verify the output message
    assert "\n" + result.output == EXAMPLE_OUTPUT % (str(EXAMPLE_JUNIT_XML), str(badge_path.as_posix()))

    assert badge_path.exists()


def _invoke_genbadge(args):
    runner = CliRunner()
    print("\n> genbadge %s" % (" ".join(args),))
    result = runner.invoke(genbadge_cmd, args, catch_exceptions=False)
    print(result.output)
    return result
