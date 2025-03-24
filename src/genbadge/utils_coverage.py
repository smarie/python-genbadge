#  Authors: Sylvain MARIE <sylvain.marie@se.com>
#            + All contributors to <https://github.com/smarie/python-genbadge>
#
#  License: 3-clause BSD, <https://github.com/smarie/python-genbadge/blob/master/LICENSE>
from __future__ import division

from .utils_badge import Badge

try:
    # security patch: see https://docs.python.org/3/library/xml.etree.elementtree.html
    import defusedxml.ElementTree as defused_etree
except ImportError as e:
    ee = e  # save it
    class FakeDefusedXmlImport(object):  # noqa
        def __getattribute__(self, item):
            raise ImportError("Could not import `defusedxml.ElementTree`, please install `defusedxml`. "
                              "Note that all dependencies for the coverage command can be installed with "
                              "`pip install genbadge[coverage]`. Caught: %r" % ee)
    defused_etree = FakeDefusedXmlImport()


class CoverageStats(object):
    """
    Contains the results from parsing the coverage.xml.
    """
    def __init__(self,
                 branches_covered=None, branches_valid=None, branch_option=None,
                 complexity=None, lines_covered=None, lines_valid=None,
                 ):
        self.complexity = complexity

        self.branches_covered = branches_covered
        self.branches_valid = branches_valid
        self.branch_option = branch_option

        self.lines_covered = lines_covered
        self.lines_valid = lines_valid

    @property
    def branch_rate(self):
        """
        Note: in --no-branch situations, the number of branches is 0.
        In that case, the branch rate is 0 in the coverage.xml.
        But in --branch situations without actual branches,
        the number of branches is also 0 but the branch rate is 1.
        We mimic both behaviours in this field to be consistent.
        """
        if self.branches_valid > 0:
            return self.branches_covered / self.branches_valid
        elif self.branch_option:
            return 1
        else:
            return 0

    @property
    def line_rate(self):
        """See branch rate for the special case of division by zero"""
        if self.lines_valid > 0:
            return self.lines_covered / self.lines_valid
        else:
            return 0

    @property
    def branch_coverage(self):
        return self.branch_rate * 100

    @property
    def line_coverage(self):
        return self.line_rate * 100

    @property
    def total_rate(self):
        """
        See XmlReport class in https://github.com/nedbat/coveragepy/blob/master/coverage/xmlreport.py
        for the formula.

        See branch rate for the special case of division by zero.
        """
        denom = self.lines_valid + self.branches_valid
        if denom > 0:
            return (self.lines_covered + self.branches_covered) / denom
        else:
            return 0

    @property
    def total_coverage(self):
        return self.total_rate * 100


def get_coverage_stats(coverage_xml_file):
    # type: (...) -> CoverageStats
    """
    Reads a coverage.xml file

    <coverage branch-rate="0.6" branches-covered="24" branches-valid="40" complexity="0" line-rate="0.8586"
              lines-covered="170" lines-valid="198" timestamp="1620747625339" version="5.5">
    </coverage>
    """
    if isinstance(coverage_xml_file, str):
        # assume a file path
        with open(coverage_xml_file) as f:
            cov_stats = parse_cov(f)
    else:
        # assume a stream already
        cov_stats = parse_cov(coverage_xml_file)

    return cov_stats


def get_color(
        cov_stats  # type: CoverageStats
):
    """ Returns the badge color to use depending on the coverage rate """

    if cov_stats.total_coverage < 50:
        color = 'red'
    elif cov_stats.total_coverage < 75:
        color = 'orange'
    elif cov_stats.total_coverage < 90:
        color = 'green'
    else:
        color = 'brightgreen'

    return color


def get_coverage_badge(
    cov_stats,  # type: CoverageStats
    left_txt= "coverage" # type: str
):
    # type: (...) -> Badge
    """Return the badge from coverage results """

    color = get_color(cov_stats)

    right_txt = "%.2f%%" % (cov_stats.total_coverage,)

    return Badge(left_txt=left_txt, right_txt=right_txt, color=color)


def parse_cov(source):
    """Parses the coverage.xml contents from source"""
    return CovParser().parse(source)


class CovParser(object):
    """Parser class - inspired by the code in `xunitparser`"""

    def parse(self, source):
        xml = defused_etree.parse(source)
        root = xml.getroot()
        return self.parse_root(root)

    def parse_root(self, root):
        cov = CoverageStats()
        assert root.tag == 'coverage'

        cov.complexity = float(root.attrib.get('complexity'))

        cov.branches_covered = int(root.attrib.get('branches-covered'))
        cov.branches_valid = int(root.attrib.get('branches-valid'))

        cov.lines_covered = int(root.attrib.get('lines-covered'))
        cov.lines_valid = int(root.attrib.get('lines-valid'))

        # recompute the rates for more precision, but make sure that's correct
        branch_rate = float(root.attrib.get('branch-rate'))
        line_rate = float(root.attrib.get('line-rate'))

        # detect whether the --branch option were set or not
        # so CoverageStats knows how to distinguish between them
        cov.branch_option = cov.branches_valid > 0 or branch_rate == 1.0

        if not is_close(cov.branch_rate, branch_rate):
            raise ValueError("Computed branch rate (%s) is different from the one in the file (%s)"
                             % (cov.branch_rate, branch_rate))
        if not is_close(cov.line_rate, line_rate):
            raise ValueError("Computed line rate (%s) is different from the one in the file (%s)"
                             % (cov.line_rate, line_rate))

        # for el in root:
        #     if el.tag == 'sources':
        #         self.parse_sources(el, ts)
        #     if el.tag == 'packages':
        #         self.parse_packages(el, ts)

        return cov


def is_close(a, b):
    """Return True if there is at most a difference of 1 at the 2d decimal"""
    return abs(a - b) <= 0.01
