isort -l 120 -m 3 --length-sort .
black --line-length 120 .
pylint $(git status -s | grep -E '\.py$' | cut -c 4-) --max-line-length 120 --disable=missing-docstring,empty-docstring,redefined-builtin,too-many-arguments,too-many-instance-attributes,too-many-locals
mypy . --ignore-missing-imports
