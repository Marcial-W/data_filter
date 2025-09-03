# -*- coding: utf-8 -*-
# @Time : 2025/9/3 10:51
# @Author : Marcial
# @Project: data_filter
# @File : request_schedual.py
# @Software: PyCharm

import logging
from typing import Dict, Any, Optional
from request_manage.utils import get_filter_class
from request_manage.request_filter import RequestFilter
from redis_queue import get_redis_queue_cls

class RequestSchedule(object):
    def __init__(self, log_level=logging.INFO):
        self.queue: Dict[str, Any] = {}
        self.filter_of_queue: Dict[str, str] = {}
        self._setup_logger(log_level)

    def _setup_logger(self, level):
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self.logger.setLevel(level)
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)

    def add_request(self, request_obj: Dict[str, Any], filter_name: str, queue_name: str) -> bool:
        try:
            filter = self._get_filter(filter_name)
            queue = self._get_queue(queue_name)
            self.queue[queue_name] = queue
            self.filter_of_queue[queue_name] = filter_name
            
            if filter.is_exist(request_obj):
                self.logger.warning(f"请求已存在，跳过添加: {request_obj.get('url', 'unknown')}")
                return False
            else:
                queue.put(request_obj)
                filter.mark_request(request_obj)
                self.logger.info(f"成功添加请求到队列 {queue_name}: {request_obj.get('url', 'unknown')}")
                return True
        except Exception as e:
            self.logger.error(f"添加请求失败: {e}")
            return False

    def _get_filter(self, filter_name: str) -> RequestFilter:
        try:
            filter_cls = get_filter_class(filter_name)
            return RequestFilter(filter_cls())
        except Exception as e:
            self.logger.error(f"创建过滤器失败 {filter_name}: {e}")
            raise

    def _get_queue(self, queue_name: str):
        try:
            queue_cls = get_redis_queue_cls(queue_name)
            return queue_cls()
        except Exception as e:
            self.logger.error(f"创建队列失败 {queue_name}: {e}")
            raise

    def get_request(self, queue_name: str, block: bool = False) -> Optional[Any]:
        try:
            if queue_name not in self.queue:
                self.logger.error(f"队列 {queue_name} 不存在")
                return None
            result = self.queue[queue_name].get(block=block)
            self.logger.info(f"从队列 {queue_name} 获取请求成功")
            return result
        except Exception as e:
            self.logger.error(f"从队列 {queue_name} 获取请求失败: {e}")
            return None

    def get_queue_stats(self) -> Dict[str, Any]:
        stats = {}
        for queue_name, queue in self.queue.items():
            try:
                stats[queue_name] = {
                    'size': queue.qsize(),
                    'filter': self.filter_of_queue.get(queue_name, 'unknown')
                }
            except Exception as e:
                self.logger.error(f"获取队列 {queue_name} 统计信息失败: {e}")
                stats[queue_name] = {'error': str(e)}
        return stats

    def clear_queue(self, queue_name: str) -> bool:
        try:
            if queue_name in self.queue:
                # 清空队列
                while not self.queue[queue_name].empty():
                    self.queue[queue_name].get_nowait()
                self.logger.info(f"队列 {queue_name} 已清空")
                return True
            else:
                self.logger.warning(f"队列 {queue_name} 不存在")
                return False
        except Exception as e:
            self.logger.error(f"清空队列 {queue_name} 失败: {e}")
            return False

if __name__ == "__main__":
    # 配置根日志级别
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    request_list = []
    for i in range(1, 4):
        request = {"url": f"https://baidu.com/home?query=dajiahao&id={i}",
                   "method": "GET",
                   "query": f"param{i}",
                   "headers": {},
                   "body": ""}
        request_list.append(request)

    request_schedule = RequestSchedule()
    for i, req in enumerate(request_list):
        print(f"处理第{i+1}个请求:")
        if request_schedule.add_request(req, "redis", "lifo"):
            result = request_schedule.get_request("lifo", block=False)
            if result:
                print(f"获取到请求: {result}")
        print("-" * 30)
    
    # 显示队列统计信息
    stats = request_schedule.get_queue_stats()
    print(f"队列统计信息: {stats}")