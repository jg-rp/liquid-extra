Liquid Extra
============

A growing collection of extra tags and filters for `Python Liquid <https://github.com/jg-rp/liquid>`_.

.. image:: https://img.shields.io/pypi/v/python-liquid-extra.svg
    :target: https://pypi.org/project/python-liquid-extra/
    :alt: Version

.. image:: https://img.shields.io/pypi/l/python-liquid-extra.svg
    :target: https://pypi.org/project/python-liquid-extra/
    :alt: Licence

.. image:: https://img.shields.io/pypi/pyversions/python-liquid-extra.svg
    :target: https://pypi.org/project/python-liquid-extra/
    :alt: Python versions


- `Installing`_
- `Usage`_
  
Extra Tags

- `if (not)`_
- `macro / call`_
- `inline if / else (assign, echo and output statements)`_
- `with`_

Extra Filters

- `index`_
- `json`_
- `stylesheet_tag`_
- `script_tag`_
- `t (translate)`_

Installing
++++++++++

Install and update using `pip <https://pip.pypa.io/en/stable/quickstart/>`_:

.. code-block:: text

    $ python -m pip install -U python-liquid-extra


Usage
+++++

All filters and tags built-in to Liquid are registered automatically when you create a
new ``Environment``. If you register a new tag or filter with the same name as a
built-in one, the built-in tag or filter will be replaced without warning.

Filters
-------

Register a filter by calling the ``add_filter`` method of a ``liquid.Environment``. 
``add_filter`` takes two arguments. The first is the filter's name. This is what you'll
use to apply the filter to an expression in a liquid template. The second is any
callable that accepts at least one argument, the result of the left hand side of the
expression the filter is applied to.

.. code-block:: text

    add_filter(name: str, filter_: Callable[..., Any]) -> None

For example

.. code-block:: python

    from liquid import Environment
    from liquid_extra import filters

    env = Environment()
    env.add_filter("json", filters.JSON())

Or, if you're using `Flask-Liquid <https://github.com/jg-rp/Flask-Liquid>`_.

.. code-block:: python

    # saved as app.py
    from flask import Flask

    from flask_liquid import Liquid
    from flask_liquid import render_template

    from liquid_extra import filters

    app = Flask(__name__)

    liquid = Liquid(app)
    liquid.env.add_filter("json", filters.JSON())

    @app.route("/hello/")
    @app.route("/hello/<name>")
    def index(name=None):
        return render_template("index.html", name=name)

Equivalently, using `django-liquid <https://github.com/jg-rp/django-liquid>`_, if the
following is saved as ``myproject/liquid.py``

.. code-block:: python

    from liquid import Environment
    from liquid_extra import filters
    
    def environment(**options):
        env = Environment(**options)
        env.add_filter("json", filters.JSON())
        # Register more filters or tags here.
        return env

Then tell the django template backend to use your environment factory function in your
project's ``settings.py`` file.

.. code-block:: python

  TEMPLATES = [
      {
          'BACKEND': 'django_liquid.liquid.Liquid',
          'DIRS': [],
          'APP_DIRS': True,
          'OPTIONS': {
            'environment': 'myproject.liquid.environment'
          },
      },
  ]


Filters can be implemented as simple functions, classes with a ``__call__`` method or
closures that return a function or callable object. The latter two could take additional
arguments, some optional and some mandatory. Refer to the documentation for each filter
below to see what, if any, additional arguments they support.

Tags
----

Register a tag by calling the ``add_tag`` method of a ``liquid.Environment``. Note that 
``add_tag`` expects the tag class, not an instance of it.

.. code-block:: text

    add_tag(self, tag: Type[liquid.tag.Tag]) -> None


For example

.. code-block:: python

    from liquid import Environment
    from liquid_extra.tags import IfNotTag

    env = Environment()
    env.add_tag(IfNotTag)


Or, if you're using `Flask-Liquid`_.

