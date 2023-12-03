isort -l 120 -m 3 --length-sort .
black --line-length 120 .
pylint $(git status -s | grep -E '\.py$' | cut -c 4-) --max-line-length 120 --disable=missing-docstring,empty-docstring,redefined-builtin
mypy . --ignore-missing-imports
