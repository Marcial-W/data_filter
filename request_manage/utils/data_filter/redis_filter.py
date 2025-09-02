
# -*- coding: utf-8 -*-
# @Time : 2025/8/23 14:22
# @Author : Marcial
# @File : redis_filter.py
# @Software: PyCharm

import logging
from typing import Optional

from . import BaseFilter
import redis

# 导入配置
try:
    from request_manage.utils.config import config
except ImportError:
    # 如果配置文件不存在，使用默认配置
    class DefaultConfig:
        REDIS_HOST = '127.0.0.1'
        REDIS_PORT = 6379
        REDIS_DB = 0
        REDIS_PASSWORD = '1234567' # 更新默认密码
        REDIS_KEY = 'filter'
        REDIS_DECODE_RESPONSES = True
        
        @classmethod
        def get_redis_config(cls) -> dict:
            return {
                'host': cls.REDIS_HOST,
                'port': cls.REDIS_PORT,
                'db': cls.REDIS_DB,
                'password': cls.REDIS_PASSWORD,
                'decode_responses': cls.REDIS_DECODE_RESPONSES,
                'redis_key': cls.REDIS_KEY # 添加缺失的redis_key
            }
    
    config = DefaultConfig()

# 配置日志
logging.basicConfig(level=getattr(logging, config.LOG_LEVEL))
logger = logging.getLogger(__name__)

class RedisFilter(BaseFilter):
    """基于redis的持久化的数据过滤器"""
    
    # 类级别的连接池，所有实例共享
    _connection_pool = None
    _redis_key = 'filter'
    
    def __init__(self, redis_host: Optional[str] = None, redis_port: Optional[int] = None, 
                 redis_db: Optional[int] = None, redis_key: Optional[str] = None, 
                 redis_password: Optional[str] = None, redis_decode_responses: Optional[bool] = None):
        """
        初始化Redis过滤器
        :param redis_host: Redis主机地址，如果为None则使用配置文件中的设置
        :param redis_port: Redis端口，如果为None则使用配置文件中的设置
        :param redis_db: Redis数据库编号，如果为None则使用配置文件中的设置
        :param redis_key: Redis集合的key名称，如果为None则使用配置文件中的设置
        :param redis_password: Redis密码（如果有），如果为None则使用配置文件中的设置
        :param redis_decode_responses: 是否自动解码响应，如果为None则使用配置文件中的设置
        """
        # 使用参数值或配置文件中的默认值
        redis_config = config.get_redis_config()
        self.redis_host = redis_host or redis_config['host']
        self.redis_port = redis_port or redis_config['port']
        self.redis_db = redis_db or redis_config['db']
        self.redis_key = redis_key or redis_config['redis_key']
        self.redis_password = redis_password or redis_config['password']
        self.redis_decode_responses = redis_decode_responses if redis_decode_responses is not None else redis_config['decode_responses']
        
        # 调用父类初始化
        super().__init__()
    
    def _get_connection_pool(self):
        """获取或创建Redis连接池"""
        if RedisFilter._connection_pool is None:
            try:
                RedisFilter._connection_pool = redis.ConnectionPool(
                    host=self.redis_host,
                    port=self.redis_port,
                    db=self.redis_db,
                    password=self.redis_password,
                    decode_responses=self.redis_decode_responses,
                    max_connections=10,  # 最大连接数
                    retry_on_timeout=True,  # 超时重试
                    socket_connect_timeout=5,  # 连接超时
                    socket_timeout=5  # 读写超时
                )
                logger.info("Redis连接池初始化成功")
            except Exception as e:
                logger.error(f"Redis连接池初始化失败: {e}")
                raise
        return RedisFilter._connection_pool

    def _get_storage(self):
        '''返回redis连接对象'''
        pool = self._get_connection_pool()
        client = redis.Redis(connection_pool=pool)
        return client

    def _save_data(self, hash_value: str) -> int:
        """
        使用redis的无序集合保存数据
        :param hash_value: 哈希值
        :return: 添加结果（1表示新添加，0表示已存在）
        """
        try:
            result = self.storage.sadd(self.redis_key, hash_value)
            if result == 1:
                logger.debug(f"哈希值保存成功: {hash_value}")
            else:
                logger.debug(f"哈希值已存在: {hash_value}")
            return result
        except redis.RedisError as e:
            logger.error(f"Redis保存数据失败: {e}")
            return 0
        except Exception as e:
            logger.error(f"保存哈希值时发生未知错误: {e}")
            return 0

    def _is_exist(self, hash_value: str) -> bool:
        """
        判断redis的无序集合中是否存在数据
        :param hash_value: 哈希值
        :return: 是否存在
        """
        try:
            result = self.storage.sismember(self.redis_key, hash_value)
            return bool(result)
        except redis.RedisError as e:
            logger.error(f"Redis查询数据失败: {e}")
            return False
        except Exception as e:
            logger.error(f"查询哈希值时发生未知错误: {e}")
            return False
    
    def get_stats(self) -> dict:
        """
        获取过滤器统计信息
        :return: 包含统计信息的字典
        """
        try:
            total_count = self.storage.scard(self.redis_key)
            return {
                'total_records': total_count,
                'redis_key': self.redis_key,
                'redis_db': self.redis_db
            }
        except Exception as e:
            logger.error(f"获取统计信息失败: {e}")
            return {'error': str(e)}
    
    def clear_all(self) -> bool:
        """
        清空所有数据（危险操作，谨慎使用）
        :return: True表示成功，False表示失败
        """
        try:
            result = self.storage.delete(self.redis_key)
            logger.info("所有数据已清空")
            return bool(result)
        except Exception as e:
            logger.error(f"清空数据失败: {e}")
            return False
    
    def close_connection(self):
        """关闭Redis连接池（通常在程序结束时调用）"""
        if RedisFilter._connection_pool:
            RedisFilter._connection_pool.disconnect()
            RedisFilter._connection_pool = None
            logger.info("Redis连接池已关闭")