.. code-block:: python

    # saved as app.py
    from flask import Flask

    from flask_liquid import Liquid
    from flask_liquid import render_template

    from liquid_extra.tags import IfNotTag

    app = Flask(__name__)

    liquid = Liquid(app)
    liquid.env.add_tag(IfNotTag)

    @app.route("/hello/")
    @app.route("/hello/<name>")
    def index(name=None):
        return render_template("index.html", name=name)


Some tags, like ``IfNot``, will replace standard, built-in tags. Others will introduce new
tags. Refer to the documentation for each tag below to see what features they add and/or
remove.


Extra Tags
++++++++++

if (not)
--------

A drop-in replacement for the standard ``if`` tag that supports logical ``not`` and grouping
with parentheses.

.. code-block:: python

    from liquid import Environment
    from liquid_extra.tags import IfNotTag

    env = Environment()
    env.add_tag(IfNotTag)

    template = env.from_string("""
        {% if not user %}
            please log in
        {% else %}
            hello user
        {% endif %}

        {% comment %}without parentheses{% endcomment %}
        {% if user != empty and user.eligible and user.score > 100 or exempt %}
            user is special
        {% else %}
            denied
        {% endif %}

        {% comment %}with parentheses{% endcomment %}
        {% if (user != empty and user.eligible and user.score > 100) or exempt %}
            user is special
        {% else %}
            denied
        {% endif %}
    """)

    user = {
        "eligible": False,
        "score": 5,
    }

    print(template.render(user=user, exempt=True))

Of course nested ``if`` and/or ``unless`` tags can be combined to work around the lack
of ``not`` in standard Liquid, but it does not always feel natural or intuitive.

Note that the ``not`` prefix operator uses Liquid `truthiness`. Only ``false`` and
``nil`` are not truthy. Empty strings, arrays and objects all evaluate to ``true``. You
can, however, use ``not`` in front of a comparison to ``empty`` or ``blank``.

.. code-block::

    {% if not something == empty %}
        ...
    {% endif %}

``and`` and ``or`` operators in Liquid are right associative. Where ``true and false and false
or true`` is equivalent to ``(true and (false and (false or true)))``, evaluating to ``false``.
Python, on the other hand, would parse the same expression as ``(((true and false) and false)
or true)``, evaluating to ``true``.

This implementation of ``if`` maintains that right associativity so that any standard ``if``
expression will behave the same, with or without non-standard ``if``. Only when ``not`` or
parentheses are used will behavior deviate from the standard.

inline if / else (assign, echo and output statements)
-----------------------------------------------------

Drop-in replacements for the standard output statement and ``assign`` and ``echo`` tags
that supports inline ``if``/``else`` expressions.

.. code-block:: python

    from liquid import Environment
    from liquid_extra.tags import InlineIfAssignTag
    from liquid_extra.tags import InlineIfEchoTag
    from liquid_extra.tags import InlineIfStatement

    env = Environment()
    env.add_tag(InlineIfAssignTag)
    env.add_tag(InlineIfEchoTag)
    env.add_tag(InlineIfStatement)

    template = env.from_string("""
        {{ 'hello user' if user.logged_in else 'please log in' }}
        {% assign message = 'hello user' if user.logged_in else 'please log in' %}
        {% echo 'hello user' if user.logged_in else 'please log in' %}

        {% comment %}else defaults to `undefined` if not provided.{% endcomment %}
        {{ 'hello user' if user.logged_in }}

        {% comment %}Filters can appear after the initial object.{% endcomment %}
        {{ 'hello user' | capitalize if user.logged_in else 'please log in' }}

        {% comment %}
            Or at the end of the expression. In which case filters will be applied even
            if the else clause is triggered.
        {% endcomment %}
        {{ 'hello user' if user.logged_in else 'please log in' | url_encode }}

        {% comment %}Or both{% endcomment %}
        {{ 'hello user' | capitalize if user.logged_in else 'please log in' | url_encode }}

        {% comment %}
            The condition can be any standard boolean expression.
        {% endcomment %}
        {{ 'you win' if user.score > 3 else 'you loose' }}

        {% comment %}
            And objects can be any liquid literal (like the strings thus far) or
            identifier.
        {% endcomment %}
        {{ user.messages[0] if user.messages else default_message }}
    """)

    user = {
        "score": 5,
        "messages": [],
        "logged_in": False
    }

    print(template.render(user=user, default_message="hello"))
    
