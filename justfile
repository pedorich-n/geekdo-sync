import 'dev/justfile.default'

clean-venv:
    rm -rf {{ join(justfile_directory(), ".venv") }}

sync:
    uv sync --all-extras

run:
    uv run geekdo-sync
