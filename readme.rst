Atlas of Information Management
===============================

    This is a Python version of the `Atlas web app <https://github.com/Riverside-Healthcare/Atlas>`_ and is currently under development. The dotnet version of the app is still being maintained.


Atlas of Information Management is a business intelligence library and documentation database. ELT processes collect metadata from various reporting platforms and store it in a centraly located database. A modern web UI is used to add additional documentation to the report objects and also to provide an intuative way to search, favorite and share reporting content.

|travis| |codecov| |codacy| |codeql| |climate| |quality| |demo| |browserstack|

Project Goals
#############

Take a look at the `github project <https://github.com/Riverside-Healthcare/Atlas-Py/projects/1>`_ to see where the project is heading. Here's a summary of new features planned.

- Authentication
    - Single sign on with SAML2
    - LDAP Auth
- Testing
    - Include automated browser testing
    - Include code tests w/ 95% coverage
- Database
    - Convert to Postgres database
- Enhanced search
    - Use Apache Solr search engine
    - Allow search favorites
    - Allow clearing search history
    - Add search tags to reports
    - Improve sql searching
    - Option to export search results
- Dedicated Admin section of app
    - ability to manage security by etl'd groups
    - ability to monitor/manage ETL from inside the app
    - include additional report library status reports
    - include additional top-user metrics
    - include report profiles for user roles
- Mail features
    - Enable SMTP notifications
    - Allow sending attachments
    - Creating folders
    - Keyboard navigation
    - Sorting
    - Notification when a favorite report is modified
    - Allow markdown in messages
    - Enable conversation grouping
    - Add markers for replied/forwarded message
    - Ability to receive/open ssrs subscriptions in app
- Data Projects
    - Allow data project annotations to be "archived" vs deleted
    - Allow data project annotation groups
    - Auto build recommended projects based on analytics
- Report Documentation
    - Convert editor to browser/js markdown rendering engine
    - Add hidden dev notes fields to documentation for developers
- Add filters to charts
- Ability to save SSRS parameterized urls in favorites
- Convert css to scss

=============
Documentation
=============

See the `project documentation <https://riverside-healthcare.github.io/Atlas-Py/>`_

=====================
How can I contribute?
=====================

- `Suggest a new feature or idea in our discussion board! <https://github.com/Riverside-Healthcare/Atlas-Py/discussions>`_
- Try out the `daily build demo <https://atlas-py.herokuapp.com>`_. Please `create an issue <https://github.com/Riverside-Healthcare/Atlas-Py/issues/new>`_ for any bugs you find!
- Contribute to the code!


Development
###########

This version of the app is built using python + django.

* `Precommit <https://pre-commit.com>`_ ``pre-commit install``
* `Poetry <https://python-poetry.org>`_
* `Pyenv <https://github.com/pyenv/pyenv>`_ ``pyenv local 3.6.2 3.7.0 3.8.0 3.9.0``
* `NodeJS <https://nodejs.dev>`_
* Developing on windows is difficult, but can be done. `Git sdk 64 <https://github.com/git-for-windows/git-sdk-64>`_ works well for installing and running these tools.


There are a few settings files to run the app. The required settings have already been set in the existing files. Org specific settings can be added in *_cust.py files. They will be ignored in commits.

If you need to override any of the default config, add your overrides to the *_cust.py files.

The names should be:

- settings_cust.py
- dev_cust.py
- prod_cust.py
- test_cust.py

As an example, if you want to use an existing Atlas sql server database, you can add a database config like this:

.. code:: python

    # stop multiple queries for db version
    from sql_server.pyodbc.base import DatabaseWrapper
    DatabaseWrapper.sql_server_version = 2017

    DATABSES = "default": {
        "ENGINE": "sql_server.pyodbc",
        "NAME": "atlas",
        "HOST": "server_name",
        "USER": "datagov",
        "PASSWORD": "12345",
        "OPTIONS": {
            "driver": "ODBC Driver 17 for SQL Server",
            "extra_params": "MARS_Connection=Yes",
        },
        "schemas": ["app", "dbo"],
    },
    # note, sql server will only allow connections if app is the default schema for the user.

Running the app
###############

Redis, Solr and a database should be up. See ``solr/readme.md`` for a guide to starting up a demo solr instance for development.

In terminal 1, start webapp:

.. code:: bash

    cd atlas && poetry run python manage.py runserver


