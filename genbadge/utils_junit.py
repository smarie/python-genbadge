#  Authors: Sylvain MARIE <sylvain.marie@se.com>
#            + All contributors to <https://github.com/smarie/python-genbadge>
#
#  License: 3-clause BSD, <https://github.com/smarie/python-genbadge/blob/master/LICENSE>
from __future__ import division

from io import TextIOWrapper
from math import floor

try:
    from typing import Union
except ImportError:
    pass

try:
    # xunitparser is an optional dependency, do not fail if it cant be loaded
    import xunitparser
except ImportError as e:
    class FakeXunitParserImport(object):
        def __getattribute__(self, item):
            raise ImportError("Could not import `xunitparser` module, please install it")
    xunitparser = FakeXunitParserImport()

from .utils_badge import Badge


class TestStats(object):
    """
    Contains the results from parsing the Junit style test report (junit.xml).
    Some stats are available as properties, computed based on others.
    """
    def __init__(self, runned, skipped, failed, errors):
        self.runned = runned
        self.failed = failed
        self.skipped = skipped
        self.errors = errors

    @property
    def success(self):
        return self.runned - self.skipped - self.failed

    @property
    def total_with_skipped(self):
        return self.runned + self.errors

    @property
    def total_without_skipped(self):
        return self.runned - self.skipped + self.errors

    @property
    def success_percentage(self):
        if self.runned > 0:
            return self.success * 100 / self.total_without_skipped
        else:
            return 100

    def __repr__(self):
        return "%s(%s)" % (self.__class__.__name__, ",".join("%s=%r" % (k, v) for k, v in vars(self).items()))


def get_test_stats(junit_xml_file='reports/junit/junit.xml'  # type: Union[str, TextIOWrapper]
                   ):
    # type: (...) -> TestStats
    """
    read the junit test file and extract the success percentage
    :param junit_xml_file: the junit xml file path or file/text stream
    :return: the success percentage (an int)
    """
    if isinstance(junit_xml_file, str):
        # assume a file path
        with open(junit_xml_file) as f:
            ts, tr = xunitparser.parse(f)
    else:
        # assume a stream already
        ts, tr = xunitparser.parse(junit_xml_file)

    runned = tr.testsRun
    skipped = len(tr.skipped)
    failed = len(tr.failures)
    errors = len(tr.errors)

    return TestStats(runned=runned, skipped=skipped, failed=failed, errors=errors)


def get_color(
        test_stats  # type: TestStats
):
    """ Returns the badge color to use depending on the success percentage """

    if test_stats.success_percentage < 50:
        color = 'red'
    elif test_stats.success_percentage < 75:
        color = 'orange'
    elif test_stats.success_percentage < 90:
        color = 'green'
    else:
        color = 'brightgreen'

    return color


def get_tests_badge(
        test_stats  # type: TestStats
):
    # type: (...) -> Badge
    """Return the badge from test statistics """

    color = get_color(test_stats)

    # right_txt = "%s%%" % test_stats.success_percentage
    right_txt = "%s/%s" % (test_stats.success, test_stats.total_without_skipped)

    return Badge(left_txt="tests", right_txt=right_txt, color=color)
