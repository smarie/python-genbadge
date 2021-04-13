from genbadge.utils_badge import Badge


def test_genbadge():
    b = Badge(left_txt="verytring", right_txt="1XYZ", color="green")
    b.write_to("tmp_badge.svg", shields_version=False)
