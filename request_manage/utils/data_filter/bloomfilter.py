# -*- coding: utf-8 -*-
# @Time : 2025/8/24 15:40
# @Author : Marcial
# @Project: data_filter
# @File : bloomfilter.py
# @Software: PyCharm

import hashlib
import redis
import logging
from typing import Optional

# 导入配置
try:
    from request_manage.utils.config import config
except ImportError:
    # 如果配置文件不存在，使用默认配置
    class DefaultConfig:
        REDIS_BLOOM_HOST = '127.0.0.1'
        REDIS_BLOOM_PORT = 6380 # 使用专用端口
        REDIS_BLOOM_DB = 0
        REDIS_BLOOM_PASSWORD = '12345678' # 更新默认密码
        REDIS_BLOOM_KEY = 'bloom_filter'
        REDIS_BLOOM_DECODE_RESPONSES = True
        LOG_LEVEL = 'INFO'

        @classmethod
        def get_redis_bloom_config(cls) -> dict:
            return {
                'host': cls.REDIS_BLOOM_HOST,
                'port': cls.REDIS_BLOOM_PORT,
                'db': cls.REDIS_BLOOM_DB,
                'password': cls.REDIS_BLOOM_PASSWORD,
                'decode_responses': cls.REDIS_BLOOM_DECODE_RESPONSES,
                'redis_key': cls.REDIS_BLOOM_KEY
            }

    config = DefaultConfig()

# 配置日志
logging.basicConfig(level=getattr(logging, getattr(config, 'LOG_LEVEL', 'INFO')))
logger = logging.getLogger(__name__)

class MultipleHash(object):
    """多重哈希类，用于生成多个哈希值"""

    def __init__(self, salts, hash_func='md5'):
        """
        初始化多重哈希
        :param salts: 盐值列表，至少3个
        :param hash_func: 哈希函数名称
        """
        try:
            if len(salts) < 3:
                raise ValueError("salts length must be greater than or equal to 3")
            self.salts = salts
        except TypeError:
            raise TypeError("salts must be a list or tuple")

        self.hash_func = getattr(hashlib, hash_func)

    def _safe_data(self, data) -> bytes:
        """
        安全处理原始数据，将其转换为二进制类型
        :param data: 原始数据（str, bytes, 其他类型）
        :return: bytes 类型数据
        """
        if isinstance(data, bytes):
            return data
        elif isinstance(data, str):
            return data.encode("utf-8")
        else:
            # 统一转成字符串再编码，避免 TypeError
            return str(data).encode("utf-8")

    def get_hash_value(self, data):
        """
        获取多个哈希值
        :param data: 输入数据
        :return: 哈希值列表
        """
        hash_values = []
        data = self._safe_data(data)
        for salt in self.salts:
            salt = self._safe_data(salt)
            hash_obj = self.hash_func()
            hash_obj.update(data)
            hash_obj.update(salt)
            ret = hash_obj.hexdigest()
            hash_values.append(int(ret, 16))
        return hash_values

