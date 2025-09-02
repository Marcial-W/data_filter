# -*- coding: utf-8 -*-
# @Time : 2025/8/30 17:50
# @Author : Marcial
# @Project: data_process
# @File : test_redis_connection.py
# @Software: PyCharm

import redis
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_direct_redis_connection():
    """直接连接Redis服务测试"""
    print("=== 直接Redis连接测试 ===")
    
    # 测试不同的密码配置
    passwords = [None, '', '123456', 'password', 'redis']
    
    for port in [6379, 6380]:
        print(f"\n测试端口 {port}:")
        
        for password in passwords:
            try:
                # 尝试连接
                if password:
                    r = redis.Redis(host='127.0.0.1', port=port, db=0, password=password, decode_responses=True)
                else:
                    r = redis.Redis(host='127.0.0.1', port=port, db=0, decode_responses=True)
                
                # 测试连接
                r.ping()
                
                # 获取所有keys
                keys = r.keys("*")
                print(f"  密码 '{password}': 连接成功")
                print(f"    所有keys: {keys}")
                
                # 检查特定key的类型和内容
                for key in keys:
                    key_type = r.type(key)
                    if key_type == 'set':
                        count = r.scard(key)
                        print(f"    {key} (set): {count} 个元素")
                    elif key_type == 'string':
                        length = r.strlen(key)
                        print(f"    {key} (bitmap): {length} 字节")
                    else:
                        print(f"    {key} ({key_type})")
                
                break # 连接成功就不用试其他密码了
                
            except redis.AuthenticationError:
                print(f"  密码 '{password}': 认证失败")
            except redis.ConnectionError as e:
                print(f"  密码 '{password}': 连接失败 - {e}")
            except Exception as e:
                print(f"  密码 '{password}': 其他错误 - {e}")

def test_app_redis_connection():
    """测试应用程序的Redis连接"""
    print("\n=== 应用程序Redis连接测试 ===")
    
    try:
        from request_manage.utils.data_filter.redis_filter import RedisFilter
        from request_manage.utils.data_filter.bloomfilter import BloomFilter
        
        # 测试Redis过滤器
        print("测试Redis过滤器:")
        redis_filter = RedisFilter()
        print(f"  连接配置: {redis_filter.redis_host}:{redis_filter.redis_port}")
        print(f"  使用key: {redis_filter.redis_key}")
        print(f"  密码: {redis_filter.redis_password}")
        
        try:
            stats = redis_filter.get_stats()
            print(f"  统计信息: {stats}")
        except Exception as e:
            print(f"  获取统计失败: {e}")
        
        # 测试布隆过滤器
        print("\n测试布隆过滤器:")
        bloom_filter = BloomFilter()
        print(f"  连接配置: {bloom_filter.redis_host}:{bloom_filter.redis_port}")
        print(f"  使用key: {bloom_filter.redis_key}")
        print(f"  密码: {bloom_filter.redis_password}")
        
        try:
            stats = bloom_filter.get_stats()
            print(f"  统计信息: {stats}")
        except Exception as e:
            print(f"  获取统计失败: {e}")
            
    except Exception as e:
        print(f"应用程序连接测试失败: {e}")

if __name__ == "__main__":
    print("开始Redis连接诊断...\n")
    
    test_direct_redis_connection()
    test_app_redis_connection()
    
    print("\n=== 诊断建议 ===")
    print("1. 如果6379端口显示bloom_filter数据，可能是:")
    print("   - 之前的数据残留（需要清理）")
    print("   - 应用程序配置错误（检查密码和key配置）")
    print("2. 建议操作:")
    print("   - 停止容器: docker-compose down")
    print("   - 删除数据卷: docker volume prune")
    print("   - 重新启动: docker-compose up -d") 