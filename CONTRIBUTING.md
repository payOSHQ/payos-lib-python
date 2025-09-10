# Contributing

## Setting up the environment

Require Python 3.9 or higher.

We use [uv](https://docs.astral.sh/uv/) to manage dependencies and [poethepoet](https://github.com/nat-n/poethepoet) as task runner.

```bash
# install uv
pip install --upgrade uv

uv sync --frozen

source .venv/bin/activate
```

## Adding and running examples

You can run, modify and add new examples in `examples/` directory.

```bash
uv sync --group example
cd examples
python <example>.py
```

## Linting and formatting

This repository use [ruff](https://github.com/astral-sh/ruff) and [black](https://github.com/psf/black) to format the code in repository.

```bash
uv run poe format
uv run poe lint
```

## Publishing and release

Update version with `uv version --bump`:

```bash
# for patch
uv version --bump patch
```

Then you need to run `scripts/publish-pypi` script with `PYPI_TOKEN` set on environment after change version of package.

```bash
chmod +x ./scripts/publish-pypi
./scripts/publish-pypi
```
