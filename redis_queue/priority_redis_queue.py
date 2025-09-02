# -*- coding: utf-8 -*-
# @Time : 2025/9/1 21:02
# @Author : Marcial
# @Project: data_filter
# @File : priority_redis_queue.py
# @Software: PyCharm

from .base import BaseRedisQueue
import umsgpack
from .redis_distributed_lock import RedisDistributedLock
from .config import get  # 统一配置

class PriorityRedisQueue(BaseRedisQueue):
    '''利用redis的有序集合进行数据存取'''

    def __init__(self, is_use_lock=None, name=None):
        is_use_lock = get('use_lock') if is_use_lock is None else is_use_lock
        name = name or get('priority_queue_name')
        if is_use_lock:
            self.redis_lock = RedisDistributedLock(get('lock_name'))
        self.is_use_lock = is_use_lock
        super(PriorityRedisQueue, self).__init__(name=name)

    def qsize(self):
        self.last_qsize = self.redis.zcard(self.name)
        return self.last_qsize

    def put_nowait(self, obj: dict):
        """

        :param obj: {value:priority}
        :return:
        """
        if self.lazy_limit and self.last_qsize < self.maxsize:
            pass
        elif self.full():
            raise self.Full
        self.last_qsize = self.redis.zadd(self.name, obj)
        return True

    def get_nowait(self):
        """
        -1,-1默认去权重最大的值
        0,0默认去权重最小的值
        :return:
        """

        if self.is_use_lock:
            if self.redis_lock.acquire_lock():
                ret = self.redis.zrange(self.name, -1, -1)
                if not ret:
                    raise self.Empty
                self.redis.zrem(self.name, ret[0])
                self.redis_lock.release_lock()

                return ret
        else:
            ret = self.redis.zrange(self.name, -1, -1)
            if not ret:
                raise self.Empty
            self.redis.zrem(self.name, ret[0])
            return ret