For some, these inline conditions will be easier to read than the standard, longer form
``if``/``else`` tags. For example, one of the filtered statements from the (contrived)
example above would normally be written like this.

.. code-block::

    {% if user.logged_in %}
        {{ 'hello user' | capitalize | url_encode }}
    {% else %}
        {{ 'please log in' | url_encode }}
    {% endif %}

Note that if the condition evaluates to ``false`` (Liquid truthiness), the leading
object is not evaluated. Equally, if the condition evaluates to ``true``, any ``else``
object is not evaluated. This is not terribly important if the objects are Liquid
literals or simple Python objects, but could matter if the objects are custom drops that
do time consuming IO or processing.


macro / call
------------

Define parameterized Liquid snippets using the ``macro`` tag and call them using the
``call`` tag. Macros are intended to make code reuse easier, especially for small Liquid
snippets that are only needed within one template.

``macro`` is a bit like the standard ``capture`` tag, where a block is stored on the
render context for later use. Unlike ``capture``, ``macro`` accepts parameters,
possibly with default values, and the block is not evaluated until it is called using
a ``call`` tag.

``call`` is a bit like ``render``, in that a new context is created including any 
arguments supplied in the ``call`` expression. That context is then used to render the
named macro. Unlike ``render``, ``call`` can take positional arguments and does not hit
any template loader or the template cache.

Similar to ``include`` and ``render``, ``macro`` and ``call`` take a string literal
identifying the macro, followed by zero or more arguments. Neither ``macro`` or ``call``
accept ``for`` or ``with``/``as`` style expressions.

.. code-block:: python

    from liquid import Environment
    from liquid import StrictUndefined

    from liquid_extra.tags import MacroTag
    from liquid_extra.tags import CallTag

    # Setting strict undefined is strongly recommended.
    env = Environment(undefined=StrictUndefined)
    env.add_tag(MacroTag)
    env.add_tag(CallTag)

    template = env.from_string("""
        {% macro 'price', product, on_sale: false %}
            <div class="price-wrapper">
            {% if on_sale %}
                <p>Was {{ product.regular_price | money }}</p>
                <p>Now {{ product.price | money }}</p>
            {% else %}
                <p>{{ product.price | money }}</p>
            {% endif %}
            </div>
        {% endmacro %}
        {% call 'price', products.some_shoes, on_sale: true %}
        {% call 'price', products.a_hat %}
    """)

    products = {
        "some_shoes": {
            "regular_price": 599,
            "price": 399,
        },
        "a_hat": {
            "price": 50,
        }
    }

    print(template.render(products=products))

Excess arguments passed to ``call`` are collected into ``args`` and ``kwargs``, so
macros that handle an unknown number of arguments are possible.

Note that argument defaults are bound late. Defaults are evaluated when a ``call``
expression is evaluated, not when the macro is defined.

It's not uncommon for people to use ``include`` or ``render`` to load snippets of
Liquid in lieu of macros. It's worth noting that ..

- Macros don't need to exist on a file system or in a database.
- Macros can be defined within the template that's using them.
- Multiple, common macros can be defined in one template and included in others when
  needed.

with
----

Extend the local namespace with block scoped variables.

.. code-block:: python

    from liquid import Environment
    from liquid import StrictUndefined

    from liquid_extra.tags import WithTag

    env = Environment(undefined=StrictUndefined)
    env.add_tag(WithTag)

    template = env.from_string("""
        {% with p: collection.products.first %}
          {{ p.title }}
        {% endwith %}
        {{ p.title }}

        {% with a: 1, b: 3.4 %}
          {{ a }} + {{ b }} = {{ a | plus: b }}
        {% endwith %}
    """)

    data = {"collection": {"products": [{"title": "A Shoe"}]}}
    print(template.render(**data))

Extra Filters
+++++++++++++

index
-----

