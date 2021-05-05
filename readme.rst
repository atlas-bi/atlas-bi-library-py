
|travis| |codecov| |codacy| |codeql|

Atlas of Information Management
===============================

    This is a Python version of the `Atlas web app <https://github.com/Riverside-Healthcare/Atlas>`_ and is currently under development. The dotnet version of the app is still being maintained.


Atlas of Information Management is a business intelligence library and documentation database. ELT processes collect metadata from various reporting platforms and store it in a centraly located database. A modern web UI is used to add additional documentation to the report objects and also to provide an intuative way to search, favorite and share reporting content.


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
- Try out the daily build demo. Please `create an issue <https://github.com/Riverside-Healthcare/Atlas-Py/issues/new>`_ for any bugs you find!
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

.. code:: python

    cd atlas && poetry run python manage.py runserver


Running tests
#############

Testing uses a local postgres server and redis server. The server names are "postgres" and "redis" to allow them to run as a service in the ci/cd pipelines. The best thing is to add a mapping in your local host file of ``127.0.0.1 postgres`` and ``127.0.0.1 redis``.

1. Start postgres in a docker container. (You can do the same with redis, or, as in our case, install with homebrew.)

   .. code:: bash

      docker run --name postgresql-container -p 5432:5432 -e POSTGRES_HOST_AUTH_METHOD=trust -d postgres

2. Run tests directly (this will also run selenium tests)

   .. code:: bash

      poetry run python manage.py test --no-input --settings atlas.settings.test


3. Or run tests with Tox (this will only run headless tests)

   .. code:: bash

       # run with py36, 37, 38 or 39.
       tox -e clean,py39,cov



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


.. |travis| image:: https://travis-ci.com/Riverside-Healthcare/Atlas-Py.svg?branch=master
    :target: https://travis-ci.com/Riverside-Healthcare/Atlas-Py

.. |codecov| image:: https://codecov.io/gh/Riverside-Healthcare/Atlas-Py/branch/main/graph/badge.svg?token=2JfEYNRwFl
      :target: https://codecov.io/gh/Riverside-Healthcare/Atlas-Py

.. |codeql| image:: https://github.com/Riverside-Healthcare/Atlas-Py/actions/workflows/codeql-analysis.yml/badge.svg
   :target: https://github.com/Riverside-Healthcare/Atlas-Py/actions/workflows/codeql-analysis.yml
   :alt: CodeQL

.. |codacy| image:: https://app.codacy.com/project/badge/Grade/ccc9f660171643669480f456be4a5e3c
    :target: https://www.codacy.com/gh/Riverside-Healthcare/Atlas-Py/dashboard?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=Riverside-Healthcare/Atlas-Py&amp;utm_campaign=Badge_Grade
