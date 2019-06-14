clean:
	@find . -name "*.pyc" | xargs rm -rf
	@find . -name "*.pyo" | xargs rm -rf
	@find . -name "__pycache__" -type d | xargs rm -rf
	@find . -name ".pytest_cache" -type d | xargs rm -rf

# -- test
check-debugger:
	@find . -type f -iname "*.py" -exec egrep -iH "set_trace" {} \+ && echo "Ooops! Found 1 set_trace on your source code!" && exit 1 || exit 0

test-matching: clean
	py.test . -k $(filter-out $@, $(MAKECMDGOALS)) --pdb

test: SHELL:=/bin/bash
test: clean
	export DEBUG=False && \
	py.test -s --pdb --cov-config .coveragerc --cov . . --cov-report term-missing

test-ci: clean check-debugger
	py.test -n 2 --cov-config .coveragerc --cov . . --cov-report term-missing
