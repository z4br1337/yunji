import os

if os.environ.get('DB_ENGINE') == 'mysql':
    try:
        import pymysql
        pymysql.install_as_MySQLdb()
    except ImportError:
        pass
