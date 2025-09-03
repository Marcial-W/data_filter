# -*- coding: utf-8 -*-
# @Time : 2025/8/30 13:26
# @Author : Marcial
# @Project: data_filter
# @File : __init__.py
# @Software: PyCharm

from typing import Type, Dict, Any # 添加类型提示
from .data_filter import MemoryFilter, RedisFilter, MySQLFilter
from .data_filter.bloomfilter import BloomFilter

# 过滤器类缓存
_filter_cache: Dict[str, Type] = {}

def get_filter_class(class_name: str) -> Type:
    """
    根据名称获取对应的过滤器类
    
    Args:
        class_name: 过滤器类型名称 ('memory', 'redis', 'mysql', 'bloom')
    
    Returns:
        对应的过滤器类
        
    Raises:
        ValueError: 当过滤器类型不支持时
    """
    if not isinstance(class_name, str):
        raise TypeError("class_name必须是字符串类型")
    
    class_name = class_name.lower()
    
    # 检查缓存
    if class_name in _filter_cache:
        return _filter_cache[class_name]
    
    try:
        if class_name == 'memory':
            _filter_cache[class_name] = MemoryFilter
        elif class_name == 'redis':
            _filter_cache[class_name] = RedisFilter
        elif class_name == 'mysql':
            _filter_cache[class_name] = MySQLFilter
        elif class_name == 'bloom':
            _filter_cache[class_name] = BloomFilter
        else:
            raise ValueError(f"不支持的过滤器类型: {class_name},支持的过滤器为[redis,mysql,bloom,memory]")
        
        return _filter_cache[class_name]
        
    except ImportError as e:
        raise ImportError(f"导入过滤器类失败: {e}")
    except Exception as e:
        raise RuntimeError(f"获取过滤器类时出错: {e}")

def get_available_filters() -> list:
    """获取所有可用的过滤器类型"""
    return ['memory', 'redis', 'mysql', 'bloom']

def clear_filter_cache():
    """清空过滤器类缓存"""
    _filter_cache.clear()