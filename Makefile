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


.PHONY: test
test:				## run tests
	@poetry run pytest
