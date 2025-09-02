# -*- coding: utf-8 -*-
# @Time : 2025/9/1 13:11
# @Author : Marcial
# @Project: data_filter
# @File : lifo_redis_queue.py
# @Software: PyCharm
from .base import BaseRedisQueue
import umsgpack

class LifoRedisQueue(BaseRedisQueue):

    def get_nowait(self):
        ret = self.redis.rpop(self.name)
        if ret is None:
            raise self.Empty
        return umsgpack.unpackb(ret)