# PuzzleServer
[![coverage](https://github.com/jhb123/PuzzleServer/actions/workflows/coverage.yml/badge.svg)](https://htmlpreview.github.io/?https://github.com/jhb123/PuzzleServerCoverageReports/blob/main/coverage/index.html)

[//]: # (![Static Badge]&#40;https://img.shields.io/badge/Coverage-39.0%25-%23FF0000&#41;)

[Coverage report](https://htmlpreview.github.io/?https://github.com/jhb123/PuzzleServerCoverageReports/blob/main/coverage/index.html)
## Running the server locally
Install the server with
```commandline
pip install -e .
```
Start the server locally with:
```commandline
gunicorn -w 4 -b 0.0.0.0:5000 run_server:app
```
Stop the server with `ctrl+C`
## Development
To develop this package, use
```commandline
pip install -e '.[dev]'
```
Pre-commit hooks will keep your code tidy. Set them up with
```commandline
pre-commit install
```
To run them manually, use
```commandline
pre-commit run --all-files
```
Tags on merge into release
### testing
To run the tests in this package, install with
```commandline
pip install -e '.[test]'
```
Run with e.g.
```commandline
pytest test/unit_tests/test_storage.py
coverage run -m pytest
```
View the coverage with
```commandline
coverage html --omit="test/*" -d test/coverage
```
### CI
The test suite runs whenever commits are pushed.
A coverage report is generated when a PR into main is created

`act` is a useful tool for developing pipelines. Create an artifact directory
```commandline
mkdir /tmp/artifacts
```
and then run the jobs you want to test e.g.
```commandline
act --container-architecture linux/amd64 -s REPORT_TOKEN=*** --artifact-server-path /tmp/artifacts -j publish

```
## AWS
While developing, using the AWS plugin for PyCharm may be the best process.

Set up an IAM user with the required permissions. Create an access key for the user. Then follow through the steps as prompted
```commandline
aws configure
```
