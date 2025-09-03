# -*- coding: utf-8 -*-
# @Time : 2025/8/30 13:25
# @Author : Marcial
# @Project: data_filter
# @File : __init__.py
# @Software: PyCharm

from urllib.parse import urlparse, parse_qsl, urlencode
from typing import Any, Dict, List, Tuple

class RequestFilter:
    def __init__(self, filter_obj):
        self.filter_obj = filter_obj
        self._cache = {}

    def is_exist(self, request_obj) -> bool:
        try:
            data = self._get_request_filter_data(request_obj)
            cache_key = hash(data)
            if cache_key in self._cache:
                return self._cache[cache_key]
            result = self.filter_obj.is_exist(data)
            self._cache[cache_key] = result
            return result
        except Exception as e:
            print(f"检查请求存在性时出错: {e}")
            return False

    def mark_request(self, request_obj) -> bool:
        try:
            data = self._get_request_filter_data(request_obj)
            cache_key = hash(data)
            result = self.filter_obj.save_data(data)
            if result:
                self._cache[cache_key] = True
            return result
        except Exception as e:
            print(f"标记请求时出错: {e}")
            return False

    def _get_request_filter_data(self, request_obj) -> str:
        # 支持字典和对象两种访问方式
        if isinstance(request_obj, dict):
            url = request_obj.get('url', '')
            method = request_obj.get('method', 'GET')
            query = request_obj.get('query', {})
            headers = request_obj.get('headers', {})
            body = request_obj.get('body', {})
        else:
            url = getattr(request_obj, 'url', '')
            method = getattr(request_obj, 'method', 'GET')
            query = getattr(request_obj, 'query', {})
            headers = getattr(request_obj, 'headers', {})
            body = getattr(request_obj, 'body', {})
        
        # 处理query参数
        if isinstance(query, str):
            if not query:
                query = {}
            elif '=' in query:  # 键值对格式
                query = dict(parse_qsl(query))
            else:  # 简单字符串，作为额外参数
                query = {'extra_param': query}  # 转换为字典格式
        elif hasattr(query, 'items'):
            query = dict(query.items())
        else:
            query = {}
        
        # 处理body参数
        if isinstance(body, str):
            body = {} if not body else dict(parse_qsl(body))
        elif hasattr(body, 'items'):
            body = dict(body.items())
        else:
            body = {}

        parsed_url = urlparse(url)
        url_query = parse_qsl(parsed_url.query)
        url_without_query = parsed_url.scheme + "://" + parsed_url.hostname + (":" + str(parsed_url.port) if parsed_url.port else "") + parsed_url.path
        
        all_query = sorted(set(list(query.items()) + url_query))
        url_with_query = url_without_query + "?" + urlencode(all_query) if all_query else url_without_query

        method = method.lower()
        headers_str = str(sorted(headers.items())) if hasattr(headers, 'items') else str(headers)
        body_str = str(sorted(body.items())) if hasattr(body, 'items') else str(body)

        return url_with_query + method + headers_str + body_str
    
    def clear_cache(self):
        self._cache.clear()
    
    def get_stats(self):
        try:
            return self.filter_obj.get_stats()
        except:
            return {'error': '无法获取统计信息'}
