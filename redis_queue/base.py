# -*- coding: utf-8 -*-
# @Time : 2025/9/1 12:54
# @Author : Marcial
# @Project: data_filter
# @File : base.py
# @Software: PyCharm

# 基于pyspider redis_queue改写

import time
import redis
from rediscluster import RedisCluster
import umsgpack
from six.moves import queue as BaseQueue
# import queue
from .config import get  # 统一配置

class BaseRedisQueue(object):
    """
    A Queue like message built over redis
    """

    Empty = BaseQueue.Empty
    Full = BaseQueue.Full
    max_timeout = 0.3

    def __init__(self, name=None, host=None, port=None, db=None,
                 maxsize=0, lazy_limit=True, password=None, cluster_nodes=None):
        """
        Constructor for RedisQueue

        maxsize:    an integer that sets the upperbound limit on the number of
                    items that can be placed in the queue.
        lazy_limit: redis queue is shared via instance, a lazy size limit is used
                    for better performance.
        """
        self.name = name or get('queue_name_default')
        host = host or get('host')
        port = port or get('port')
        db = db or get('db')
        password = (password if password is not None else get('password'))
        decode_responses = get('decode_responses')
        cluster_nodes = cluster_nodes or get('cluster_nodes')
        if cluster_nodes is not None:
            # 使用集群模式
            self.redis = RedisCluster(startup_nodes=cluster_nodes, decode_responses=decode_responses)  # 正确类
        else:
            # 使用单机模式
            self.redis = redis.Redis(host=host, port=port, db=db, password=password, decode_responses=decode_responses)
        self.maxsize = maxsize
        self.lazy_limit = lazy_limit
        self.last_qsize = 0

    def qsize(self):
        self.last_qsize = self.redis.llen(self.name)
        return self.last_qsize

    def empty(self):
        if self.qsize() == 0:
            return True
        else:
            return False

    def full(self):
        if self.maxsize and self.qsize() >= self.maxsize:
            return True
        else:
            return False

    def put_nowait(self, obj):
        if self.lazy_limit and self.last_qsize < self.maxsize:
            pass
        elif self.full():
            raise self.Full
        self.last_qsize = self.redis.rpush(self.name, umsgpack.packb(obj))
        return True

    def put(self, obj, block=True, timeout=None):
        if not block:
            return self.put_nowait(obj)

        start_time = time.time()
        while True:
            try:
                return self.put_nowait(obj)
            except self.Full:
                if timeout:
                    lasted = time.time() - start_time
                    if timeout > lasted:
                        time.sleep(min(self.max_timeout, timeout - lasted))
                    else:
                        raise
                else:
                    time.sleep(self.max_timeout)

    def get_nowait(self):
        ret = self.redis.lpop(self.name)
        if ret is None:
            raise self.Empty
        return umsgpack.unpackb(ret)

    def get(self, block=True, timeout=None):
        if not block:
            return self.get_nowait()

        start_time = time.time()
        while True:
            try:
                return self.get_nowait()
            except self.Empty:
                if timeout:
                    lasted = time.time() - start_time
                    if timeout > lasted:
                        time.sleep(min(self.max_timeout, timeout - lasted))
                    else:
                        raise
                else:
                    time.sleep(self.max_timeout)