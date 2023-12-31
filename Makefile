.PHONY: test-ci

TEST = ""

test-ci:
	docker compose up --exit-code-from test

setup:
	python test-config/prepare-test.py

test:
	pytest -k ${TEST} -s --cov-config=.coveragerc --cov=fractal -v --asyncio-mode=auto --cov-report=lcov --cov-report=term tests/

qtest:
	pytest -k ${TEST} -s --cov-config=.coveragerc --cov=fractal --asyncio-mode=auto --cov-report=lcov tests/