Return the first zero-based index of an item in an array. Or None if the item is not in the array.

.. code-block:: python

    from liquid import Environment
    from liquid_extra import filters

    env = Environment()
    env.add_filter("index", filters.index)

    template = env.from_string("{{ colours | index 'blue' }}")

    context = {
        "colours": ["red", "blue", "green"],
    }

    print(template.render(**context))  # 1


json
----

Serialize objects as a JSON (JavaScript Object Notation) formatted string.

The ``json`` filter uses Python's default `JSONEncoder <https://docs.python.org/3.8/library/json.html#json.JSONEncoder>`_,
supporting ``dict``, ``list``, ``tuple``, ``str``, ``int``, ``float``, some Enums, ``True``,
``False`` and ``None``.

.. code-block:: python

    from liquid import Environment
    from liquid_extra import filters

    env = Environment()
    env.add_filter("json", filters.JSON())

    template = env.from_string("""
        <script type="application/json">
            {{ product | json }}
        </script>
    """)

    context = {
        "product": {
            "id": 1234,
            "name": "Football",
        },
    }

    print(template.render(**context))


.. code-block:: text

    <script type="application/json">
        {"product": {"id": 1234, "name": "Football"}}
    </script>


The ``JSON`` filter takes an optional ``default`` argument. ``default`` will be passed
to ``json.dumps`` and should be a function that gets called for objects that can't
otherwise be serialized. For example, this default function adds support for serializing 
`data classes <https://docs.python.org/3/library/dataclasses.html>`_.

.. code-block:: python

    from dataclasses import dataclass
    from dataclasses import asdict
    from dataclasses import is_dataclass

    from liquid import Environment
    from liquid_extra import filters

    env = Environment()

    def default(obj):
        if is_dataclass(obj):
            return asdict(obj)

    env.add_filter("json", filters.JSON(default=default))

    template = env.from_string("""
        <script type="application/json">
            {{ product | json }}
        </script>
    """)

    @dataclass
    class Product:
        id: int
        name: str

    print(template.render(product=Product(1234, "Football")))


stylesheet_tag
--------------

Wrap a URL in an HTML stylesheet tag.

.. code-block:: python

    from liquid import Environment
    from liquid_extra import filters

    env = Environment()
    env.add_filter("stylesheet_tag", filters.stylesheet_tag)

    template = env.from_string("{{ url | stylesheet_tag }}")

    context = {
        "url": "https://example.com/static/style.css",
    }

    print(template.render(**context))


.. code-block:: text

    <link href="https://example.com/static/style.css" rel="stylesheet" type="text/css" media="all" />


script_tag
----------

Wrap a URL in an HTML script tag.

.. code-block:: python

    from liquid import Environment
    from liquid_extra import filters

    env = Environment()
    env.add_filter("script_tag", filters.script_tag)

    template = env.from_string("{{ url | script_tag }}")

    context = {
        "url": "https://example.com/static/app.js",
    }

    print(template.render(**context))


.. code-block:: text

    <script src="https://example.com/static/app.js" type="text/javascript"></script>


t (translate)
-------------

Replace translation keys with strings for the current locale.

Pass a mapping of locales to translations to the ``Translate`` filter when you register
it with a ``liquid.Environment``. The current locale is read from the template context at
render time.

.. code-block:: python

    from liquid import Environment
    from liquid_extra.filters import Translate

    some_locales = {
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

    env = Environment()
    env.add_filter(Translate.name, Translate(locales=some_locales))

    template = env.from_string("{{ 'layout.greeting' | t: name: user.name }}")

    # Defaults to the "default" locale.
    print(template.render(user={"name": "World"}))  # -> "Hello World"

    # Use the "locale" context key to specify the current locale.
    print(template.render(locale="de", user={"name": "Welt"}))  # -> "Hallo Welt"


Notice that the ``t`` filter accepts arbitrary named parameters. Named parameters can be
used to substitute fields in translation strings with values from the template context.

It you don't give ``Translate`` any locales or you leave it empty, you'll always get the
translation key back unchanged.


