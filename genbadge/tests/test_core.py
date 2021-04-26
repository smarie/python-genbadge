import pytest

from genbadge.utils_badge import Badge


@pytest.mark.parametrize("shields_version", [False],  # TODO, True],
                         ids="shields_version={}".format)
def test_genbadge(tmpdir, shields_version):
    """Test that the `Badge` class works as expected"""

    b = Badge(left_txt="verytring", right_txt="1XYZ", color="green")

    # Console representation
    assert repr(b) == "[ verytring | 1XYZ ]  color: green"

    # SVG representation
    refsvg_str = """
<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="104" height="20" role="img" aria-label="verytring: 1XYZ">
	<title>verytring: 1XYZ</title>
	<linearGradient id="s" x2="0" y2="100%">
		<stop offset="0" stop-color="#bbb" stop-opacity=".1"/>
		<stop offset="1" stop-opacity=".1"/>
	</linearGradient>
	<clipPath id="r">
		<rect width="104" height="20" rx="3" fill="#fff"/>
	</clipPath>
	<g clip-path="url(#r)">
		<rect width="63" height="20" fill="#555"/>
		<rect x="63" width="41" height="20" fill="#97ca00"/>
		<rect width="104" height="20" fill="url(#s)"/>
	</g>
	<g fill="#fff" text-anchor="middle" font-family="Verdana,Geneva,DejaVu Sans,sans-serif" text-rendering="geometricPrecision" font-size="110">
		<text aria-hidden="true" x="325.0" y="150" fill="#010101" fill-opacity=".3" transform="scale(.1)" textLength="530">verytring</text>
		<text x="325.0" y="140" transform="scale(.1)" fill="#fff" textLength="530">verytring</text>
		<text aria-hidden="true" x="825.0" y="150" fill="#010101" fill-opacity=".3" transform="scale(.1)" textLength="310">1XYZ</text>
		<text x="825.0" y="140" transform="scale(.1)" fill="#fff" textLength="310">1XYZ</text>
	</g>
</svg>"""  # noqa
    assert standardize_xml("\n" + b.as_svg(shields_version=shields_version)) == standardize_xml(refsvg_str)

    # Write to file
    b.write_to(str(tmpdir / "tmp_badge.svg"), shields_version=shields_version)
    with open(str(tmpdir / "tmp_badge.svg"), mode="rt") as f:
        svgtxt = f.read()
    assert standardize_xml("\n" + svgtxt) == standardize_xml(refsvg_str)


def standardize_xml(xmltxt):
    import xml.dom.minidom
    dom = xml.dom.minidom.parseString(xmltxt)  # or xml.dom.minidom.parseString(xml_string)
    return dom.toprettyxml()
