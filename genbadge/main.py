try:
    from pathlib import Path
except ImportError:  # pragma: no cover
    from pathlib2 import Path  # python 2

import click


from .utils_junit import get_test_stats, get_tests_badge
from .utils_coverage import get_coverage_badge, get_coverage_stats
from .utils_flake8 import get_flake8_stats, get_flake8_badge

try:
    FileNotFoundError
except NameError:
    FileNotFoundError = IOError


INFILE_HELP_TMP = "An alternate %s file to read. '-' is supported and means <stdin>."
OUTFILE_BADGE_HELP = ("An alternate SVG badge file to write to. '-' is supported and means <stdout>. Note that in this "
                      "case no other message will be printed to <stdout>. In particular the verbose flag will have no "
                      "effect.")
SHIELDS_HELP = ("Indicates if badges should be generated using the shields.io HTTP API (default) or the local SVG file "
                "template included.")
VERBOSE_HELP = ("Use this flag to print details to stdout during the badge generation process. Note that this flag has "
                "no effect when '-' is used as output, since the badge is written to <stdout>. It also has no effect "
                "when the silent flag `-s` is used.")
SILENT_HELP = ("When this flag is active nothing will be written to stdout. Note that this flag has no effect when '-' "
               "is used as the output file.")


@click.group()
def genbadge():
    """
    Commandline utility to generate badges.
    To get help on each command use:

        genbadge <cmd> --help

    """
    pass


@genbadge.command(name="tests",
                  short_help="Generate a badge for the test results (e.g. from a junit.xml).")
@click.option('-i', '--input-file', type=click.File('rt'), help=INFILE_HELP_TMP % "test results XML")
@click.option('-o', '--output-file', type=click.File('wt'), help=OUTFILE_BADGE_HELP)
@click.option('-t', '--threshold', type=float,
              help="An optional success percentage threshold to use. The command will fail with exit code 1 if the"
                   "actual success percentage is strictly less than the provided value.")
@click.option('-w/-l', '--webshields/--local', type=bool, default=True, help=SHIELDS_HELP)
@click.option('-v', '--verbose', type=bool, default=False, is_flag=True, help=VERBOSE_HELP)
@click.option('-s', '--silent', type=bool, default=False, is_flag=True, help=SILENT_HELP)
def gen_tests_badge(
        input_file=None,
        output_file=None,
        threshold=None,
        webshields=None,
        verbose=None,
        silent=None
):
    """
    This command generates a badge for the test results, from an XML file in the
    junit format. Such a file can be for example generated from python pytest
    using the --junitxml flag, or from java junit.

    By default the input file is the relative `./reports/junit/junit.xml` and
    the output file is `./tests-badge.svg`. You can change these settings with
    the `-i/--input_file` and `-o/--output-file` options.

    You can use the verbose flag `-v/--verbose` to display information on the
    input file contents, for verification.

    The resulting badge will by default look like this: [tests | 6/12]
    where 6 is the number of tests that have run successfully, and 12 is the
    total number of tests minus the number of skipped tests. You can change the
    appearance of the badge with the --format option (not implemented, todo).

    The success percentage is defined as 6/12 = 50.0%. You can use the
    `-t/--threshold` flag to setup a minimum success percentage required. If the
    success percentage is below the threshold, an error will be raised and the
    badge will not be generated.
    """
    # Process i/o files
    input_file, input_file_path = _process_infile(input_file, "reports/junit/junit.xml")
    output_file, output_file_path, is_stdout = _process_outfile(output_file, "tests-badge.svg")

    # First retrieve the success percentage from the junit xml
    try:
        test_stats = get_test_stats(junit_xml_file=input_file)
    except FileNotFoundError:
        raise click.exceptions.FileError(input_file, hint="File not found")

    if not silent and verbose and not is_stdout:
        click.echo("""Test statistics parsed successfully from %r
 - Nb tests: Total (%s) = Success (%s) + Skipped (%s) + Failed (%s) + Errors (%s)
 - Success percentage: %.2f%% (%s / %s) (Skipped tests are excluded)
""" % (input_file_path, test_stats.total_with_skipped, test_stats.success, test_stats.skipped, test_stats.failed,
       test_stats.errors, test_stats.success_percentage, test_stats.success, test_stats.total_without_skipped))

    # sanity check
    if test_stats.total_with_skipped != test_stats.success + test_stats.skipped + test_stats.failed + test_stats.errors:
        raise click.exceptions.ClickException(
            "Inconsistent junit results: the sum of all kind of tests is not equal to the total. Please report this "
            "issue if you think your file is correct. Details: %r" % test_stats
        )

    # Validate against the threshold
    if threshold is not None and test_stats.success_percentage < threshold:
        raise click.exceptions.ClickException(
            "Success percentage %s%% is strictly lower than required threshold %s%%"
            % (float(test_stats.success_percentage), threshold)
        )

    # Generate the badge
    badge = get_tests_badge(test_stats)
    badge.write_to(output_file if is_stdout else output_file_path, use_shields=webshields)

    if not silent and not is_stdout:
        click.echo("SUCCESS - Tests badge created: %r" % str(output_file_path))


