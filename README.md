# Guizhong

[![GitHub Actions Workflow Status](https://img.shields.io/github/actions/workflow/status/jasmaa/guizhong/test.yml)
](https://github.com/jasmaa/guizhong/actions/workflows/test.yml)
[![Codecov](https://img.shields.io/codecov/c/github/jasmaa/guizhong)](https://app.codecov.io/gh/jasmaa/guizhong/)


A Discord bot that plays music from a queue.


## Getting started

Run bot:

```
uv run main.py
```

See [setup instructions](./docs/SETUP.md) for more detailed instructions.

Testing code:

```
uv run pytest -v -s --cov=src --cov-branch --cov-report=xml --cov-report=html --cov-report=term
```

Formatting code:

```
black .
```
