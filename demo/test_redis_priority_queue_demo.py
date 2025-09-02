# -*- coding: utf-8 -*-  # 优先队列演示
from redis_queue import get_redis_queue_cls  # 工厂

if __name__=='__main__':
    pq=get_redis_queue_cls('priority')()  # 实例
    pq.put({'ali':100,'bob':50,'carl':150})  # 入
    print(pq.get())  # 出一条
    print(pq.get())  # 再出一条 