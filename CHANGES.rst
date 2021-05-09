Liquid Extra Change Log
========================

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

