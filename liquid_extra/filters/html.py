"""Extra HTML filters."""
import html

from liquid import Markup
from liquid import escape

from liquid.filter import string_filter
from liquid.filter import with_environment

from liquid import Environment


@string_filter
@with_environment
def stylesheet_tag(url: str, *, environment: Environment) -> str:
    """Wrap a URL in an HTML stylesheet tag."""
    tag = '<link href="{}" rel="stylesheet" type="text/css" media="all" />'
    if environment.autoescape:
        # We are deliberately forcing possible Markup strings to normal strings. We do
        # not want markup in the middle of a link tag.
        return Markup(tag).format(escape(str(url)))
    return tag.format(html.escape(url))


@string_filter
@with_environment
def script_tag(url: str, *, environment: Environment) -> str:
    """Wrap a URL in an HTML script tag."""
    tag = '<script src="{}" type="text/javascript"></script>'
    if environment.autoescape:
        # We are deliberately forcing possible Markup strings to normal strings. We do
        # not want markup in the middle of a script tag.
        return Markup(tag).format(escape(str(url)))
    return tag.format(html.escape(url))
