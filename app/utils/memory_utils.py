#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
内存管理工具模块
"""

import gc
import psutil
import os
from functools import wraps
from flask import current_app
from ..config import MAX_MEMORY_USAGE_MB


def monitor_memory(func):
    """内存监控装饰器"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        # 获取当前进程
        process = psutil.Process(os.getpid())
        
        # 记录开始时的内存使用
        start_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        try:
            # 执行函数
            result = func(*args, **kwargs)
            
            # 检查内存使用
            current_memory = process.memory_info().rss / 1024 / 1024  # MB
            memory_used = current_memory - start_memory
            
            if memory_used > MAX_MEMORY_USAGE_MB:
                current_app.logger.warning(
                    f"函数 {func.__name__} 使用了过多内存: {memory_used:.2f}MB"
                )
            
            return result
            
        finally:
            # 强制垃圾回收
            gc.collect()
            
    return wrapper


def check_available_memory():
    """检查可用内存"""
    memory = psutil.virtual_memory()
    available_mb = memory.available / 1024 / 1024
    
    if available_mb < MAX_MEMORY_USAGE_MB * 2:  # 保留2倍的安全余量
        raise MemoryError(f"可用内存不足: {available_mb:.2f}MB")
    
    return available_mb


def force_cleanup():
    """强制清理内存"""
    gc.collect()
    return True
