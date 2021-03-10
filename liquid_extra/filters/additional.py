import json

from liquid.context import get_item
from liquid.filter import Filter
from liquid.filter import no_args


class JSON(Filter):
    """Serialize objects as a JSON (JavaScript Object Notation) formatted string.

    Args:
        default: A 'default' function passed to json.dumps. This function is called
            in the event that the JSONEncoder does not know how to serialize an object.
    """

    name = "json"

    def __init__(self, env, default=None):
        super().__init__(env)
        self.default = default

    @no_args
    def __call__(self, obj):
        return json.dumps(obj, default=self.default)


class Translate(Filter):
    """Replace translation keys with strings for the current locale.

    Tries to read the locale from the current template context, falling back to
    "default" if the key "locale" does not exist.

    Args:
        locales: A mapping of locale name to translation key mapping. If locales
            is `None`, the default, the translation key will be returned unchanged.
    """

    name = "t"
    with_context = True

    def __init__(self, env, locales=None):
        super().__init__(env)
        self.locales = locales or {}

    def __call__(self, key, *, context, **kwargs):
        locale = context.resolve("locale", default="default")
        translations = self.locales.get(locale, {})

        key = str(key)
        path = key.split(".")

        val = get_item(translations, *path, default=key)
        return self.env.from_string(val).render(**kwargs)
