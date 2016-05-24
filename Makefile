
WEBPACK=./node_modules/webpack/bin/webpack.js
GRUNT=grunt
NODE_PATH=./node_modules
FLAKE8=flake8 setup.py pytest_pylons/ rhodecode/ --select=E124 --ignore=E711,E712,E510,E121,E122,E126,E127,E128,E501,F401 --max-line-length=100 --exclude=*rhodecode/lib/dbmigrate/*,*rhodecode/tests/*,*rhodecode/lib/vcs/utils/*
CI_PREFIX=enterprise

.PHONY: help clean test test-clean test-lint test-only

help:
	@echo "TODO: describe Makefile"

clean: test-clean
	find . -type f \( -iname '*.c' -o -iname '*.pyc' -o -iname '*.so' \) -exec rm '{}' ';'

test: test-clean test-lint test-only

test-clean:
	rm -rf coverage.xml htmlcov junit.xml pylint.log result

test-lint:
	if [ "$$IN_NIX_SHELL" = "1" ]; then \
		$(FLAKE8); \
	else \
		$(FLAKE8) --format=pylint --exit-zero > pylint.log; \
	fi

test-only:
	PYTHONHASHSEED=random py.test -vv -r xw --cov=rhodecode --cov-report=term-missing --cov-report=html rhodecode/tests/

web-build:
	NODE_PATH=$(NODE_PATH) $(GRUNT)

web-test:
	@echo "no test for our javascript, yet!"

docs-bootstrap:
	(cd docs; nix-build default.nix -o result)
	@echo "Please go to docs folder and run make html"
