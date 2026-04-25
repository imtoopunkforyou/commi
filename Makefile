# === Configuration ===
MAKEFLAGS += --silent
make:
	cat ./Makefile

# === Dev ===
.PHONY: mypy
mypy:
	poetry run mypy ./commi --no-pretty

.PHONY: lint
lint:
	poetry run ruff format ./commi ./tests \
	&& poetry run ruff check ./commi ./tests \
	&& poetry run flake8 ./commi \
	&& make mypy \
	&& poetry run codespell --skip="*.lock,./htmlcov," -L PROMT \
	&& poetry run pymarkdown scan .

.PHONY: tests
tests:
	poetry run pytest ./tests/

.PHONY: all
all:
	make lint \
	&& make tests \
	&& echo "🚀🚀🚀 All checks have been successfully completed! 🚀🚀🚀"

# === Aliases ===
l: lint
t: tests
a: all
