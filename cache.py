# coding:utf-8
__author__ = 'chenghao'

'''
A simple cache interface.
'''

from config import logger, redis_param
import redis
from redis.exceptions import RedisError

try:
    import cPickle as pickle
except ImportError:
    import pickle

user_session_prefix = "websetup_user"  # 用户session前缀
retri_pwd_prefix = "websetup_retripwd"  # 用户找回密码前缀
ver_code_prefix = "websetup_ver_code"  # 用户验证码前缀

half_hour = 30 * 60  # 30分钟
one_hour = half_hour * 2  # 1小时
quarter = one_hour * 24 * 91  # 一季度
half_year = quarter * 2  # 半年


def _safe_pickle_loads(r):
    if r is None:
        return None
    try:
        return pickle.loads(r)
    except pickle.UnpicklingError:
        pass
    return None


class RedisClient(object):
    def __init__(self):
        self._pool = redis.ConnectionPool(host=redis_param["host"], port=redis_param["port"], db=0,
                                          max_connections=150)
        self._client = redis.Redis(connection_pool=self._pool)

    def set(self, key, value, expires=half_hour):
        logger.debug('set cache: key = %s' % key)
        try:
            self._client.set(key, pickle.dumps(value), ex=expires)
        except RedisError, e:
            logger.error("set cache 失败: " + str(e), exc_info=True)

    def hset(self, name, key, value):
        logger.debug('hset cache: name = %s, key = %s' % (name, key))
        try:
            self._client.hset(name, key, pickle.dumps(value))
        except RedisError, e:
            logger.error("hset cache 失败: " + str(e), exc_info=True)

    def get(self, key, default=None):
        logger.debug('get cache: key = %s' % key)
        try:
            r = self._client.get(key)
            if r is None:
                return default
            return _safe_pickle_loads(r)
        except RedisError, e:
            logger.error("get cache 失败: " + str(e), exc_info=True)
            return -1

    def hget(self, name, key, default=None):
        logger.debug('hget cache: name = %s, key = %s' % (name, key))
        try:
            r = self._client.hget(name, key)
            if r is None:
                return default
            return _safe_pickle_loads(r)
        except RedisError, e:
            logger.error("hget cache 失败: " + str(e), exc_info=True)
            return -1

    def gets(self, *keys):
        '''
        Get objects by keys.
        Args:
            keys: cache keys as str.
        Returns:
            list of object.

        c = RedisClient('localhost')
        c.gets(key1, key2, key3)
        [None, None, None]
        c.set(key1, 'Key1')
        c.set(key3, 'Key3')
        c.gets(key1, key2, key3)
        ['Key1', None, 'Key3']
        '''
        logger.debug('gets cache: keys = %s' % keys)
        try:
            return map(_safe_pickle_loads, self._client.mget(keys))
        except RedisError, e:
            logger.error("gets cache 失败: " + str(e), exc_info=True)
            return -1

    def delete(self, key):
        logger.debug('delete cache: key = %s' % key)
        try:
            self._client.delete(key)
        except RedisError, e:
            logger.error("delete cache 失败: " + str(e), exc_info=True)

    def hdel(self, name, key):
        logger.debug('hdel cache: name = %s, key = %s' % (name, key))
        try:
            self._client.hdel(name, key)
        except RedisError, e:
            logger.error("hdel cache 失败: " + str(e), exc_info=True)


redis_cache = RedisClient()