In terminal 2, start celery (for ETL's):

.. code:: bash

    DJANGO_SETTINGS_MODULE='atlas.settings.dev' poetry run celery -A atlas worker -l DEBUG

In terminal 3, start celery beat (for scheduled ETL's):

.. code:: bash

    DJANGO_SETTINGS_MODULE='atlas.settings.dev' poetry run celery -A atlas beat -l DEBUG --scheduler django_celery_beat.schedulers:DatabaseScheduler

In terminal 4, start static file watcher

.. code:: bash

    npm run watch

Building Static Content
-----------------------

.. code:: bash

    npm run build


Running tests
#############

Testing uses a local postgres server and redis server. The server names are "postgres" and "redis" to allow them to run as a service in the ci/cd pipelines. The best thing is to add a mapping in your local host file of ``127.0.0.1 postgres`` and ``127.0.0.1 redis``.

1. Start postgres in a docker container. (You can do the same with redis, or, as in our case, install with homebrew.)

   .. code:: bash

      docker run --name postgresql-container -p 5432:5432 -e POSTGRES_HOST_AUTH_METHOD=trust -d postgres

2. Start solr

See /solr/readme.rst for a guide.

3. Run code tests directly

   .. code:: bash

      poetry run python manage.py test --no-input --pattern="test_views.py" --settings atlas.settings.test

      # or with tox
      # run with py36, 37, 38 or 39.
      tox -e clean,py39,cov


4. Run browser tests

   .. code:: bash

      BROWSERSTACK_USERNAME=<browserstack username> \
      BROWSERSTACK_ACCESS_KEY=<browserstack accesskey> \
      BROWSERSTACK_BUILD_NAME="local" \
      BROWSERSTACK_PROJECT_NAME="Atlas-Py" \
      poetry run python manage.py test --no-input --pattern="test_browser.py" --settings atlas.settings.test_browser

      # or with tox
      tox -e clean,browsertest,cov -r


Linting
=======

Node is used for linting. Install packages in project > npm install

Todo:
add html lint


Server setup
============

install
- memcache (check if online q/ telnet 127.0.0.1 11211)
- redis (check if online with ping redis)


Database
========

Currently db first, using a pre-existing mssql atlas database. https://docs.djangoproject.com/en/3.1/howto/legacy-databases/

The tests are run with a separate model designed for postgres, which is the ultimate direction of atlas.


Caching
=======

Using python-memcached

to create cache:

.. code:: sh

    python manage.py createcachetable

Release Process
===============

create a new tag

.. code:: python

   git tag x.x.x
   git push origin --tags


1. run gulp build
2. put output into a release
3. build .deb's (see ``/scripts/readme.md``)


.. |travis| image:: https://app.travis-ci.com/atlas-bi/atlas-bi-library-py.svg?branch=master
    :target: https://app.travis-ci.com/atlas-bi/atlas-bi-library-py

.. |codecov| image:: https://codecov.io/gh/atlas-bi/atlas-bi-library-py/branch/master/graph/badge.svg?token=2JfEYNRwFl
      :target: https://codecov.io/gh/atlas-bi/atlas-bi-library-py


.. |codeql| image:: https://github.com/atlas-bi/atlas-bi-library-py/actions/workflows/codeql.yml/badge.svg)
   :target: https://github.com/atlas-bi/atlas-bi-library-py/actions/workflows/codeql.yml
   :alt: CodeQL

.. |codacy| image:: https://app.codacy.com/project/badge/Grade/74d31f9d9f1840818bc68bb0d26a9dda
    :target: https://www.codacy.com/gh/atlas-bi/atlas-bi-library-py/dashboard?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=atlas-bi/atlas-bi-library-py&amp;utm_campaign=Badge_Grade

.. |climate| image:: https://api.codeclimate.com/v1/badges/5b76a0292bbe56043511/maintainability
   :target: https://codeclimate.com/github/atlas-bi/atlas-bi-library-py/maintainability
   :alt: Maintainability

.. |quality| image:: https://github.com/atlas-bi/atlas-bi-library-py/actions/workflows/quality.yml/badge.svg
   :target: https://github.com/atlas-bi/atlas-bi-library-py/actions/workflows/quality.yml

.. |demo| image:: https://github.com/atlas-bi/atlas-bi-library-py/actions/workflows/demo.yml/badge.svg
   :target: https://atlas-py.herokuapp.com

.. |browserstack| image:: https://automate.browserstack.com/badge.svg?badge_key=SWVldTlYclVWZEJ5R0NQUFRTMlltSTlNQ2JRaEF1ek9NeWd1L0FjYWt1cz0tLUcyRUhJUGprRDVmTnlyUytOQmpkVWc9PQ==--017a6b444f1f4d88941b98cea65cbce32c651a58
   :target: https://automate.browserstack.com/public-build/SWVldTlYclVWZEJ5R0NQUFRTMlltSTlNQ2JRaEF1ek9NeWd1L0FjYWt1cz0tLUcyRUhJUGprRDVmTnlyUytOQmpkVWc9PQ==--017a6b444f1f4d88941b98cea65cbce32c651a58



