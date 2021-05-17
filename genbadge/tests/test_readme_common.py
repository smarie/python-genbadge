import platform
import sys
from shutil import copy

import click
from distutils.version import LooseVersion

import pytest

try:
    from pathlib import Path
except ImportError:  # pragma: no cover
    from pathlib2 import Path  # python 2

from click.testing import CliRunner
from genbadge.main import genbadge as genbadge_cmd


TESTS_FOLDER = Path(__file__).parent.absolute()


class CmdReference:
    """
    Container class used to store our test reference for all commands
    """
    def __init__(self, name, default_infile, default_outfile, example_input_file, example_output_msg,
                 example_output_msg_long, help_msg):
        self.name = name
        self.default_infile = default_infile
        self.default_outfile = default_outfile
        self.example_input_file = example_input_file
        self.example_output_msg = example_output_msg
        self.example_output_msg_long = example_output_msg_long
        self.help_msg = help_msg

    def __str__(self):
        return self.name


TEST_CMD = CmdReference(
        name="tests",
        default_infile="reports/junit/junit.xml",
        default_outfile = "tests-badge.svg",
        example_input_file=(TESTS_FOLDER / "reports" / "junit" / "junit.xml").as_posix(),
        example_output_msg="SUCCESS - Tests badge created: %r\n",
        example_output_msg_long="""
Test statistics parsed successfully from %r
 - Nb tests: Total (6) = Success (2) + Skipped (1) + Failed (2) + Errors (1)
 - Success percentage: 40.00%% (2 / 5) (Skipped tests are excluded)

SUCCESS - Tests badge created: %r
""",
        help_msg="""Usage: genbadge tests [OPTIONS]

  This command generates a badge for the test results, from an XML file in the
  junit format. Such a file can be for example generated from python pytest
  using the --junitxml flag, or from java junit.

  By default the input file is the relative `./reports/junit/junit.xml` and the
  output file is `./tests-badge.svg`. You can change these settings with the
  `-i/--input_file` and `-o/--output-file` options.

  You can use the verbose flag `-v/--verbose` to display information on the
  input file contents, for verification.

  The resulting badge will by default look like this: [tests | 6/12] where 6 is
  the number of tests that have run successfully, and 12 is the total number of
  tests minus the number of skipped tests. You can change the appearance of the
  badge with the --format option (not implemented, todo).

  The success percentage is defined as 6/12 = 50.0%. You can use the
  `-t/--threshold` flag to setup a minimum success percentage required. If the
  success percentage is below the threshold, an error will be raised and the
  badge will not be generated.

Options:
  -i, --input-file FILENAME       An alternate test results XML file to read.
                                  '-' is supported and means <stdin>.
  -o, --output-file FILENAME      An alternate SVG badge file to write to. '-'
                                  is supported and means <stdout>. Note that in
                                  this case no other message will be printed to
                                  <stdout>. In particular the verbose flag will
                                  have no effect.
  -t, --threshold FLOAT           An optional success percentage threshold to
                                  use. The command will fail with exit code 1 if
                                  theactual success percentage is strictly less
                                  than the provided value.
  -w, --webshields / -l, --local  Indicates if badges should be generated using
                                  the shields.io HTTP API (default) or the local
                                  SVG file template included.
  -v, --verbose                   Use this flag to print details to stdout
                                  during the badge generation process. Note that
                                  this flag has no effect when '-' is used as
                                  output, since the badge is written to
                                  <stdout>. It also has no effect when the
                                  silent flag `-s` is used.
  -s, --silent                    When this flag is active nothing will be
                                  written to stdout. Note that this flag has no
                                  effect when '-' is used as the output file.
  --help                          Show this message and exit.
"""
)
COV_CMD = CmdReference(
        name="coverage",
        default_infile="reports/coverage/coverage.xml",
        default_outfile = "coverage-badge.svg",
        example_input_file=(TESTS_FOLDER / "reports" / "coverage" / "coverage.xml").as_posix(),
        example_output_msg="SUCCESS - Coverage badge created: %r\n",
        example_output_msg_long="""
Coverage results parsed successfully from %r
 - Branch coverage: 5.56%% (1/18)
 - Line coverage: 17.81%% (13/73)
 - Total coverage: 15.38%% ((1+13)/(18+73))

SUCCESS - Coverage badge created: %r
""",
        help_msg="""Usage: genbadge coverage [OPTIONS]

  This command generates a badge for the coverage results, from an XML file in
  the 'coverage' format. Such a file can be for example generated using the
  python `coverage` tool, or java `cobertura`.

  By default the input file is the relative `./reports/coverage/coverage.xml`
  and the output file is `./coverage-badge.svg`. You can change these settings
  with the `-i/--input_file` and `-o/--output-file` options.

  You can use the verbose flag `-v/--verbose` to display information on the
  input file contents, for verification.

  The resulting badge will by default look like this: [coverage | 98.1%] where
  98.1 is the total coverage, obtained from the branch and line coverages using
  the formula

      (nb_lines_covered + nb_branches_covered) / (nb_lines / nb_branches)

  and multiplying this by 100.

Options:
  -i, --input-file FILENAME       An alternate coverage results XML file to
                                  read. '-' is supported and means <stdin>.
  -o, --output-file FILENAME      An alternate SVG badge file to write to. '-'
                                  is supported and means <stdout>. Note that in
                                  this case no other message will be printed to
                                  <stdout>. In particular the verbose flag will
                                  have no effect.
  -w, --webshields / -l, --local  Indicates if badges should be generated using
                                  the shields.io HTTP API (default) or the local
                                  SVG file template included.
  -v, --verbose                   Use this flag to print details to stdout
                                  during the badge generation process. Note that
                                  this flag has no effect when '-' is used as
                                  output, since the badge is written to
                                  <stdout>. It also has no effect when the
                                  silent flag `-s` is used.
  -s, --silent                    When this flag is active nothing will be
                                  written to stdout. Note that this flag has no
                                  effect when '-' is used as the output file.
  --help                          Show this message and exit.
"""
)
FLAKE8_CMD = CmdReference(
        name="flake8",
        default_infile="reports/flake8/flake8stats.txt",
        default_outfile = "flake8-badge.svg",
        example_input_file=(TESTS_FOLDER / "reports" / "flake8" / "flake8stats.txt").as_posix(),
        example_output_msg="SUCCESS - Flake8 badge created: %r\n",
        example_output_msg_long="""
Flake8 statistics parsed successfully from %r
 - Total (20) = Critical (6) + Warning (9) + Info (5)

SUCCESS - Flake8 badge created: %r
""",
        help_msg="""Usage: genbadge flake8 [OPTIONS]

  This command generates a badge for the flake8 results, from a flake8stats.txt
  file. Such a file can be generated from python `flake8` using the --statistics
  flag.

  By default the input file is the relative `./reports/flake8/flake8stats.txt`
  and the output file is `./flake8-badge.svg`. You can change these settings
  with the `-i/--input_file` and `-o/--output-file` options.

  You can use the verbose flag `-v/--verbose` to display information on the
  input file contents, for verification.

  The resulting badge will by default look like this: [flake8 | 6 C, 0 W, 5 I]
  where 6, 0, 5 denote the number of critical issues, warnings, and information
  messages respectively. These severity levels are determined by the flake8-html
  plugin so as to match the colors in the HTML report. You can change the
  appearance of the badge with the --format option (not implemented, todo).

Options:
  -i, --input-file FILENAME       An alternate flake8 results TXT file to read.
                                  '-' is supported and means <stdin>.
  -o, --output-file FILENAME      An alternate SVG badge file to write to. '-'
                                  is supported and means <stdout>. Note that in
                                  this case no other message will be printed to
                                  <stdout>. In particular the verbose flag will
                                  have no effect.
  -w, --webshields / -l, --local  Indicates if badges should be generated using
                                  the shields.io HTTP API (default) or the local
                                  SVG file template included.
  -v, --verbose                   Use this flag to print details to stdout
                                  during the badge generation process. Note that
                                  this flag has no effect when '-' is used as
                                  output, since the badge is written to
                                  <stdout>. It also has no effect when the
                                  silent flag `-s` is used.
  -s, --silent                    When this flag is active nothing will be
                                  written to stdout. Note that this flag has no
                                  effect when '-' is used as the output file.
  --help                          Show this message and exit.
"""
)

