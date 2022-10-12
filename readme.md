<h1 align="center">
    <br />
    <a title="atlas.bi" href="https://www.atlas.bi">
        <img title="atlas logo" alt="atlas logo" src="https://raw.githubusercontent.com/atlas-bi/atlas-bi-library-py/master/atlas/static/img/atlas-logo-smooth.png" width=420 />
    </a>
    <br />
</h1>

<h4 align="center">Atlas BI Library (py) | The unified report library.</h4>

<p align="center">
    <a href="https://www.atlas.bi" target="_blank">Website</a> • <a href="https://demo.atlas.bi" target="_blank">Demo</a> • <a href="https://www.atlas.bi/docs/bi-library/" target="_blank">Documentation</a> • <a href="https://discord.gg/hdz2cpygQD" target="_blank">Chat</a>
</p>

<p align="center">
Atlas business intelligence library plugs in to your existing reporting platforms, extracts useful metadata, and displays it in a unified report library where you can easily search for, document, and launch reports.
</p>

<p align="center">
    <a href="https://www.codacy.com/gh/atlas-bi/atlas-bi-library-py/dashboard?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=atlas-bi/atlas-bi-library-py&amp;utm_campaign=Badge_Grade"><img src="https://app.codacy.com/project/badge/Grade/74d31f9d9f1840818bc68bb0d26a9dda"/></a>
    <a href="https://codecov.io/gh/atlas-bi/atlas-bi-library-py" >
 <img src="https://codecov.io/gh/atlas-bi/atlas-bi-library-py/branch/master/graph/badge.svg?token=2JfEYNRwFl"/>
 </a>
<a href="https://github.com/atlas-bi/atlas-bi-library-py/actions/workflows/test.yml" target="_blank"><img src="https://github.com/atlas-bi/atlas-bi-library-py/actions/workflows/test.yml/badge.svg" /></a>
<a href="https://discord.gg/hdz2cpygQD"><img alt="discord chat" src="https://badgen.net/discord/online-members/hdz2cpygQD/" /></a>
<a href="https://github.com/atlas-bi/atlas-bi-library-py/releases"><img alt="latest release" src="https://badgen.net/github/release/atlas-bi/atlas-bi-library-py" /></a>
</p>

## 🥅 Project Goals?

This is an all-in-one fully open source version of Atlas BI Library.

-   Installs on Ubuntu Server
-   Has dependencies requiring a license to be purchased
-   Has the ETL's managed from the website with no additional configuration

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
npm start
```

## Running Celery for ETL Development

```bash
npm run start:celery
```

In a separate terminal, start celery beat for scheduled jobs.

```bash
npm run start:beat
```

## 🧪 Testing

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
    npm run test

    # or through python
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

## 🏆 Credits

Atlas was created by the Riverside Healthcare Analytics team. See the [credits](https://www.atlas.bi/about/) for more details.

## 🔧 Tools

Special thanks to a few other tools used here.

<a href="https://automate.browserstack.com/public-build/bGhJNzFxaXI1MFFONmh2TlQwdW5MQXNyblFtYXorbEQxdU4wNnpqWFYzWT0tLVN1L2l1Mi9ueGFXQ0hIYmUxWll2c2c9PQ==--0a7425816259714011cafee8777c3fe2e15baaba"><img src='https://automate.browserstack.com/badge.svg?badge_key=bGhJNzFxaXI1MFFONmh2TlQwdW5MQXNyblFtYXorbEQxdU4wNnpqWFYzWT0tLVN1L2l1Mi9ueGFXQ0hIYmUxWll2c2c9PQ==--0a7425816259714011cafee8777c3fe2e15baaba'/></a>
<img src="https://badgen.net/badge/icon/gitguardian?icon=gitguardian&label" alt="gitguardian"> <img src="https://img.shields.io/badge/renovate-configured-green?logo=renovatebot" alt="renovate"> <a href="https://snyk.io/test/github/atlas-bi/atlas-bi-library-py"><img src="https://snyk.io/test/github/atlas-bi/atlas-bi-library-py/badge.svg" alt="snyk" /></a> <a href="https://sonarcloud.io/summary/new_code?id=atlas-bi_atlas-bi-library-py"><img src="https://sonarcloud.io/api/project_badges/measure?project=atlas-bi_atlas-bi-library-py&metric=alert_status" alt="quality gate sonar" /></a> <a href="http://commitizen.github.io/cz-cli/"><a src="https://img.shields.io/badge/commitizen-friendly-brightgreen.svg" alt="commitizen"></a>
<a href="https://github.com/semantic-release/semantic-release"><img src="https://img.shields.io/badge/%20%20%F0%9F%93%A6%F0%9F%9A%80-semantic--release-e10079.svg" alt="semantic-release" /></a> [![Lines of Code](https://sonarcloud.io/api/project_badges/measure?project=atlas-bi_atlas-bi-library-py&metric=ncloc)](https://sonarcloud.io/summary/new_code?id=atlas-bi_atlas-bi-library-py) [![Maintainability Rating](https://sonarcloud.io/api/project_badges/measure?project=atlas-bi_atlas-bi-library-py&metric=sqale_rating)](https://sonarcloud.io/summary/new_code?id=atlas-bi_atlas-bi-library-py) [![Security Rating](https://sonarcloud.io/api/project_badges/measure?project=atlas-bi_atlas-bi-library-py&metric=security_rating)](https://sonarcloud.io/summary/new_code?id=atlas-bi_atlas-bi-library-py)

## 🎁 Contributing

Contributions are welcome! Please open an [issue](https://github.com/atlas-bi/atlas-bi-library/issues) describing an issue or feature.

This repository uses commitizen. Commit code changes for pr's with `npm run commit`.
