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
- `Extra Tags`_
    - `if (not)`_
- `Extra Filters`_
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

Liquid requires Python>=3.7 or PyPy3.7.

Usage
+++++

All filters and tags built-in to Liquid are registered automatically when you create a new 
``Environment``. If you register a new tag or filter with the same name as a built-in one,
the built-in tag or filter will be replaced without warning.

Filters
-------

Register a filter by calling the ``add_filter`` method of a ``liquid.Environment``.

    ``add_filter(name: str, fltr: Callable[..., Any]) -> None:``

    :name:
        The filter's name. Does not need to match the function or class name. This
        is what you'll use to apply the filter to an expression in a liquid template.
    :fltr:
        Any callable that accepts at least one argument, the result of the left hand
        side of the expression the filter is applied to.

For example

.. code-block:: python

    from liquid import Environment
    from liquid_extra.filters import JSON

    env = Environment()
    env.add_filter(JSON.name, JSON(env))

Or, if you're using `Flask-Liquid <https://github.com/jg-rp/Flask-Liquid>`_.

.. code-block:: python

    # saved as app.py
    from flask import Flask

    from flask_liquid import Liquid
    from flask_liquid import render_template

    from liquid_extra.filters import JSON

    app = Flask(__name__)

    liquid = Liquid(app)
    liquid.env.add_filter(JSON.name, JSON(liquid.env))

    @app.route("/hello/")
    @app.route("/hello/<name>")
    def index(name=None):
        return render_template("index.html", name=name)

Some filters take additional constructor arguments, some optional and some mandatory.
Refer to the documentation for each filter below to see what, if any, additional
arguments they support.

Tags
----

Register a tag by calling the ``add_tag`` method of a ``liquid.Environment``. Note that 
``add_tag`` expects the tag class, not an instance of it.

    ``add_tag(self, tag: Type[Tag]) -> None:``

    :tag: A subclass of ``liquid.tag.Tag``

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

Note that the ``not`` prefix operator uses Liquid `truthiness`. Only ``false`` and ``nil``
are not truthy. Empty strings, arrays and objects all evaluate to ``true``. You can, however,
use ``not`` in front of a comparison to ``empty`` or ``blank``.

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

Extra Filters
+++++++++++++

index
-----

Return the first zero-based index of an item in an array. Or None if the item is not in the array.

.. code-block:: python

    from liquid import Environment
    from liquid_extra.filters import Index

    env = Environment()
    env.add_filter(Index.name, Index(env))

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
    from liquid_extra.filters import JSON

    env = Environment()
    env.add_filter(JSON.name, JSON(env))

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


The ``JSON`` constructor takes an optional ``default`` argument. ``default`` will be
passed to ``json.dumps`` and should be a function that gets called for objects that can’t
otherwise be serialized. For example, this default function adds support for serializing 
`data classes <https://docs.python.org/3/library/dataclasses.html>`_.

.. code-block:: python

    from dataclasses import dataclass
    from dataclasses import asdict
    from dataclasses import is_dataclass

    from liquid import Environment
    from liquid_extra.filters import JSON

    env = Environment()

    def default(obj):
        if is_dataclass(obj):
            return asdict(obj)

    env.add_filter(JSON.name, JSON(env, default=default))

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
    from liquid_extra.filters import StylesheetTag

    env = Environment()
    env.add_filter(StylesheetTag.name, StylesheetTag(env))

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
    from liquid_extra.filters import ScriptTag

    env = Environment()
    env.add_filter(ScriptTag.name, ScriptTag(env))

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
    env.add_filter(Translate.name, Translate(env, locales=some_locales))

    template = env.from_string("{{ 'layout.greeting' | t: name: user.name }}")

    # Defaults to the "default" locale.
    print(template.render(user={"name": "World"}))  # -> "Hello World"

    # Use the "locale" context key to specify the current locale.
    print(template.render(locale="de", user={"name": "Welt"}))  # -> "Hallo Welt"


Notice that the ``t`` filter accepts arbitrary named parameters. Named parameters can be used
to substitute fields in translation strings with values from the template context.

It you don't give ``Translate`` any locales or you leave it empty, you'll always get the
translation key back unchanged.