@genbadge.command(name="coverage",
                  short_help="Generate a badge for the coverage results (e.g. from a coverage.xml).")
@click.option('-i', '--input-file', type=click.File('rt'), help=INFILE_HELP_TMP % "coverage results XML")
@click.option('-o', '--output-file', type=click.File('wt'), help=OUTFILE_BADGE_HELP)
@click.option('-w/-l', '--webshields/--local', type=bool, default=True, help=SHIELDS_HELP)
@click.option('-v', '--verbose', type=bool, default=False, is_flag=True, help=VERBOSE_HELP)
@click.option('-s', '--silent', type=bool, default=False, is_flag=True, help=SILENT_HELP)
def gen_coverage_badge(
        input_file=None,
        output_file=None,
        webshields=None,
        verbose=None,
        silent=None
):
    """
    This command generates a badge for the coverage results, from an XML file in
    the 'coverage' format. Such a file can be for example generated using the
    python `coverage` tool, or java `cobertura`.

    By default the input file is the relative `./reports/coverage/coverage.xml`
    and the output file is `./coverage-badge.svg`. You can change these settings
    with the `-i/--input_file` and `-o/--output-file` options.

    You can use the verbose flag `-v/--verbose` to display information on the
    input file contents, for verification.

    The resulting badge will by default look like this: [coverage | 98.1%] where
    98.1 is the total coverage, obtained from the branch and line coverages
    using the formula

        (nb_lines_covered + nb_branches_covered) / (nb_lines / nb_branches)

    and multiplying this by 100.
    """
    # Process i/o files
    input_file, input_file_path = _process_infile(input_file, "reports/coverage/coverage.xml")
    output_file, output_file_path, is_stdout = _process_outfile(output_file, "coverage-badge.svg")

    # First retrieve the coverage info from the coverage xml
    try:
        cov_stats = get_coverage_stats(coverage_xml_file=input_file)
    except FileNotFoundError:
        raise click.exceptions.FileError(input_file, hint="File not found")

    if not silent and verbose and not is_stdout:
        click.echo("""Coverage results parsed successfully from %(ifp)r
 - Branch coverage: %(bcp).2f%% (%(bc)s/%(bv)s)
 - Line coverage: %(lcp).2f%% (%(lc)s/%(lv)s)
 - Total coverage: %(tcp).2f%% ((%(bc)s+%(lc)s)/(%(bv)s+%(lv)s))
""" % dict(ifp=input_file_path, tcp=cov_stats.total_coverage,
           bcp=cov_stats.branch_coverage, bc=cov_stats.branches_covered, bv=cov_stats.branches_valid,
           lcp=cov_stats.line_coverage, lc=cov_stats.lines_covered, lv=cov_stats.lines_valid))

    # Generate the badge
    badge = get_coverage_badge(cov_stats)
    badge.write_to(output_file if is_stdout else output_file_path, use_shields=webshields)

    if not silent and not is_stdout:
        click.echo("SUCCESS - Coverage badge created: %r" % str(output_file_path))


