isort -l 120 -m 3 --length-sort .
black --line-length 120 .
pylint --recursive=y . --max-line-length 120 --disable=missing-docstring,empty-docstring,redefined-builtin
mypy . --ignore-missing-imports
