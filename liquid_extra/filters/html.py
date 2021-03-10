from liquid.filter import Filter
from liquid.filter import string_required
from liquid.filter import no_args


class StylesheetTag(Filter):
    """Wrap a URL in an HTML stylesheet tag."""

    name = "stylesheet_tag"

    @string_required
    @no_args
    def __call__(self, url):
        return f'<link href="{url}" rel="stylesheet" type="text/css" media="all" />'


class ScriptTag(Filter):
    """Wrap a URL in an HTML script tag."""

    name = "script_tag"

    @string_required
    @no_args
    def __call__(self, url):
        return f'<script src="{url}" type="text/javascript"></script>'
