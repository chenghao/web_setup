# coding:utf-8
__author__ = 'chenghao'

'''
Database operation module. This module is independent with web module.
'''

import time, functools, threading
from config import logger
from utils import Dict


def _profiling(start, sql=''):
    t = time.time() - start
    if t > 0.1:
        logger.warning('[PROFILING] [DB] %s: %s' % (t, sql))
    else:
        logger.info('[PROFILING] [DB] %s: %s' % (t, sql))


class DBError(Exception):
    pass


class MultiColumnsError(DBError):
    pass


def _log(s):
    logger.debug(s)


def _dummy_connect():
    '''
    Connect function used for get db connection. This function will be relocated in init(dbn, ...).
    '''
    raise DBError('Database is not initialized. call init(dbn, ...) first.')


_db_connect = _dummy_connect
_db_convert = '?'


class _LasyConnection(object):
    def __init__(self):
        self.connection = None

    def cursor(self):
        if self.connection is None:
            _log('open connection...')
            self.connection = _db_connect()
        return self.connection.cursor()

    def commit(self):
        self.connection.commit()

    def rollback(self):
        self.connection.rollback()

    def cleanup(self):
        if self.connection:
            connection = self.connection
            self.connection = None
            _log('close connection...')
            connection.close()


class _DbCtx(threading.local):
    '''
    Thread local object that holds connection info.
    '''

    def __init__(self):
        self.connection = None
        self.transactions = 0

    def is_init(self):
        return not self.connection is None

    def init(self):
        _log('open lazy connection...')
        self.connection = _LasyConnection()
        self.transactions = 0

    def cleanup(self):
        self.connection.cleanup()

    def cursor(self):
        '''
        Return cursor
        '''
        return self.connection.cursor()


_db_ctx = _DbCtx()


class _ConnectionCtx(object):
    '''
    _ConnectionCtx object that can open and close connection context. _ConnectionCtx object can be nested and only the most
    outer connection has effect.
    with connection():
        pass
        with connection():
            pass
    '''

    def __enter__(self):
        global _db_ctx
        self.should_cleanup = False
        if not _db_ctx.is_init():
            _db_ctx.init()
            self.should_cleanup = True
        return self

    def __exit__(self, exctype, excvalue, traceback):
        global _db_ctx
        if self.should_cleanup:
            _db_ctx.cleanup()


def connection():
    '''
    Return _ConnectionCtx object that can be used by 'with' statement:
    with connection():
        pass
    '''
    return _ConnectionCtx()


def with_connection(func):
    '''
    Decorator for reuse connection.
    @with_connection
    def foo(*args, **kw):
        f1()
        f2()
        f3()
    '''

    @functools.wraps(func)
    def _wrapper(*args, **kw):
        with _ConnectionCtx():
            return func(*args, **kw)

    return _wrapper


class _TransactionCtx(object):
    '''
    _TransactionCtx object that can handle transactions.
    with _TransactionCtx():
        pass
    '''

    def __enter__(self):
        global _db_ctx
        self.should_close_conn = False
        if not _db_ctx.is_init():
            # needs open a connection first:
            _db_ctx.init()
            self.should_close_conn = True
        _db_ctx.transactions = _db_ctx.transactions + 1
        _log('begin transaction...' if _db_ctx.transactions == 1 else 'join current transaction...')
        return self

    def __exit__(self, exctype, excvalue, traceback):
        global _db_ctx
        _db_ctx.transactions = _db_ctx.transactions - 1
        try:
            if _db_ctx.transactions == 0:
                if exctype is None:
                    self.commit()
                else:
                    self.rollback()
        finally:
            if self.should_close_conn:
                _db_ctx.cleanup()

    def commit(self):
        global _db_ctx
        _log('commit transaction...')
        try:
            _db_ctx.connection.commit()
            _log('commit ok.')
        except:
            logger.warning('commit failed. try rollback...')
            _db_ctx.connection.rollback()
            logger.warning('rollback ok.')
            raise

    def rollback(self):
        global _db_ctx
        _log('manully rollback transaction...')
        _db_ctx.connection.rollback()
        logger.info('rollback ok.')


def transaction():
    '''
    Create a transaction object so can use with statement:
    with transaction():
        pass
    '''
    return _TransactionCtx()


def with_transaction(func):
    '''
    A decorator that makes function around transaction.
    '''
    @functools.wraps(func)
    def _wrapper(*args, **kw):
        _start = time.time()
        with _TransactionCtx():
            return func(*args, **kw)
        _profiling(_start)

    return _wrapper


def _select(sql, first, *args):
    ' execute select SQL and return unique result or list results.'
    global _db_ctx, _db_convert
    cursor = None
    if _db_convert != '?':
        sql = sql.replace('?', _db_convert)
    _log('SQL: %s, ARGS: %s' % (sql, args))
    start = time.time()
    try:
        cursor = _db_ctx.connection.cursor()
        cursor.execute(sql, args)
        if cursor.description:
            names = [x[0] for x in cursor.description]
        if first:
            values = cursor.fetchone()
            if not values:
                return None
            return Dict(names, values)
        return [Dict(names, x) for x in cursor.fetchall()]
    finally:
        if cursor:
            cursor.close()
        _profiling(start, sql)


@with_connection
def select_one(sql, *args):
    '''
    Execute select SQL and expected one result.
    If no result found, return None.
    If multiple results found, the first one returned.
    '''
    return _select(sql, True, *args)


