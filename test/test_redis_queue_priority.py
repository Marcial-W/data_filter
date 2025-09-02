# -*- coding: utf-8 -*-  # 优先队列基础测试
import pytest
from redis_queue import get_redis_queue_cls

@pytest.mark.redis
def test_priority_put_get():  # 基本入队出队
    pq=get_redis_queue_cls('priority')(name='test_pq_put_get')  # 实例
    pq.redis.delete(pq.name)  # 清空
    pq.put({'ali':100,'bob':50,'carl':150})  # 入
    a=pq.get(); b=pq.get()  # 出
    assert a and isinstance(a,list)  # 返回列表
    assert len(a)==1 and a[0] in {'ali','bob','carl'}  # 值有效
    assert b and isinstance(b,list)

@pytest.mark.redis
def test_priority_order():  # 校验权重顺序
    pq=get_redis_queue_cls('priority')(name='test_pq_order')
    pq.redis.delete(pq.name)  # 清空
    pq.put({'t1':1,'t2':3,'t3':2})
    first=pq.get()[0]; second=pq.get()[0]
    assert first=='t2' and second in {'t3','t1'}  # 最大优先 