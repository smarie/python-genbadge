try:
    from pathlib import Path
except ImportError:  # pragma: no cover
    from pathlib2 import Path  # python 2

import click


@click.group()
def genbadge():
    """
    Commandline utility to generate badges.
    To get help on each command use:

        genbadge <cmd> --help

    """
    pass


@genbadge.command(name="junit")
@click.option('-f', '--input_file', type=click.File('rt'))
@click.option('-o', '--output_file', type=click.Path())
@click.option('-t', '--threshold', type=int)
def gen_junit_badge(
        input_file=None,
        output_file=None,
        threshold=None
):
    """

    :param junit_xml_file:
    :param dest_folder:
    :param threshold:
    :return:
    """
    from genbadge.utils_junit import get_test_stats, get_tests_badge

    # output file
    DEFAULT_BADGE_FILE = "junit-badge.svg"
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
        input_file_path = input_file.name

    # First retrieve the success percentage from the junit xml
    test_stats = get_test_stats(junit_xml_file=input_file)
    click.echo("""Test Stats parsed successfully.
 - Source file: %r
 - Nb tests: Total (%s) = Success (%s) + Skipped (%s) + Failed (%s) + Errors (%s)
 - Success percentage: %.2f%%
""" % (input_file_path, test_stats.total, test_stats.success, test_stats.skipped, test_stats.failed, test_stats.errors,
       test_stats.success_percentage))

    # sanity check
    if test_stats.total != test_stats.success + test_stats.skipped + test_stats.failed + test_stats.errors:
        raise click.exceptions.UsageError("Inconsistent junit results: the sum of all kind of tests is not equal to the"
                                          " total. Please report this issue if you think your file is correct. Details:"
                                          " %r" % test_stats)

    # Validate against the threshold
    if threshold is not None and test_stats.success_percentage < threshold:
        raise click.exceptions.UsageError("Success percentage %s%% is strictly lower than required threshold %s%%"
                                          % (test_stats.success_percentage, threshold))

    # Generate the badge
    # Old way: call shields.io.   download_badge(test_stats, dest_folder=dest_folder or ".")
    # New way: use the template
    badge = get_tests_badge(test_stats)
    badge.write_to(output_file_path)

    click.echo("JUnit badge created: %r" % str(output_file_path.absolute().as_posix()))


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
