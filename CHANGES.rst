Liquid Extra Change Log
========================

Version 1.1.1
-------------

- Fix missing expressions from ``FilteredIfExpression.children()``. See
  `#4 <https://github.com/jg-rp/liquid-extra/issues/4>`_.


Version 1.1.0
-------------

- Add support for static analysis of templates that make use of extra tags.

Version 1.0.0
-------------

Version bump. First stable release.

Version 0.5.0
-------------

- Added a ``with`` tag. A tag that extends the local namespace for the duration of its
  block.
- Removed depreciated ``env`` argument to the ``JSON`` and ``Translate`` filters.

Version 0.4.0
-------------

- Removed depreciated class-based filters.
- The "if not" tag now plays nicely with range literals.

Version 0.3.3
-------------

- Added drop-in replacements for standard output statements and ``echo`` and ``assign``
  tags that support inline ``if``/``else`` expressions.

Version 0.3.2
-------------

- Added ``macro`` and ``call`` tags. Define a macro (a bit like ``capture`` but with
  arguments) and run it with ``call`` (a bit like ``render`` but without hitting a
  template loader).

Version 0.3.1
-------------

- Fixed a bug where ``if not foo contains 'bar'`` would raise a ``LiquidTypeError``. It
  is now equivalent to ``if not (foo contains 'bar')``.

Version 0.3.0
-------------

- Depreciated filters that inherit from ``liquid.filter.Filter``. That's
  ``StylesheetTag``, ``ScriptTag`` and ``Index``. Use the function-based implementations
  instead (``stylesheet_tag``, ``script_tag`` and ``index``).
- Depreciated the ``env`` argument to ``filters.JSON`` and ``filters.Translate``.

Version 0.2.0
-------------

- HTML filters are now marked as "safe" when ``autoescape`` is on.
- The ``href`` and ``src`` attributes of ``stylesheet_tag`` and ``script_tag`` are now
  HTML escaped, even if ``autoescape`` is off.

