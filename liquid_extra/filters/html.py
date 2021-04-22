import html

from liquid import Markup
from liquid import escape

from liquid.filter import Filter
from liquid.filter import string_required
from liquid.filter import no_args


class StylesheetTag(Filter):
    """Wrap a URL in an HTML stylesheet tag."""

    name = "stylesheet_tag"

    @string_required
    @no_args
    def __call__(self, url):
        tag = '<link href="{}" rel="stylesheet" type="text/css" media="all" />'
        if self.env.autoescape:
            return Markup(tag).format(escape(str(url)))
        return tag.format(html.escape(url))


class ScriptTag(Filter):
    """Wrap a URL in an HTML script tag."""

    name = "script_tag"

    @string_required
    @no_args
    def __call__(self, url):
        tag = '<script src="{}" type="text/javascript"></script>'
        if self.env.autoescape:
            return Markup(tag).format(escape(str(url)))
        return tag.format(html.escape(url))