@with_connection
def select_int(sql, *args):
    '''
    Execute select SQL and expected one int and only one int result.

    MultiColumnsError: Expect only one column.
    '''
    d = _select(sql, True, *args)
    if len(d) != 1:
        raise MultiColumnsError('Expect only one column.')
    return d.values()[0]


@with_connection
def select(sql, *args):
    '''
    Execute select SQL and return list or empty list if no result.
    > u1 = dict(id=200, name='Wall.E', email='wall.e@test.org', passwd='back-to-earth', last_modified=time.time())
    > u2 = dict(id=201, name='Eva', email='eva@test.org', passwd='back-to-earth', last_modified=time.time())
    > insert('user', **u1)
    1
    > insert('user', **u2)
    1
    > L = select('select * from user where id=?', 900900900)
    > L
    []
    > L = select('select * from user where id=?', 200)
    > L[0].email
    u'wall.e@test.org'
    > L = select('select * from user where passwd=? order by id desc', 'back-to-earth')
    > L[0].name
    u'Eva'
    > L[1].name
    u'Wall.E'
    '''
    return _select(sql, False, *args)


@with_connection
def _update(sql, args, post_fn=None):
    global _db_ctx, _db_convert
    cursor = None
    if _db_convert != '?':
        sql = sql.replace('?', _db_convert)
    _log('SQL: %s, ARGS: %s' % (sql, args))
    start = time.time()
    try:
        cursor = _db_ctx.connection.cursor()
        cursor.execute(sql, args)
        r = cursor.rowcount
        if _db_ctx.transactions == 0:
            # no transaction enviroment:
            _log('auto commit')
            _db_ctx.connection.commit()
            post_fn and post_fn()
        return r
    finally:
        if cursor:
            cursor.close()
        _profiling(start, sql)


def insert(table, **kw):
    '''
    Execute insert SQL.
    > u1 = dict(id=2000, name='Bob', email='bob@test.org', passwd='bobobob', last_modified=time.time())
    > insert('user', **u1)
    1
    > u2 = select_one('select * from user where id=?', 2000)
    > u2.name
    u'Bob'
    > insert('user', **u2)
    Traceback (most recent call last):
      ...
    IntegrityError: column id is not unique
    '''
    cols, args = zip(*kw.iteritems())
    sql = 'insert into %s (%s) values (%s)' % (table, ','.join(cols), ','.join([_db_convert for i in range(len(cols))]))
    return _update(sql, args)


def update(sql, *args):
    '''
    Execute update SQL.
    > u1 = dict(id=1000, name='Michael', email='michael@test.org', passwd='123456', last_modified=time.time())
    > insert('user', **u1)
    1
    > u2 = select_one('select * from user where id=?', 1000)
    > u2.email
    u'michael@test.org'
    > u2.passwd
    u'123456'
    > update('update user set email=?, passwd=? where id=?', 'michael@example.org', '654321', 1000)
    1
    > u3 = select_one('select * from user where id=?', 1000)
    > u3.email
    u'michael@example.org'
    > u3.passwd
    u'654321'
    '''
    return _update(sql, args)


def update_kw(table, where, *args, **kw):
    '''
    Execute update SQL by table, where, args and kw.
    > u1 = dict(id=900900, name='Maya', email='maya@test.org', passwd='MAYA', last_modified=time.time())
    > insert('user', **u1)
    1
    > u2 = select_one('select * from user where id=?', 900900)
    > u2.email
    u'maya@test.org'
    > u2.passwd
    u'MAYA'
    > update_kw('user', 'id=?', 900900, name='Kate', email='kate@example.org')
    1
    > u3 = select_one('select * from user where id=?', 900900)
    > u3.name
    u'Kate'
    > u3.email
    u'kate@example.org'
    > u3.passwd
    u'MAYA'
    '''
    if len(kw) == 0:
        raise ValueError('No kw args.')
    sqls = ['update', table, 'set']
    params = []
    updates = []
    for k, v in kw.iteritems():
        updates.append('%s=?' % k)
        params.append(v)
    sqls.append(', '.join(updates))
    sqls.append('where')
    sqls.append(where)
    sql = ' '.join(sqls)
    params.extend(args)
    return update(sql, *params)


def init_connector(func_connect, convert_char='%s'):
    global _db_connect, _db_convert
    _log('init connector...')
    _db_connect = func_connect
    _db_convert = convert_char


def init(db_type, db_schema, db_host, db_port=0, db_user=None, db_password=None, db_driver=None, **db_args):
    '''
    Initialize database.
    Args:
      db_type: db type, 'mysql', 'sqlite3'.
      db_schema: schema name.
      db_host: db host.
      db_user: username.
      db_password: password.
      db_driver: db driver, default to None.
      **db_args: other parameters, e.g. use_unicode=True
    '''
    global _db_connect, _db_convert
    if db_type == 'mysql':
        _log('init mysql...')
        import MySQLdb

        if not 'use_unicode' in db_args:
            db_args['use_unicode'] = True
        if not 'charset' in db_args:
            db_args['charset'] = 'utf8'
        if db_port == 0:
            db_port = 3306
        _db_connect = lambda: MySQLdb.connect(db_host, db_user, db_password, db_schema, db_port, **db_args)
        _db_convert = '%s'
    elif db_type == 'sqlite3':
        _log('init sqlite3...')
        import sqlite3

        _db_connect = lambda: sqlite3.connect(db_schema)
    else:
        raise DBError('Unsupported db: %s' % db_type)