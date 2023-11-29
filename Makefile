.PHONY: test-ci

test-ci:
	docker compose up --exit-code-from test	