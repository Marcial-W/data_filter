# -*- coding: utf-8 -*-
# @Time : 2025/8/30 13:27
# @Author : Marcial
# @Project: data_filter
# @File : request.py
# @Software: PyCharm

from typing import Dict, Any, Optional # 添加类型提示

class Request:
    """HTTP请求对象，支持URL、方法、查询参数、请求头和请求体"""
    
    def __init__(self, url: str, method: str = 'GET', query: Dict[str, Any] = None, 
                 headers: Dict[str, Any] = None, body: Dict[str, Any] = None, name: str = None):
        self._url = url
        self._method = method.upper()
        self._query = query or {}
        self._headers = headers or {}
        self._body = body or {}
        self._name = None # 请求名称
        
        # 验证参数类型
        self._validate_parameters()
    
    def _validate_parameters(self):
        """验证参数类型和格式"""
        if not isinstance(self._query, dict):
            raise TypeError("query必须是字典类型")
        if not isinstance(self._headers, dict):
            raise TypeError("headers必须是字典类型")
        if not isinstance(self._body, dict):
            raise TypeError("body必须是字典类型")
        if not self._url or not isinstance(self._url, str):
            raise ValueError("url必须是有效的字符串")
    
    @property
    def url(self) -> str:
        """获取请求URL"""
        return self._url
    
    @property
    def method(self) -> str:
        """获取请求方法"""
        return self._method
    
    @property
    def query(self) -> Dict[str, Any]:
        """获取查询参数"""
        return self._query.copy() # 返回副本防止外部修改
    
    @property
    def headers(self) -> Dict[str, Any]:
        """获取请求头"""
        return self._headers.copy() # 返回副本防止外部修改
    
    @property
    def body(self) -> Dict[str, Any]:
        """获取请求体"""
        return self._body.copy() # 返回副本防止外部修改
    
    @property
    def name(self) -> Optional[str]:
        """获取请求名称"""
        return self._name
    
    @name.setter
    def name(self, value: str):
        """设置请求名称"""
        self._name = value
    
    def add_query_param(self, key: str, value: Any):
        """添加查询参数"""
        self._query[key] = value
    
    def add_header(self, key: str, value: str):
        """添加请求头"""
        self._headers[key] = value
    
    def add_body_param(self, key: str, value: Any):
        """添加请求体参数"""
        self._body[key] = value
    
    def __str__(self) -> str:
        """字符串表示"""
        return f"Request({self._method} {self._url}, name={self._name})"
    
    def __repr__(self) -> str:
        """详细字符串表示"""
        return f"Request(url='{self._url}', method='{self._method}', query={self._query}, headers={self._headers}, body={self._body}, name='{self._name}')"


