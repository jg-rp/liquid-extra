
.PHONY: test
test:
	python -m unittest -f


.PHONY: coverage
coverage:
	python -m coverage erase
	tox -c tox_cov.ini
	python -m coverage combine
	python -m coverage html


.PHONY: build
build: clean
	python -m build

.PHONY: clean
clean:
	python -Bc "import pathlib; [p.unlink() for p in pathlib.Path('.').rglob('*.py[co]')]"
	python -Bc "import pathlib; [p.rmdir() for p in pathlib.Path('.').rglob('__pycache__')]"
	rm -f .coverage
	rm -rf htmlcov
	rm -rf python_liquid_extra.egg-info
	rm -rf build
	rm -rf dist
	rm -rf .tox


