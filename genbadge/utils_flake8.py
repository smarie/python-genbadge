#  Authors:
#            Sylvain MARIE <sylvain.marie@se.com>
#            + All contributors to <https://github.com/smarie/python-genbadge>
#
#  License: 3-clause BSD, <https://github.com/smarie/python-genbadge/blob/master/LICENSE>

from __future__ import division

from warnings import warn
import re

from .utils_badge import Badge


try:
    # flake8-html is an optional dependency, do not fail if it cant be loaded
    import flake8_html
except ImportError as e:
    class FakeFlake8HtmlImport(object):
        def __getattribute__(self, item):
            raise ImportError("Could not import `flake8_html` module, please install it")
    flake8_html = FakeFlake8HtmlImport()


class Flake8Stats(object):
    """
    Contains the results from parsing the flake8 report.
    The severity levels are defined by flake8-html
    """
    def __init__(self,
                 nb_critical=0, nb_warning=0, nb_info=0
                 ):
        # severities 1, 2, 3
        self.nb_critical = nb_critical
        self.nb_warning = nb_warning
        self.nb_info = nb_info

    def add(self,
            nb,   # type: int
            code  # type: str
            ):
        """
        Add `nb` errors with the same code to the statistics.
        """
        severity = flake8_html.plugin.find_severity(code)
        if severity == 1:
            self.nb_critical += nb
        elif severity == 2:
            self.nb_warning += nb
        elif severity == 3:
            self.nb_info += nb
        else:
            raise ValueError("Unknown severity: %r for code %r" % (severity, code))

    @property
    def nb_total(self):
        return self.nb_critical + self.nb_warning + self.nb_info


def get_color(
        flake8_stats  # type: Flake8Stats
):
    """ Returns the badge color to use depending on the flake8 results """

    if flake8_stats.nb_critical > 0:
        color = 'red'
    elif flake8_stats.nb_warning > 0:
        color = 'orange'
    elif flake8_stats.nb_info > 0:
        color = 'green'
    else:
        color = 'brightgreen'

    return color


def get_flake8_badge(
    flake8_stats  # type: Flake8Stats
):
    # type: (...) -> Badge
    """Return the badge from coverage results """

    color = get_color(flake8_stats)

    right_txt = "%s C, %s W, %s I" % (flake8_stats.nb_critical, flake8_stats.nb_warning, flake8_stats.nb_info)

    return Badge(left_txt="flake8", right_txt=right_txt, color=color)


def get_flake8_stats(flake8_stats_file):
    # type: (...) -> Flake8Stats
    """
    Reads an index.html file obtained from flake8-html.
    """
    if isinstance(flake8_stats_file, str):
        # assume a file path
        with open(flake8_stats_file) as f:
            flake8_stats_txt = f.read()
    else:
        # assume a stream already
        flake8_stats_txt = flake8_stats_file.read()

    return parse_flake8_stats(flake8_stats_txt)


RE_TO_MATCH = re.compile(r"([0-9]+)\s+([A-Z0-9]+)\s.*")


def parse_flake8_stats(stats_txt  # type: str
                       ):
    # type: (...) -> Flake8Stats

    stats = Flake8Stats()
    for line in stats_txt.splitlines():
        match = RE_TO_MATCH.match(line)
        if not match:
            warn("Line in Flake8 statistics report does not match template and will be ignored: %r" % line)
        else:
            nb, code = match.groups()
            stats.add(int(nb), code)

    return stats


# def parse_flake8_html(html  # type: str
#                       ):
#     #
#     """Reads the flake8 html report"""
#     soup = bs4.BeautifulSoup(html, "html.parser")
#
#     # check title
#     title = soup.head.title.get_text()
#     assert title == 'flake8 violations', "Invalid flake8 html report found, unexpected title: %s" % title
#
#     # get page div
#     pagediv = soup.body.find("div", {"id": "page"})
#     assert pagediv.h1.get_text() == 'flake8 violations'
#
#     results_dct = dict()
#     ul_violations = pagediv.ul
#     for li in ul_violations.find_all('li'):
#         # synthesis
#         typ_str, severity_str = li.a.span['class']
#         assert typ_str == 'count'
#         assert severity_str.startswith('sev-')
#         count = int(li.a.span.get_text().strip())
#         worst_severity_nb = int(severity_str[4:])
#
#         count2, file_name = list(li.stripped_strings)
#         assert int(count2) == count
#
#         # we need to access the details because the count is not correct
#         li_href = li.a['href']
#         child_results_dct = parse_child_html(path, li_href)
#         for c_severity_nb, c_count in child_results_dct.items():
#             try:
#                 results_dct[c_severity_nb] += c_count
#             except KeyError:
#                 results_dct[c_severity_nb] = c_count
#
#         assert worst_severity_nb == min(child_results_dct.keys())
#         assert count == sum(child_results_dct.values())
#
#     return results_dct

#
# def parse_child_html(path,   # type: str
#                      suffix  # type: str
#                      ):
#     with open(path + suffix) as f:
#         html_child = f.read()
#     soup_child = bs4.BeautifulSoup(html_child, "html.parser")
#
#     # check title
#     title = soup_child.head.title.get_text()
#     assert title.startswith('flake8 violations'), "Invalid flake8 html report found, unexpected title: %s" % title
#
#     # get page div
#     pagediv = soup_child.body.find("div", {"id": "page"})
#     # assert pagediv.h1.get_text() == 'flake8 violations'
#
#     results_dct = dict()
#     ul_violations = pagediv.ul
#     for li in ul_violations.find_all('li', recursive=False):
#         code = li.a['data-code']  # F401, etc.
#         typ_str, severity_str = li.a.span['class']
#         assert typ_str == 'count'
#         assert severity_str.startswith('sev-')
#         count = int(li.a.span.get_text().strip())
#         severity_nb = int(severity_str[4:])
#
#         try:
#             results_dct[severity_nb] += count
#         except KeyError:
#             results_dct[severity_nb] = count
#
#     return results_dct
