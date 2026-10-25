## CI

GitHub Actions runs on every push and pull request that touches
`backend/`. The pipeline:

1.  Installs dependencies (`uv sync --locked`)
2.  Lints with `ruff check` and `ruff format --check`
3.  Type-checks with `mypy --strict`
4.  Runs the full test suite with coverage

Test and coverage reports are uploaded as workflow artifacts on every
run.
