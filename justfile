import 'dev/justfile.default'

clean-venv:
    uv venv --clear

sync:
    uv sync --all-extras

run:
    uv run geekdo-sync
