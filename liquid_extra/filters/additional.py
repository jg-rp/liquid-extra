import json

from liquid.context import get_item

from liquid.filter import liquid_filter
from liquid.filter import with_context
from liquid.filter import with_environment


class JSON:
    """Serialize objects as a JSON (JavaScript Object Notation) formatted string.

    Args:
        default: A 'default' function passed to json.dumps. This function is called
            in the event that the JSONEncoder does not know how to serialize an object.
    """

    name = "json"

    def __init__(self, default=None):
        self.default = default

    @liquid_filter
    def __call__(self, obj):
        return json.dumps(obj, default=self.default)


@with_context
@with_environment
class Translate:
    """Replace translation keys with strings for the current locale.

    Tries to read the locale from the current template context, falling back to
    "default" if the key "locale" does not exist.

    Args:
        locales: A mapping of locale name to translation key mapping. If locales
            is `None`, the default, the translation key will be returned unchanged.
    """

    name = "t"

    def __init__(self, locales=None):
        self.locales = locales or {}

    @liquid_filter
    def __call__(self, key, *, context, environment, **kwargs):
        locale = context.resolve("locale", default="default")
        translations = self.locales.get(locale, {})

        key = str(key)
        path = key.split(".")

        val = get_item(translations, *path, default=key)  # type: ignore
        return environment.from_string(val).render(**kwargs)
