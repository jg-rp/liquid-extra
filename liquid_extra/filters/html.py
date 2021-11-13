import html

from liquid import Markup
from liquid import escape

from liquid.filter import string_filter
from liquid.filter import with_environment


@string_filter
@with_environment
def stylesheet_tag(url, *, environment):
    """Wrap a URL in an HTML stylesheet tag."""
    tag = '<link href="{}" rel="stylesheet" type="text/css" media="all" />'
    if environment.autoescape:
        return Markup(tag).format(escape(str(url)))
    return tag.format(html.escape(url))


@with_environment
@string_filter
def script_tag(url, *, environment):
    """Wrap a URL in an HTML script tag."""
    tag = '<script src="{}" type="text/javascript"></script>'
    if environment.autoescape:
        return Markup(tag).format(escape(str(url)))
    return tag.format(html.escape(url))
