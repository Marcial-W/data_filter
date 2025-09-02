# -*- coding: utf-8 -*-
# @Time : 2025/9/2 15:30
# @Author : Marcial
# @Project: data_filter
# @File : redis_distributed_lock.py
# @Software: PyCharm

import redis
import umsgpack
from request_manage.utils.config import config  # 读取统一配置
import socket
import os
import threading

class RedisDistributedLock(object):

    def __init__(self, lock_name, host=None, password=None, port=None, db=None, ttl=5):  # ttl为锁过期秒数
        self.lock_name = lock_name  # 锁名
        rc = config.get_redis_config()  # 统一读取配置
        self.redis = redis.StrictRedis(
            host=host or rc['host'],
            port=port or rc['port'],
            db=db or rc['db'],
            password=(password if password is not None else rc['password']),
            socket_connect_timeout=3, socket_timeout=3, decode_responses=False
        )  # 使用连接/读写超时避免“假死”
        self.ttl = ttl  # 过期时间

    def acquire_lock(self, thread_id=None):
        """尝试获取分布式锁，返回True/False"""
        if not thread_id:
            thread_id = self._get_thread_id()  # 获取当前线程ID
        print('当前线程ID:', thread_id)
        val = umsgpack.packb(thread_id)  # 与释放时保持一致
        ret = self.redis.set(self.lock_name, val, nx=True, ex=self.ttl)  # 原子设置与过期
        if ret:
            print('获取分布式锁成功')
            return True
        print('获取分布式锁失败')
        return False

    def release_lock(self, thread_id=None):
        """释放分布式锁，仅当持有者匹配时删除"""
        if not thread_id:
            thread_id = self._get_thread_id()  # 获取当前线程ID
        cur = self.redis.get(self.lock_name)
        if cur and cur == umsgpack.packb(thread_id):  # 与加锁时一致
            self.redis.delete(self.lock_name)
            print('释放分布式锁成功')
            return True
        print('释放分布式锁失败')
        return False

    def _get_thread_id(self):
        """获取当前线程ID"""
        return socket.gethostname()+str(os.getpid())+threading.current_thread().name

if __name__ == '__main__':
    lock = RedisDistributedLock()

    if lock.acquire_lock():
        print("执行操作")
        lock.release_lock()