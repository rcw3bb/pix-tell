# pix-tell

**pix-tell** is an intelligent AI-powered application that analyzes and describes images with clear, detailed, and natural language.

## :computer: Prerequisites
- Python ^3.13 ([Download Python](https://www.python.org/downloads/))
- Poetry 2.0 ([Poetry installation guide](https://python-poetry.org/docs/#installation))

## :package: Installation
Clone the repository and install dependencies:

```sh
git clone https://github.com/rcw3bb/pix-tell.git
cd pix-tell
poetry install
```

## :zap: Usage

Run the application in your terminal:

```sh
poetry run python -m pix_tell
```

## :wrench: Development
- All source code is in the `pix_tell` package.
- Tests are in the `tests` package.

## :microscope: Testing & Coverage
Run all tests and generate an HTML coverage report:
```sh
poetry run pytest --cov=pix_tell tests --cov-report html
```
Open `htmlcov/index.html` to view the coverage report.

## :art: Formatting & Linting
Format and lint the code in one step:
```sh
poetry run black pix_tell && poetry run pylint pix_tell
```

## :scroll: Changelog
See [CHANGELOG.md](CHANGELOG.md) for release history.

## :key: License
This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details.

## :pen: Author
**Ron Webb**