@genbadge.command(name="flake8",
                  short_help="Generate a badge for the flake8 results (e.g. from a flake8stats.txt file).")
@click.option('-i', '--input-file', type=click.File('rt'), help=INFILE_HELP_TMP % "flake8 results TXT")
@click.option('-o', '--output-file', type=click.File('wt'), help=OUTFILE_BADGE_HELP)
@click.option('-w/-l', '--webshields/--local', type=bool, default=True, help=SHIELDS_HELP)
@click.option('-v', '--verbose', type=bool, default=False, is_flag=True, help=VERBOSE_HELP)
@click.option('-s', '--silent', type=bool, default=False, is_flag=True, help=SILENT_HELP)
def gen_flake8_badge(
        input_file=None,
        output_file=None,
        webshields=None,
        verbose=None,
        silent=None
):
    """
    This command generates a badge for the flake8 results, from a flake8stats.txt
    file. Such a file can be generated from python `flake8` using the
    --statistics flag.

    By default the input file is the relative `./reports/flake8/flake8stats.txt`
    and the output file is `./flake8-badge.svg`. You can change these settings
    with the `-i/--input_file` and `-o/--output-file` options.

    You can use the verbose flag `-v/--verbose` to display information on the
    input file contents, for verification.

    The resulting badge will by default look like this: [flake8 | 6 C, 0 W, 5 I]
    where 6, 0, 5 denote the number of critical issues, warnings, and
    information messages respectively. These severity levels are determined by
    the flake8-html plugin so as to match the colors in the HTML report. You can
    change the appearance of the badge with the --format option (not
    implemented, todo).
    """
    # Process i/o files
    input_file, input_file_path = _process_infile(input_file, "reports/flake8/flake8stats.txt")
    output_file, output_file_path, is_stdout = _process_outfile(output_file, "flake8-badge.svg")

    # First retrieve the success percentage from the junit xml
    try:
        flake8_stats = get_flake8_stats(flake8_stats_file=input_file)
    except FileNotFoundError:
        raise click.exceptions.FileError(input_file, hint="File not found")

    if not silent and verbose and not is_stdout:
        click.echo("""Flake8 statistics parsed successfully from %r
 - Total (%s) = Critical (%s) + Warning (%s) + Info (%s)
""" % (input_file_path, flake8_stats.nb_total, flake8_stats.nb_critical, flake8_stats.nb_warning, flake8_stats.nb_info))

    # Generate the badge
    badge = get_flake8_badge(flake8_stats)
    badge.write_to(output_file if is_stdout else output_file_path, use_shields=webshields)

    if not silent and not is_stdout:
        click.echo("SUCCESS - Flake8 badge created: %r" % str(output_file_path))


def _process_infile(input_file, default_in_file):
    """Common in file processor"""

    if input_file is None:
        input_file = default_in_file

    if isinstance(input_file, str):
        input_file_path = Path(input_file).absolute().as_posix()
    else:
        input_file_path = getattr(input_file, "name", "<stdin>")

    return input_file, input_file_path


def _process_outfile(output_file, default_out_file):
    """Common out file processor"""

    is_stdout = False
    if output_file is None:
        output_file_path = Path(default_out_file).absolute()
    elif isinstance(output_file, str):
        output_file_path = Path(output_file).absolute()
        # special case of a directory
        if output_file_path.is_dir():
            output_file_path = output_file_path / default_out_file
    else:
        output_file_path = getattr(output_file, "name", "<stdout>")
        if output_file_path == "<stdout>":
            is_stdout = True
        else:
            output_file_path = Path(output_file_path).absolute()

    if not is_stdout:
        output_file_path = output_file_path.as_posix()

    return output_file, output_file_path, is_stdout


if __name__ == '__main__':
    genbadge()
