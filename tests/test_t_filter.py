"""Translation filter test cases."""
# pylint: disable=missing-class-docstring,missing-function-docstring

from liquid_extra.filters import Translate

from .base import FilterTestCase
from .base import RenderFilterTestCase
from .base import Case
from .base import RenderCase


mock_locales = {
    "default": {
        "layout": {
            "greeting": r"Hello {{ name }}",
        },
        "cart": {
            "general": {
                "title": "Shopping Basket",
            },
        },
        "pagination": {
            "next": "Next Page",
        },
    },
    "de": {
        "layout": {
            "greeting": r"Hallo {{ name }}",
        },
        "cart": {
            "general": {
                "title": "Warenkorb",
            },
        },
        "pagination": {
            "next": "Nächste Seite",
        },
    },
}


class TranslateFilterTestCase(FilterTestCase):
    """Test the Translate template filter."""

    def test_translate_filter(self) -> None:
        test_cases = [
            Case(
                description="default locale",
                val="cart.general.title",
                args=[],
                kwargs={},
                expect="Shopping Basket",
            ),
            Case(
                description="default locale missing key",
                val="foo.bar",
                args=[],
                kwargs={},
                expect="foo.bar",
            ),
            Case(
                description="default locale not a string",
                val=42,
                args=[],
                kwargs={},
                expect="42",
            ),
            Case(
                description="default locale interpopulate",
                val="layout.greeting",
                args=[],
                kwargs={"name": "World"},
                expect="Hello World",
            ),
        ]

        self.env.add_filter(Translate.name, Translate(locales=mock_locales))
        self._test(self.ctx.filter(Translate.name), test_cases)

    def test_translate_filter_with_locale(self) -> None:
        test_cases = [
            Case(
                description="de locale",
                val="cart.general.title",
                args=[],
                kwargs={},
                expect="Warenkorb",
            ),
            Case(
                description="de locale missing key",
                val="foo.bar",
                args=[],
                kwargs={},
                expect="foo.bar",
            ),
            Case(
                description="de locale not a string",
                val=42,
                args=[],
                kwargs={},
                expect="42",
            ),
            Case(
                description="de locale interpopulate",
                val="layout.greeting",
                args=[],
                kwargs={"name": "Welt"},
                expect="Hallo Welt",
            ),
        ]

        self.env.add_filter(Translate.name, Translate(locales=mock_locales))
        self.ctx.assign("locale", "de")
        self._test(self.ctx.filter(Translate.name), test_cases)


class RenderTranslateFilterTestCase(RenderFilterTestCase):
    """Test the Translate filter from a template."""

    def test_render_translate_filter(self) -> None:
        test_cases = [
            RenderCase(
                description="default locale",
                template=r"{{ 'cart.general.title' | t }}",
                expect="Shopping Basket",
                globals={},
                partials={},
            ),
            RenderCase(
                description="default locale missing key",
                template=r"{{ 'foobar' | t }}",
                expect="foobar",
                globals={},
                partials={},
            ),
            RenderCase(
                description="default locale interpopulate",
                template=r"{{ 'layout.greeting' | t: name: 'World' }}",
                expect="Hello World",
                globals={},
                partials={},
            ),
            RenderCase(
                description="default locale interpopulate from context",
                template=r"{{ 'layout.greeting' | t: name: user.name }}",
                expect="Hello World",
                globals={"user": {"name": "World"}},
                partials={},
            ),
            RenderCase(
                description="de locale",
                template=r"{{ 'cart.general.title' | t }}",
                expect="Warenkorb",
                globals={"locale": "de"},
                partials={},
            ),
        ]

        self._test(Translate(locales=mock_locales), test_cases)
