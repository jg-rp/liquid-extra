Liquid Extra Change Log
========================

Version 0.2.0
-------------

- HTML filters are now marked as "safe" when ``autoescape`` is on.
- The ``href`` and ``src`` attributes of ``stylesheet_tag`` and ``script_tag`` are now
  HTML escaped, even if ``autoescape`` is off.

