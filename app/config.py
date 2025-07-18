#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
应用程序配置模块
"""

import os

# 支持的文件扩展名
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

# 自定义域名
CUSTOM_DOMAIN = 'static.k1r.in'

# R2存储配置
R2_CONFIG = {
    'endpoint': os.getenv('R2_ENDPOINT'),
    'access_key': os.getenv('R2_ACCESS_KEY_ID'),
    'secret_key': os.getenv('R2_SECRET_ACCESS_KEY'),
    'bucket_name': os.getenv('R2_BUCKET_NAME'),
}

# 必需的环境变量
REQUIRED_ENV_VARS = [
    'R2_ENDPOINT',
    'R2_ACCESS_KEY_ID', 
    'R2_SECRET_ACCESS_KEY',
    'R2_BUCKET_NAME'
]

def validate_config():
    """验证必要的配置是否存在"""
    missing_vars = [var for var in REQUIRED_ENV_VARS if not os.getenv(var)]
    if missing_vars:
        raise ValueError(f"缺少必要的环境变量: {', '.join(missing_vars)}")
    return True
