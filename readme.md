# Atlas BI Libarary

## What is Atlas Py?

This is a Python version of the [Atlas BI Library](https://github.com/atlas-bi/atlas-bi-library) DotNet webapp. It is currently under development.

In our love of open source we felt the need for a version of the Atlas BI Library webapp that used completely open source tools. This version of the app will effectively mirror the DotNet version in functionality and appearance, but will be installed on Ubuntu server.

### Advantages of Atlas Py

| Feature        | DotNet      | Python               | Discussion                                                                                                                                                                                                 |
| -------------- | ----------- | -------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Authentication | IIS Windows | Saml2                | Saml2 is superior to IISWA in a few areas - primary, it allows users to login on generic workstations, through IOS devices, and it allows 2 factor.                                                        |
| Speed          | Fast        | Very Fast            | Django ORM database queries outperform DotNet Linq queries, improving site performance. We are also able to do complex image optimization on linux to improve image load times.                            |
| Database       | Sql Server  | Sql Server, Postgres | Multiple databases are supported.                                                                                                                                                                          |
| Testing        | Difficult   | Simple               | Code testing is much simpler in Python and we anticipate having a full code base and UI test suite.                                                                                                        |
| Install        | Manual      | Semi-Automated       | The DotNet version requires quite a bit of manual server setup and work during install, while the python version uses apt installers which configure the server and install or update in a single command. |

[![codecov](https://codecov.io/gh/atlas-bi/atlas-bi-library-py/branch/master/graph/badge.svg?token=2JfEYNRwFl)](https://codecov.io/gh/atlas-bi/atlas-bi-library-py) [![codacy](https://app.codacy.com/project/badge/Grade/74d31f9d9f1840818bc68bb0d26a9dda)](https://www.codacy.com/gh/atlas-bi/atlas-bi-library-py/dashboard?utm_source=github.com&utm_medium=referral&utm_content=atlas-bi/atlas-bi-library-py&utm_campaign=Badge_Grade) [![CodeQL](https://github.com/atlas-bi/atlas-bi-library-py/actions/workflows/codeql.yml/badge.svg)](https://github.com/atlas-bi/atlas-bi-library-py/actions/workflows/codeql.yml) [![Maintainability](https://api.codeclimate.com/v1/badges/5b76a0292bbe56043511/maintainability)](https://codeclimate.com/github/atlas-bi/atlas-bi-library-py/maintainability) [![quality](https://github.com/atlas-bi/atlas-bi-library-py/actions/workflows/quality.yml/badge.svg)](https://github.com/atlas-bi/atlas-bi-library-py/actions/workflows/quality.yml) [![demo](https://github.com/atlas-bi/atlas-bi-library-py/actions/workflows/demo.yml/badge.svg)](https://atlas-py.herokuapp.com) [![browserstack](https://automate.browserstack.com/badge.svg?badge_key=SWVldTlYclVWZEJ5R0NQUFRTMlltSTlNQ2JRaEF1ek9NeWd1L0FjYWt1cz0tLUcyRUhJUGprRDVmTnlyUytOQmpkVWc9PQ==--017a6b444f1f4d88941b98cea65cbce32c651a58)](https://automate.browserstack.com/public-build/SWVldTlYclVWZEJ5R0NQUFRTMlltSTlNQ2JRaEF1ek9NeWd1L0FjYWt1cz0tLUcyRUhJUGprRDVmTnlyUytOQmpkVWc9PQ==--017a6b444f1f4d88941b98cea65cbce32c651a58)

## Project Goals

Take a look at the [github project](https://github.com/atlas-bi/atlas-bi-library-py/projects/1) to see a list of planned features.

## How can I contribute?

-   [Suggest a new feature or idea in our discussion board!](https://github.com/atlas-bi/atlas-bi-library-py/discussions)
-   Try out the [daily build demo](https://demo.atlas.bi/). Please [create an issue](https://github.com/atlas-bi/atlas-bi-library-py/issues) for any bugs you find!
-   Contribute to the code!

## Development

This version of the app is built using python + django.

### Required Tools

-   [Precommit](https://pre-commit.com) `pre-commit install`
-   [Poetry](https://python-poetry.org)
-   [Pyenv](https://github.com/pyenv/pyenv) `pyenv local 3.6.2 3.7.0 3.8.0 3.9.0`
-   [NodeJS](https://nodejs.dev)

### Install Dependencies

```bash
npm install
poetry install
```

### Database Connection

There are a few settings files to run the app. The required settings have already been set in the existing files. Org specific settings can be added in `*_cust.py` files. They will be ignored in commits.

If you need to override any of the default config, add your overrides to the `*_cust.py` files.

The names should be:

-   `settings_cust.py`
-   `dev_cust.py`
-   `prod_cust.py`
-   `test_cust.py`

As an example, if you want to use an existing Atlas sql server database, you can add a database config like this:

```python
DATABSES = "default": {
    "ENGINE": "mssql",
    "NAME": "atlas_dev",
    "HOST": "127.0.0.1",
    "USER": "datagov",
    "PASSWORD": "12345",
    "COLLATION": "SQL_Latin1_General_CP1_CI_AS",
    "OPTIONS": {
        "driver": "ODBC Driver 17 for SQL Server",
    },
    "schemas": ["app", "dbo"],
}
# note, sql server will only allow connections if app is the default schema for the user.
```

## Running the Website

```bash
cd atlas && poetry run python manage.py runserver
```

## Running Celery for ETL Development

```bash
DJANGO_SETTINGS_MODULE='atlas.settings.dev' poetry run celery -A atlas worker -l DEBUG
```

In a separate terminal, start celery beat for scheduled jobs.

```bash
DJANGO_SETTINGS_MODULE='atlas.settings.dev' poetry run celery -A atlas beat -l DEBUG --scheduler django_celery_beat.schedulers:DatabaseScheduler
```

## Running tests

Testing uses a local postgres server and redis server. The server names are `postgres` and `redis` to allow them to run as a service in the ci/cd pipelines. The best thing is to add a mapping in your local host file of `127.0.0.1 postgres` and `127.0.0.1 redis`.

1.  Start postgres in a docker container. (You can do the same with redis, or, as in our case, install with homebrew.)

    ```bash
    docker run --name postgresql-container -p 5432:5432 -e POSTGRES_HOST_AUTH_METHOD=trust -d postgres
    ```

    or a sql server

    ```bash
    docker run --name mssql-container -e "ACCEPT_EULA=Y" -e "SA_PASSWORD=yourStrong(>)Password" -p 1433:1433 -d mcr.microsoft.com/mssql/server:2019-latest
    ```

    This will create a standing database. You can restart it without needing to recreate by running `docker container start postgresql-container` or `docker container start mssql-container`

2.  Start solr

See `/solr/readme.rst` for a guide.

3.  Run code tests directly

    ```bash
    poetry run python manage.py test --no-input --pattern="test_views.py" --settings atlas.settings.test

    # or with tox
    # run with py36, 37, 38 or 39.
    tox -e clean,py39,cov
    ```

4.  Run browser tests

    ```bash
    BROWSERSTACK_USERNAME=<browserstack username> \
    BROWSERSTACK_ACCESS_KEY=<browserstack accesskey> \
    BROWSERSTACK_BUILD_NAME="local" \
    BROWSERSTACK_PROJECT_NAME="Atlas-Py" \
    poetry run python manage.py test --no-input --pattern="test_browser.py" --settings atlas.settings.test_browser

    # or with tox
    tox -e clean,browsertest,cov -r
    ```
