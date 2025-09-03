# -*- coding: utf-8 -*-
# @Time : 2025/9/1 12:53
# @Author : Marcial
# @Project: data_filter
# @File : __init__.py.py
# @Software: PyCharm
from redis_queue.priority_redis_queue import PriorityRedisQueue
from redis_queue.redis_distributed_lock import RedisDistributedLock
from redis_queue.fifo_redis_queue import FifoRedisQueue
from redis_queue.lifo_redis_queue import LifoRedisQueue
from .config import get as queue_config_get  # 导出配置读取

def get_redis_queue_cls(queue_type):
    if queue_type == 'priority':
        return PriorityRedisQueue
    elif queue_type == 'fifo':
        return FifoRedisQueue
    elif queue_type == 'lifo':
        return LifoRedisQueue
    else:
        raise ValueError('Invalid queue type: {}'.format(queue_type),"支持的队列名称为[priority,fifo,lifo]")

def get_redis_lock_cls():
    return RedisDistributedLock