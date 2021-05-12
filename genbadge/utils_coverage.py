#  Authors:
#            Sylvain MARIE <sylvain.marie@se.com>
#            + All contributors to <https://github.com/smarie/python-genbadge>
#
#  License: 3-clause BSD, <https://github.com/smarie/python-genbadge/blob/master/LICENSE>

from .utils_badge import Badge
from xml.etree import ElementTree


class CoverageStats(object):
    """
    Contains the results from parsing the coverage.xml.
    """
    def __init__(self,
                 branch_rate=None, branches_covered=None, branches_valid=None,
                 complexity=None, line_rate=None, lines_covered=None, lines_valid=None
                 ):
        self.branch_rate = branch_rate
        self.branches_covered = branches_covered
        self.branches_valid = branches_valid
        self.complexity = complexity
        self.line_rate = line_rate
        self.lines_covered = lines_covered
        self.lines_valid = lines_valid

    @property
    def branch_coverage(self):
        return self.branch_rate * 100

    @property
    def line_coverage(self):
        return self.line_rate * 100


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

    if cov_stats.line_coverage < 50:
        color = 'red'
    elif cov_stats.line_coverage < 75:
        color = 'orange'
    elif cov_stats.line_coverage < 90:
        color = 'green'
    else:
        color = 'brightgreen'

    return color


def get_coverage_badge(
    cov_stats  # type: CoverageStats
):
    # type: (...) -> Badge
    """Return the badge from coverage results """

    color = get_color(cov_stats)

    right_txt = "%.2f%%" % (cov_stats.line_coverage,)

    return Badge(left_txt="coverage", right_txt=right_txt, color=color)


def parse_cov(source):
    """Parses the coverage.xml contents from source"""
    return CovParser().parse(source)


class CovParser(object):
    """Parser class - inspired by the code in `xunitparser`"""

    def parse(self, source):
        xml = ElementTree.parse(source)
        root = xml.getroot()
        return self.parse_root(root)

    def parse_root(self, root):
        cov = CoverageStats()
        assert root.tag == 'coverage'

        cov.branch_rate = float(root.attrib.get('branch-rate'))
        cov.branches_covered = int(root.attrib.get('branches-covered'))
        cov.branches_valid = int(root.attrib.get('branches-valid'))

        cov.complexity = float(root.attrib.get('complexity'))

        cov.line_rate = float(root.attrib.get('line-rate'))
        cov.lines_covered = int(root.attrib.get('lines-covered'))
        cov.lines_valid = int(root.attrib.get('lines-valid'))

        # for el in root:
        #     if el.tag == 'sources':
        #         self.parse_sources(el, ts)
        #     if el.tag == 'packages':
        #         self.parse_packages(el, ts)

        return cov