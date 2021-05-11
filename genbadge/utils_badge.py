from PIL import ImageFont

try:
    from pathlib import Path
except ImportError:  # pragma: no cover
    from pathlib2 import Path  # python 2

try:
    # python 3
    from urllib.parse import quote_plus
except ImportError:
    # python 2
    from urllib import quote_plus

try:
    from typing import Union
except ImportError:  # pragma: no cover
    pass

from pkg_resources import resource_string, resource_filename


COLORS = {
    'brightgreen': '#4c1',
    'green': '#97CA00',
    'yellowgreen': '#a4a61d',
    'yellow': '#dfb317',
    'orange': '#fe7d37',
    'red': '#e05d44',
    'lightgrey': '#9f9f9f',
}


class Badge:
    """
    A small utility class for badges
    """
    def __init__(self,
                 left_txt,   # type: str
                 right_txt,  # type: str
                 color,      # type: str
                 ):
        self.left_txt = left_txt
        self.right_txt = right_txt
        self.color = color

    def __repr__(self):
        return "[ %s | %s ]  color: %s" % (self.left_txt, self.right_txt, self.color)

    def as_svg(self,
               shields_version=False  # type: bool
               ):
        """Return a string containing the SVG representation of this badge

        :param shields_version:
        :return:
        """
        if not shields_version:
            # generate from our local file template
            return get_svg_badge(label_txt=self.left_txt, msg_txt=self.right_txt, color=self.color)
        else:
            # download from requests
            import requests
            url = 'https://img.shields.io/badge/%s-%s-%s.svg' % (self.left_txt, quote_plus(self.right_txt), self.color)
            response = requests.get(url, stream=True)
            return response.text

    def write_to(self,
                 path,                  # type: Union[str, Path]
                 shields_version=False  # type: bool
                 ):
        """Write the SVG representation of this badge to the given file

        :param path:
        :param shields_version:
        :return:
        """
        # convert to a Path
        if isinstance(path, str):
            path = Path(path)

        # create parent dirs if needed
        path.parent.mkdir(parents=True, exist_ok=True)

        # finally write to
        with open(str(path), mode="wb") as f:
            f.write(self.as_svg(shields_version=shields_version).encode("utf-8"))


def get_svg_badge(
        label_txt,    # type: str
        msg_txt,   # type: str
        color,       # type: str
        label_color=None
):
    # type: (...) -> str
    """
    Reads the SVG template from the package,
    fills the various information from args and returns the svg string
    """
    all_text = "%s: %s" % (label_txt, msg_txt) if label_txt else ("%s" % msg_txt)

    # Same principle as in shields.io
    template_path = "badge-template.svg"
    template = resource_string(__name__, template_path).decode('utf8')

    horiz_padding = 5
    vertical_margin = 0

    has_logo = False  # TODO when a logo is inserted
    total_logo_width = 0

    has_label = len(label_txt) > 0 or label_color
    label_color = label_color or '#555'
    label_margin = total_logo_width + 1

    def process_text(left_margin, content):
        """From renderText()
        https://github.com/badges/shields/blob/4415d07e8b5bf794e6675cea052cc644d0c81bb5/badge-maker/lib/badge-renderers.js#L113
        """
        text_length = preferred_width_of(content, font_size=11, font_name="Verdana")
        # todo content = escape_xml(content)
        shadow_margin = 150 + vertical_margin
        text_margin = 140 + vertical_margin
        out_text_length = 10 * text_length
        x = 10 * (left_margin + 0.5 * text_length + horiz_padding)
        return x, shadow_margin, text_margin, text_length, out_text_length

    label_x, label_shadow_margin, label_text_margin, label_width, label_text_length = \
        process_text(label_margin, content=label_txt)

    left_width = (label_width + 2 * horiz_padding + total_logo_width) if has_label else 0

    msg_margin = left_width - (1 if len(msg_txt) > 0 else 0)
    if not has_label:
        if has_logo:
            msg_margin = msg_margin + total_logo_width + horiz_padding
        else:
            msg_margin = msg_margin + 1

    msg_x, msg_shadow_margin, msg_text_margin, msg_width, msg_text_length = \
        process_text(msg_margin, content=msg_txt)

    right_width = (msg_width + 2 * horiz_padding)
    if (has_logo and not has_label):
        right_width += total_logo_width + horiz_padding - 1

    total_width = left_width + right_width

    to_replace = {
        "title": all_text,
        "label_color": get_color(label_color),
        "color": get_color(color),
        "total_width": total_width,
        "left_width": left_width,
        "right_width": right_width,
        # label text
        "left_x": label_x,
        "left_shadow_margin": label_shadow_margin,
        "left_text_margin": label_text_margin,
        "left_out_text_length": label_text_length,
        "left_text": label_txt,
        # msg text
        "right_x": msg_x,
        "right_shadow_margin": msg_shadow_margin,
        "right_text_margin": msg_text_margin,
        "right_out_text_length": msg_text_length,
        "right_text": msg_txt
    }
    for k, v in to_replace.items():
        template = template.replace("{{ %s }}" % k, str(v))

    return template


def get_color(color_str):
    try:
        color_hexa = COLORS[color_str]
    except KeyError:
        # assume custom hexa string already
        color_hexa = color_str

    return color_hexa


def round_up_to_odd(val):
    return (val + 1) if (val % 2 == 0) else val


def preferred_width_of(txt, font_name, font_size):
    # Increase chances of pixel grid alignment.
    font_file = "%s.ttf" % font_name.lower()
    try:
        # Try from name only
        font = ImageFont.truetype(font=font_file, size=font_size)
    except OSError:
        # not found: use the embedded one in the package
        font_path = resource_filename(__name__, font_file)
        font = ImageFont.truetype(font=font_path, size=font_size)
    width = font.getsize(txt)[0]
    return round_up_to_odd(width)
