help:
	@echo ================================================================================
	@fgrep -h "##" $(MAKEFILE_LIST) | fgrep -v fgrep | sed -e 's/\\$$//' | sed -e 's/##//'
	@echo ================================================================================


.PHONY: install
install:			## install main python dependencies via poetry
	poetry install


.PHONY: lint
lint:				## run linters
	@poetry run ./lint fix


.PHONY: lint-check
lint-check:			## run linters in check mode
	@poetry run ./lint


.PHONY: test
test:				## run tests
	@poetry run pytest


.PHONY: outdated
outdated:			## check for outdated dependencies
	@poetry show -o -a