ALL_COMMANDS = [TEST_CMD, COV_CMD, FLAKE8_CMD]
ALL_COMMAND_NAMES = [c.name for c in ALL_COMMANDS]


def test_help():
    """Test that `genbadge` provides the right help"""

    runner = CliRunner()
    result = runner.invoke(genbadge_cmd, [], catch_exceptions=False)

    assert result.exit_code == 0
    print(result.output)
    expected = """
Usage: genbadge [OPTIONS] COMMAND [ARGS]...

  Commandline utility to generate badges. To get help on each command use:

      genbadge <cmd> --help

Options:
  --help  Show this message and exit.

Commands:
  coverage  Generate a badge for the coverage results (e.g. from a
            coverage.xml).%s
  flake8    Generate a badge for the flake8 results (e.g. from a flake8stats.txt
            file).%s
  tests     Generate a badge for the test results (e.g. from a junit.xml).
"""
    if LooseVersion(click.__version__) < "8.":
        expected = expected % ("\n", "\n")
    else:
        expected = expected % ("", "")
    assert "\n" + result.output == expected


@pytest.mark.parametrize("cmd", ALL_COMMANDS, ids=str)
def test_help_cmd(cmd):
    """Test that the command-specific help message is correct"""

    result = _invoke_genbadge([cmd.name, "--help"])
    assert result.exit_code == 0

    if LooseVersion(click.__version__) >= "8.":
        assert result.output == cmd.help_msg
    else:
        # the line wrapping seems to have changed, do not check for this old version.
        pass


