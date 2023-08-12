# PuzzleServer
[![Publish](https://github.com/jhb123/PuzzleServer/actions/workflows/publish.yml/badge.svg)](https://htmlpreview.github.io/?https://github.com/jhb123/PuzzleServerCoverageReports/blob/main/coverage/index.html)

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
## Docker
Use docker to build a container
```commandline
docker build -t puzzle-server .
```
Create an environment file that lets docker use your AWS environment variables. These can be for in `~/.aws` if you set up the environment using the aws cli tool.
```
AWS_DEFAULT_REGION=eu-north-1
AWS_ACCESS_KEY_ID=<super secret info>
AWS_SECRET_ACCESS_KEY=<more super secret info>
```
Run the container with
```commandline
docker run --env-file .docker_image_test_env_vars -p 5000:5000  puzzle-server
```
and then use
```commandline
curl http://0.0.0.0:5000/hello
```
to check that `Hello, World!` is sent back.

Go to the ECR console page and use the instructions there to upload the container to ECR.
## Deploying to AWS Lambda with `zappa`
Create a virtual environment. As of 12/8/2023, `zappa` works with Python 3.10.
```commandline
python3.10 -m venv deployvenv
source deployvenv/bin/activate
```
Install the deployment dependencies.
```commandline
pip install ".[deploy]"
```
You need the correct IAM permissions to run `zappa`. The `zappa_settings.json` should look like
```json
{
    "dev-zappa": {
        "app_function": "run_server.app",
        "aws_region": "eu-north-1",
        "profile_name": "default",
        "project_name": "puzzleserver",
        "runtime": "python3.10",
        "s3_bucket": "zappa-js5gk7j82",
        "slim_handler": true,
        "architecture": "arm64"
    }
}
```
It can take a few minutes for the deployment to finish fully.
