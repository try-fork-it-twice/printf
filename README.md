# printf

Viewer for FreeRTOS profiles produced by [scanf](https://github.com/try-fork-it-twice/scanf)


## Development

For the dev packages installation use ```poetry install --with dev```

Start by creating trace files. Binary traces uses in many tests. You can use script for that like that: ```poetry run tests/scripts/example_bin_file_gen.py```

Than you would be able to start tests by ```poetry run test``` command or ```poetry run pytest tests/exactly_that_test.py```