# Contributing

Use `uv` for all Python workflows.

Install the repository hooks with:

```sh
git config core.hooksPath .githooks
```

Before opening a pull request, run:

```sh
uv run python tools/version_sync.py --check
uv run python tools/validate.py
uv run pytest
git diff --check
```

Keep changes scoped to the applet, backend, docs, or tests needed for the issue. The applet is the primary product; CLI commands are support tooling.
