# printf

Viewer for FreeRTOS profiles produced by [scanf](https://github.com/try-fork-it-twice/scanf)


## Development

**Prerequisites:**

- Python 3.13
- Poetry

**Setup project:**

```shell
poetry install
```

**Run tests:**

```shell
poetry run pytest -v
```

**Type check with mypy:**
```shell
poetry run mypy itmo_ics_printf tests
```

**Format code:**

```shell
poetry run ruff check --fix itmo_ics_printf tests
poetry run ruff format itmo_ics_printf tests
```
