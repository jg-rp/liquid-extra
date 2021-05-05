import html
import warnings

from liquid import Markup
from liquid import escape

from liquid.filter import string_filter
from liquid.filter import with_environment

from liquid.filter import Filter
from liquid.filter import string_required
from liquid.filter import no_args


class StylesheetTag(Filter):
    """Wrap a URL in an HTML stylesheet tag."""

    name = "stylesheet_tag"

    def __init__(self, env):
        super().__init__(env)
        warnings.warn(
            "the class-based `StylesheetTag` filter is depreciated and will be removed "
            "in a future release. Please use ``liquid_extra.filters.stylesheet_tag`` "
            "instead.",
            DeprecationWarning,
            stacklevel=2,
        )

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

    def __init__(self, env):
        super().__init__(env)
        warnings.warn(
            "the class-based `ScriptTag` filter is depreciated and will be removed in "
            "a future release. Please use ``liquid_extra.filters.script_tag`` instead.",
            DeprecationWarning,
            stacklevel=2,
        )

    @string_required
    @no_args
    def __call__(self, url):
        tag = '<script src="{}" type="text/javascript"></script>'
        if self.env.autoescape:
            return Markup(tag).format(escape(str(url)))
        return tag.format(html.escape(url))


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