@pytest.mark.parametrize("cmd", ALL_COMMANDS, ids=str)
def test_file_not_found(monkeypatch, tmpdir, cmd):
    """Test that the error message is nice when the input file is not found"""

    currentfolder = Path(str(tmpdir))
    monkeypatch.chdir(str(currentfolder))

    # a) default input file: the error is raised by us as a click.exceptions.FileError (exit code 1)
    result = _invoke_genbadge([cmd.name])
    assert result.exit_code == 1
    expected = """
Error: Could not open file %r: File not found
"""
    # support various versions of click
    if LooseVersion(click.__version__) < "8.":
        expected = expected.replace("%r", "%s")
    assert "\n" + result.output == expected % cmd.default_infile

    # b) different non-existent input file: the error is raised by click from click.File as a BadParameterError (code 2)
    unknown_file = "unknown.file"
    result = _invoke_genbadge([cmd.name, "-i", unknown_file])
    assert result.exit_code == 2
    expected = """
Usage: genbadge {name} [OPTIONS]
Try 'genbadge {name} --help' for help.

Error: Invalid value for '-i' / '--input-file': %s: No such file or directory
""".format(name=cmd.name)
    # support various versions of click
    if LooseVersion(click.__version__) < "8.":
        expected = expected % "Could not open file: %s"
    else:
        expected = expected % "%r"
    assert "\n" + result.output == expected % unknown_file


@pytest.mark.parametrize("outstream", [False, True], ids="outstream={}".format)
@pytest.mark.parametrize("silent", [False, True], ids="silent={}".format)
@pytest.mark.parametrize("verbose", [False, True], ids="verbose={}".format)
@pytest.mark.parametrize("variant", ["default", "custom", "custom_shortargs", "custom_absolute"])
@pytest.mark.parametrize("cmd", ALL_COMMANDS, ids=str)
def test_any_command(monkeypatch, cmd, tmpdir, variant, outstream, silent, verbose):
    """Test that `genbadge <cmd>` works consistently concerning the ios and output messages"""

    # from pytest path to pathlib path
    currentfolder = Path(str(tmpdir))  # tests_folder

    # change the working directory to tmpdir
    monkeypatch.chdir(str(currentfolder))

    # create the various arguments. Use local template for faster exec
    args = [cmd.name, "-l"]
    if verbose:
        args.append("--verbose")
    if silent:
        args.append("--silent")
    if variant == "default":
        if outstream:
            pytest.skip("this test does not make sense")
        infile = currentfolder / cmd.default_infile
        outfile = currentfolder / cmd.default_outfile
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
        args += ["-o" if shortargs else "--output-file", "-" if outstream else "bar/bar-badge.svg"]
    else:
        raise ValueError(variant)
    outfile_path_for_msg = str(outfile.absolute().as_posix())

    # copy the file from source
    infile.parent.mkdir(parents=True, exist_ok=True)
    copy(str(cmd.example_input_file), str(infile))

    # execute "genbadge tests" with the appropriate arguments
    print("Executing command in tmp folder %s" % (currentfolder,))
    result = _invoke_genbadge(args)
    assert result.exit_code == 0

    # verify the output message
    if not outstream:
        if silent:
            assert result.output == ""
        elif verbose:
            assert "\n" + result.output == cmd.example_output_msg_long % (infile_path_for_msg, outfile_path_for_msg)
        else:
            assert result.output == cmd.example_output_msg % outfile_path_for_msg
        assert outfile.exists()
    else:
        assert result.output.startswith('<svg xmlns="http://www.w3.org/2000/svg" '
                                        'xmlns:xlink="http://www.w3.org/1999/xlink" width=')


@pytest.mark.parametrize("threshold", [-1, 0, 40, 40.1, 100, 101])
@pytest.mark.parametrize("shortarg", [False, True])
def test_threshold(threshold, shortarg, tmpdir):

    # from pytest path to pathlib path
    destfolder = Path(str(tmpdir))
    badge_path = destfolder / "tests-badge.svg"

    # define cli args (explicit input so that we do not fall into the python 2 issue with CliRunner IOError
    args = ["tests", "-v", "-i", str(TEST_CMD.example_input_file), "-o", "%s" % badge_path]
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
""".format(str(TEST_CMD.example_input_file), float(threshold))

        assert not badge_path.exists()

    else:
        assert result.exit_code == 0

        # verify the output message
        assert "\n" + result.output == TEST_CMD.example_output_msg_long % (str(TEST_CMD.example_input_file), str(badge_path.as_posix()))

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
    args = ["tests", "-v", "-i", str(TEST_CMD.example_input_file), "-o", "%s" % badge_path]
    if use_shields is False:
        args.append("-l" if shortarg else "--local")
    if use_shields is True:
        args.append("-w" if shortarg else "--webshields")

    # execute "genbadge tests" with the appropriate arguments
    result = _invoke_genbadge(args)
    assert result.exit_code == 0

    # verify the output message
    assert "\n" + result.output == TEST_CMD.example_output_msg_long % (str(TEST_CMD.example_input_file), str(badge_path.as_posix()))

    assert badge_path.exists()


def _invoke_genbadge(args):
    runner = CliRunner()
    print("\n> genbadge %s" % (" ".join(args),))
    result = runner.invoke(genbadge_cmd, args, catch_exceptions=False)
    print(result.output)
    return result
