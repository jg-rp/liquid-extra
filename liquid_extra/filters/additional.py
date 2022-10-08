"""Some additional filters that don't belong to any specific category."""
import json

from typing import Any
from typing import Optional
from typing import Mapping

from liquid.context import get_item

from liquid.filter import liquid_filter
from liquid.filter import with_context
from liquid.filter import with_environment

from liquid import Environment
from liquid import Context


class JSON:  # pylint: disable=too-few-public-methods
    """Serialize objects as a JSON (JavaScript Object Notation) formatted string.

    Args:
        default: A 'default' function passed to json.dumps. This function is called
            in the event that the JSONEncoder does not know how to serialize an object.
    """

    name = "json"

    def __init__(self, default: Any = None):
        self.default = default

    @liquid_filter
    def __call__(self, obj: object) -> str:
        return json.dumps(obj, default=self.default)


@with_context
@with_environment
class Translate:  # pylint: disable=too-few-public-methods
    """Replace translation keys with strings for the current locale.

    Tries to read the locale from the current template context, falling back to
    "default" if the key "locale" does not exist.

    Args:
        locales: A mapping of locale name to translation key mapping. If locales
            is `None`, the default, the translation key will be returned unchanged.
    """

    name = "t"

    def __init__(self, locales: Optional[Mapping[str, Mapping[str, object]]] = None):
        self.locales: Mapping[str, Mapping[str, object]] = locales or {}

    @liquid_filter
    def __call__(
        self,
        key: object,
        *,
        context: Context,
        environment: Environment,
        **kwargs: Any,
    ) -> str:
        locale = context.resolve("locale", default="default")
        translations: Mapping[str, object] = self.locales.get(locale, {})

        key = str(key)
        path = key.split(".")

        val = get_item(translations, *path, default=key)  # type: ignore
        return environment.from_string(val).render(**kwargs)