class BloomFilter(object):
    """基于Redis的布隆过滤器实现"""

    # 类级别的连接池，所有实例共享
    _connection_pool = None
    _redis_key = 'bloom_filter'

    def __init__(self, redis_host: Optional[str] = None, redis_port: Optional[int] = None,
                 redis_db: Optional[int] = None, redis_key: Optional[str] = None,
                 redis_password: Optional[str] = None, redis_decode_responses: Optional[bool] = None,
                 hash_salts: Optional[list] = None):
        """
        初始化布隆过滤器
        :param redis_host: Redis主机地址，如果为None则使用配置文件中的设置
        :param redis_port: Redis端口，如果为None则使用配置文件中的设置
        :param redis_db: Redis数据库编号，如果为None则使用配置文件中的设置
        :param redis_key: Redis位图的key名称，如果为None则使用配置文件中的设置
        :param redis_password: Redis密码（如果有），如果为None则使用配置文件中的设置
        :param redis_decode_responses: 是否自动解码响应，如果为None则使用配置文件中的设置
        :param hash_salts: 哈希盐值列表，如果为None则使用默认值
        """
        # 使用布隆过滤器专用的Redis配置
        redis_config = config.get_redis_bloom_config()
        self.redis_host = redis_host or redis_config['host']
        self.redis_port = redis_port or redis_config['port']
        self.redis_db = redis_db or redis_config['db']
        self.redis_key = redis_key or redis_config['redis_key']
        self.redis_password = redis_password or redis_config['password']
        self.redis_decode_responses = redis_decode_responses if redis_decode_responses is not None else redis_config['decode_responses']
        
        # 初始化Redis客户端和多重哈希
        self.redis_client = self._get_redis_client()
        self.multiple_hash = MultipleHash(hash_salts or ['123', '456', '789'])

    def _get_connection_pool(self):
        """获取或创建Redis连接池"""
        if BloomFilter._connection_pool is None:
            try:
                BloomFilter._connection_pool = redis.ConnectionPool(
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
        return BloomFilter._connection_pool

    def _get_redis_client(self):
        '''返回redis连接对象'''
        pool = self._get_connection_pool()
        client = redis.Redis(connection_pool=pool)
        return client

    def save_data(self, data) -> bool:
        """
        保存数据到布隆过滤器
        :param data: 要保存的数据
        :return: 是否保存成功
        """
        try:
            hash_values = self.multiple_hash.get_hash_value(data)
            offsets = []
            for hash_value in hash_values:
                offset = self._get_offset(hash_value)
                self._set_bit(offset)
                offsets.append(offset)
            logger.debug(f"数据{data}已映射到Redis位图{self.redis_key}中")
            return offsets
        except redis.RedisError as e:
            logger.error(f"Redis保存数据失败: {e}")
        except Exception as e:
            logger.error(f"保存数据时发生未知错误: {e}")

    def _set_bit(self, offset):
        """设置位图中的位"""
        try:
            self.redis_client.setbit(self.redis_key, offset, 1)
        except Exception as e:
            logger.error(f"设置位图失败: {e}")
            raise

    def _get_offset(self, hash_value):
        """计算位图偏移量"""
        return hash_value % (2 ** 32)

    def is_exist(self, data) -> bool:
        """
        检查数据是否存在于布隆过滤器中
        :param data: 要检查的数据
        :return: 是否存在（可能存在误判）
        """
        try:
            hash_values = self.multiple_hash.get_hash_value(data)
            for hash_value in hash_values:
                offset = self._get_offset(hash_value)
                v = self.redis_client.getbit(self.redis_key, offset)
                if v == 0:
                    return False
            logger.debug(f"数据{data}可能存在于Redis位图{self.redis_key}中")
            return True
        except redis.RedisError as e:
            logger.error(f"Redis查询数据失败: {e}")
            return False
        except Exception as e:
            logger.error(f"查询数据时发生未知错误: {e}")
            return False

    def get_stats(self) -> dict:
        """
        获取布隆过滤器统计信息
        :return: 包含统计信息的字典
        """
        try:
            # 获取位图中设置的位数
            bit_count = self.redis_client.bitcount(self.redis_key)
            # 获取位图长度
            bit_length = self.redis_client.strlen(self.redis_key) * 8 if self.redis_client.exists(self.redis_key) else 0
            
            return {
                'total_bits_set': bit_count,
                'bitmap_length': bit_length,
                'redis_key': self.redis_key,
                'redis_db': self.redis_db,
                'hash_functions': len(self.multiple_hash.salts)
            }
        except Exception as e:
            logger.error(f"获取统计信息失败: {e}")
            return {'error': str(e)}

    def clear_all(self) -> bool:
        """
        清空布隆过滤器（危险操作，谨慎使用）
        :return: True表示成功，False表示失败
        """
        try:
            result = self.redis_client.delete(self.redis_key)
            logger.info("布隆过滤器数据已清空")
            return bool(result)
        except Exception as e:
            logger.error(f"清空数据失败: {e}")
            return False

    def close_connection(self):
        """关闭Redis连接池（通常在程序结束时调用）"""
        if BloomFilter._connection_pool:
            BloomFilter._connection_pool.disconnect()
            BloomFilter._connection_pool = None
            logger.info("Redis连接池已关闭")

    # 保持向后兼容的方法名
    def is_exists(self, data) -> bool:
        """向后兼容的方法名"""
        return self.is_exist(data)
