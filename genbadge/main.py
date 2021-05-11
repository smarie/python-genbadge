try:
    from pathlib import Path
except ImportError:  # pragma: no cover
    from pathlib2 import Path  # python 2

import click


from .utils_junit import get_test_stats, get_tests_badge

try:
    FileNotFoundError
except NameError:
    FileNotFoundError = IOError


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
@click.option('-i', '--input-file', type=click.File('rt'), help="")
@click.option('-o', '--output-file', type=click.Path(), help="")
@click.option('-t', '--threshold', type=float, help="")
@click.option('-w/-l', '--webshields/--local', type=bool, help="", default=True)
# TODO -s --stdout
# TODO -f --format
def gen_tests_badge(
        input_file=None,
        output_file=None,
        threshold=None,
        webshields=None
):
    """
    This command generates a badge for the test results, from an XML file in the
    junit format. Such a file can be for example generated from pytest using the
    --junitxml flag.

    By default the input file is the relative `./reports/junit/junit.xml` and
    the output file is `./tests-badge.svg`. You can change these settings with
    the `-i/--input_file` and `-o/--output-file` options.

    The resulting badge will by default look like this: [tests | 6/12]
    where 6 is the number of tests that have run successfully, and 12 is the
    total number of tests minus the number of skipped tests. You can change the
    appearance of the badge with the --format option (not implemented, todo).

    The success percentage is defined as 6/12 = 50.0%. You can use the
    `-t/--threshold` flag to setup a minimum success percentage required. If the
    success percentage is below the threshold, an error will be raised and the
    badge will not be generated.
    """
    # output file
    DEFAULT_BADGE_FILE = "tests-badge.svg"
    if output_file is None:
        output_file_path = Path(DEFAULT_BADGE_FILE)
    else:
        output_file_path = Path(output_file)
        if output_file_path.is_dir():
            output_file_path = output_file_path / DEFAULT_BADGE_FILE
    # if output_file_path.exists():
    #     answer = input("")

    # input file and its name
    if input_file is None:
        input_file = 'reports/junit/junit.xml'

    if isinstance(input_file, str):
        input_file_path = Path(input_file).absolute().as_posix()
    else:
        input_file_path = getattr(input_file, "name", "<stdin>")

    # First retrieve the success percentage from the junit xml
    try:
        test_stats = get_test_stats(junit_xml_file=input_file)
    except FileNotFoundError:
        raise click.exceptions.FileError(input_file, hint="File not found")

    # TODO if verbose and not stdout
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
    # Old way: call shields.io.   download_badge(test_stats, dest_folder=dest_folder or ".")
    # New way: use the template
    badge = get_tests_badge(test_stats)
    badge.write_to(output_file_path, use_shields=webshields)

    click.echo("SUCCESS - Tests badge created: %r" % str(output_file_path.absolute().as_posix()))


# @genbadge.command(name="flake8")
# # @click.option('-p', '--platform_id', default='public', help="Specific ODS platform id. Default 'public'")
# # @click.option('-b', '--base_url', default=None, help="Specific ODS base url. Default: "
# #                                                      "https://<platform_id>.opendatasoft.com/")
# # @click.option('-u', '--username', default=KR_DEFAULT_USERNAME, help='Custom username to use in the keyring entry. '
# #                                                                     'Default: %s' % KR_DEFAULT_USERNAME)
# def gen_flake8_badge(platform_id,                   # type: str
#                      base_url,                      # type: str
#                      username=KR_DEFAULT_USERNAME,  # type: str
#                      ):
#     """
#     Looks up an ODS apikey entry in the keyring. Custom ODS platform id or base url can be provided through options.
#     """
#
#     if apikey is not None:
#         click.echo("Api key found for platform url '%s': %s" % (url_used, apikey))
#     else:
#         click.echo("No api key registered for platform url '%s'" % (url_used, ))


if __name__ == '__main__':
    genbadge()
