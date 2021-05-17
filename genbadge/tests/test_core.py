from __future__ import division

import platform
from distutils.version import LooseVersion
import PIL

import pytest

try:
    from pathlib import Path
except ImportError:  # pragma: no cover
    from pathlib2 import Path  # python 2


from genbadge import Badge
from genbadge.utils_badge import get_local_badge_template
from genbadge.utils_coverage import parse_cov
from genbadge.utils_junit import get_test_stats
from genbadge.utils_flake8 import get_flake8_stats


TESTS_FOLDER = Path(__file__).parent.absolute()


def test_access_pkg_resources():
    """Make sure accessing the resource from the package is ok"""
    get_local_badge_template()


@pytest.mark.parametrize("use_shields", [False],  # TODO True but the contents are slightly different
                         ids="use_shields={}".format)
def test_genbadge(tmpdir, use_shields):
    """Test that the `Badge` class works as expected"""

    b = Badge(left_txt="verytring", right_txt="1XYZ", color="green")

    # Console representation
    assert repr(b) == "[ verytring | 1XYZ ]  color: green"

    # SVG representation
    if platform.system() == "Windows" or LooseVersion(PIL.__version__) < "8.0":
        ref_nbs = dict(left_width=63, right_width=41, tot_width=104, left_x=325.0, left_txt_length=530, right_x=825.0, right_txt_length=310)
    else:
        ref_nbs = dict(left_width=61, right_width=39, tot_width=100, left_x=315.0, left_txt_length=510, right_x=795.0, right_txt_length=290)

    refsvg_str = """
<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="{tot_width}" height="20" role="img" aria-label="verytring: 1XYZ">
	<title>verytring: 1XYZ</title>
	<linearGradient id="s" x2="0" y2="100%">
		<stop offset="0" stop-color="#bbb" stop-opacity=".1"/>
		<stop offset="1" stop-opacity=".1"/>
	</linearGradient>
	<clipPath id="r">
		<rect width="{tot_width}" height="20" rx="3" fill="#fff"/>
	</clipPath>
	<g clip-path="url(#r)">
		<rect width="{left_width}" height="20" fill="#555"/>
		<rect x="{left_width}" width="{right_width}" height="20" fill="#97ca00"/>
		<rect width="{tot_width}" height="20" fill="url(#s)"/>
	</g>
	<g fill="#fff" text-anchor="middle" font-family="Verdana,Geneva,DejaVu Sans,sans-serif" text-rendering="geometricPrecision" font-size="110">
		<text aria-hidden="true" x="{left_x}" y="150" fill="#010101" fill-opacity=".3" transform="scale(.1)" textLength="{left_txt_length}">verytring</text>
		<text x="{left_x}" y="140" transform="scale(.1)" fill="#fff" textLength="{left_txt_length}">verytring</text>
		<text aria-hidden="true" x="{right_x}" y="150" fill="#010101" fill-opacity=".3" transform="scale(.1)" textLength="{right_txt_length}">1XYZ</text>
		<text x="{right_x}" y="140" transform="scale(.1)" fill="#fff" textLength="{right_txt_length}">1XYZ</text>
	</g>
</svg>""".format(**ref_nbs)  # noqa
    assert standardize_xml("\n" + b.as_svg(use_shields=use_shields)) == standardize_xml(refsvg_str)

    # Write to file
    b.write_to(str(tmpdir / "tmp_badge.svg"), use_shields=use_shields)
    with open(str(tmpdir / "tmp_badge.svg"), mode="rt") as f:
        svgtxt = f.read()
    assert standardize_xml("\n" + svgtxt) == standardize_xml(refsvg_str)


def standardize_xml(xmltxt):
    import xml.dom.minidom
    dom = xml.dom.minidom.parseString(xmltxt)  # or xml.dom.minidom.parseString(xml_string)
    return dom.toprettyxml()


def test_parse_tests():
    """Check that we can parse a coverage.xml file successfully"""
    res = get_test_stats(str(TESTS_FOLDER / "reports/junit/junit.xml"))

    # not runned at all
    assert res.errors == 1
    # runned
    assert res.runned == 5
    assert res.failed == 2
    assert res.success == 2
    assert res.skipped == 1

    assert res.total_with_skipped == res.runned + res.errors
    assert res.total_without_skipped == res.runned - res.skipped + res.errors

    assert res.success_percentage == res.success * 100 / res.total_without_skipped



def test_parse_cov():
    """Check that we can parse a coverage.xml file successfully"""
    res = parse_cov(str(TESTS_FOLDER / "reports/coverage/coverage.xml"))

    assert res.branches_valid == 18
    assert res.branches_covered == 1
    assert res.branch_rate == res.branches_covered / res.branches_valid

    assert res.lines_valid == 73
    assert res.lines_covered == 13
    assert res.line_rate == res.lines_covered / res.lines_valid

    assert res.branch_coverage == res.branch_rate * 100
    assert res.line_coverage == res.line_rate * 100

    assert res.total_rate == ((res.lines_covered + res.branches_covered) / (res.branches_valid + res.lines_valid))
    assert res.total_coverage == 100 * res.total_rate


def test_parse_flake8():
    """Check that we can parse a coverage.xml file successfully"""
    res = get_flake8_stats(str(TESTS_FOLDER / "reports/flake8/flake8stats.txt"))

    assert res.nb_critical == 6
    assert res.nb_warning == 9
    assert res.nb_info == 5

    assert res.nb_total == res.nb_critical + res.nb_warning + res.nb_info
