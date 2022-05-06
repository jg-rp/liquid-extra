.. _Pipenv: https://pipenv.pypa.io/en/latest/

Liquid Extra
============

A growing collection of extra tags and filters for `Python Liquid <https://github.com/jg-rp/liquid>`_.

.. image:: https://img.shields.io/pypi/v/python-liquid-extra.svg
    :target: https://pypi.org/project/python-liquid-extra/
    :alt: Version

.. image:: https://github.com/jg-rp/liquid-extra/actions/workflows/tests.yaml/badge.svg
    :target: https://github.com/jg-rp/liquid-extra/tree/main/tests
    :alt: Tests

.. image:: https://img.shields.io/pypi/l/python-liquid-extra.svg
    :target: https://pypi.org/project/python-liquid-extra/
    :alt: Licence

.. image:: https://img.shields.io/pypi/pyversions/python-liquid-extra.svg
    :target: https://pypi.org/project/python-liquid-extra/
    :alt: Python versions

.. image:: https://img.shields.io/badge/pypy-3.7%20%7C%203.8-blue
    :target: https://pypi.org/project/python-liquid/
    :alt: PyPy versions


Installing
----------

Install Python Liquid Extra using `Pipenv`_:

.. code-block:: text

    $ pipenv install python-liquid-extra

Or `pip <https://pip.pypa.io/en/stable/getting-started/>`_:

.. code-block:: text

    $ python -m pip install -U python-liquid-extra

Links
-----

- Documentation: https://jg-rp.github.io/liquid/extra/introduction
- Change Log: https://github.com/jg-rp/liquid-extra/blob/main/CHANGES.rst
- PyPi: https://pypi.org/project/python-liquid-extra/
- Source Code: https://github.com/jg-rp/liquid-extra
- Issue Tracker: https://github.com/jg-rp/liquid-extra/issues


Contributing
------------

- Install development dependencies with `Pipenv`_

- Python Liquid uses type hints and static type checking. Run ``mypy`` or 
  ``tox -e typing`` to check for typing issues.

- Format code using `black <https://github.com/psf/black>`_.

- Write tests using ``unittest.TestCase``.

- Run tests with ``make test`` or ``python -m unittest`` or ``pytest``.

- Check test coverage with ``make coverage`` and open ``htmlcov/index.html`` in your
  browser.

- Check your changes have not adversely affected performance with ``make benchmark``.
