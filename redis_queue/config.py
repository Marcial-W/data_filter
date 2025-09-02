# -*- coding: utf-8 -*-  # 统一配置入口
# 所有可调变量集中此处，避免重复定义  # 简洁

CONFIG={
    'host':'localhost',
    'port':6379,
    'db':0,
    'password':1234567,
    'decode_responses':True,
    'cluster_nodes':None,
    'queue_name_default':'redis_queue',
    'priority_queue_name':'priority_redis_queue',
    'use_lock':True,
    'lock_name':'redis_queue_lock',
    'lock_ttl':5,
}  # 基础配置

get=lambda k,default=None:CONFIG.get(k,default)  # 快捷读取 