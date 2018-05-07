#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-
"""
# ----------------------------------------------------------
#     FileName: database.py
#       Author: wangdean
#        Email: wangdean@sowell-tech.com
#      Version: 0.0.1
#   LastChange: 2016-03-29 15:37
#         Desc:
#      History:
# ----------------------------------------------------------
"""

import os
from copy import copy
from sqlalchemy import create_engine
from sqlalchemy.engine.url import make_url
from sqlalchemy.exc import OperationalError, ProgrammingError


def database_exists(url):
    """Check if a database exists.

    :param url: A SQLAlchemy engine URL.

    """
    url = copy(make_url(url))
    database = url.database
    if url.drivername.startswith('postgresql'):
        url.database = 'template1'
    else:
        url.database = None

    engine = create_engine(url)

    if engine.dialect.name == 'postgresql':
        text = "SELECT 1 FROM pg_database WHERE datname='%s'" % database
        return bool(engine.execute(text).scalar())

    elif engine.dialect.name == 'mysql':
        text = ("SELECT SCHEMA_NAME FROM INFORMATION_SCHEMA.SCHEMATA "
                "WHERE SCHEMA_NAME = '%s'" % database)
        return bool(engine.execute(text).scalar())

    elif engine.dialect.name == 'sqlite':
        return database == ':memory:' or os.path.exists(database)

    else:
        text = 'SELECT 1'
        try:
            url.database = database
            engine = create_engine(url)
            engine.execute(text)
            return True

        except (ProgrammingError, OperationalError):
            return False

def create_database(url, encoding='utf8', template=None):
    """Issue the appropriate CREATE DATABASE statement.

    :param url: A SQLAlchemy engine URL.
    :param encoding: The encoding to create the database as.
    :param template:
        The name of the template from which to create the new database. At the
        moment only supported by PostgreSQL driver.
    """

    url = copy(make_url(url))
    database = url.database

    if url.drivername.startswith('postgresql'):
        url.database = 'template1'
    elif not url.drivername.startswith('sqlite'):
        url.database = None

    engine = create_engine(url)

    if engine.dialect.name == 'postgresql':
        if engine.driver == 'psycopg2':
            from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
            engine.raw_connection().set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)

        if not template:
            template = 'template0'

        text = "CREATE DATABASE {0} ENCODING '{1}' TEMPLATE {2}".format(
            database,
            encoding,
            template
        )
        engine.execute(text)

    elif engine.dialect.name == 'mysql':
        text = "CREATE DATABASE {0} CHARACTER SET = '{1}'".format(
            database,
            encoding
        )
        engine.execute(text)

    elif engine.dialect.name == 'sqlite' and database != ':memory:':
        open(database, 'w').close()

    else:
        text = 'CREATE DATABASE {0}'.format(database)
        engine.execute(text)

def drop_database(url):
    """Issue the appropriate DROP DATABASE statement.

    :param url: A SQLAlchemy engine URL.
    """

    url = copy(make_url(url))
    database = url.database

    if url.drivername.startswith('postgresql'):
        url.database = 'template1'
    elif not url.drivername.startswith('sqlite'):
        url.database = None

    engine = create_engine(url)

    if engine.dialect.name == 'sqlite' and url.database != ':memory:':
        os.remove(url.database)

    elif engine.dialect.name == 'postgresql' and engine.driver == 'psycopg2':
        from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
        engine.raw_connection().set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)

        # Disconnect all users from the database we are dropping.
        version = list(
            map(
                int,
                engine.execute('SHOW server_version').first()[0].split('.')
            )
        )
        pid_column = (
            'pid' if (version[0] >= 9 and version[1] >= 2) else 'procpid'
        )
        text = '''
        SELECT pg_terminate_backend(pg_stat_activity.%(pid_column)s)
        FROM pg_stat_activity
        WHERE pg_stat_activity.datname = '%(database)s'
          AND %(pid_column)s <> pg_backend_pid();
        ''' % {'pid_column': pid_column, 'database': database}

        engine.execute(text)

        # Drop the database.
        text = 'DROP DATABASE {0}'.format(database)
        engine.execute(text)

    else:
        text = 'DROP DATABASE {0}'.format(database)
        engine.execute(text)
