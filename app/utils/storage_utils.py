#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
云存储工具模块 - Cloudflare R2
"""

import datetime
import boto3
from flask import current_app
from ..config import R2_CONFIG, CUSTOM_DOMAIN


def get_r2_client():
    """创建并返回R2 S3兼容客户端"""
    try:
        return boto3.client(
            's3',
            endpoint_url=R2_CONFIG['endpoint'],
            aws_access_key_id=R2_CONFIG['access_key'],
            aws_secret_access_key=R2_CONFIG['secret_key'],
            region_name='auto'  # Cloudflare R2使用'auto'区域
        )
    except Exception as e:
        current_app.logger.error(f"创建R2客户端失败: {e}")
        return None


def upload_to_r2(file_data: bytes, file_name: str, content_type: str) -> bool:
    """上传文件到Cloudflare R2存储"""
    try:
        r2_client = get_r2_client()
        if not r2_client:
            return False
        
        r2_client.put_object(
            Bucket=R2_CONFIG['bucket_name'],
            Key=file_name,
            Body=file_data,
            ContentType=content_type,
            CacheControl='public, max-age=31536000'  # 缓存1年
        )
        return True
    except Exception as e:
        current_app.logger.error(f"上传到R2失败: {e}")
        return False


def delete_from_r2(file_name: str) -> bool:
    """从Cloudflare R2存储删除文件"""
    try:
        r2_client = get_r2_client()
        if not r2_client:
            return False
        
        r2_client.delete_object(
            Bucket=R2_CONFIG['bucket_name'],
            Key=file_name
        )
        return True
    except Exception as e:
        current_app.logger.error(f"从R2删除文件失败: {e}")
        return False


def generate_file_path(md5_hash: str, extension: str) -> str:
    """生成文件存储路径"""
    now = datetime.datetime.now()
    year = now.strftime('%Y')
    month = now.strftime('%m')
    return f"img/{year}/{month}/{md5_hash}.{extension}"


def generate_image_url(storage_path: str) -> str:
    """生成最终的图片URL"""
    return f"https://{CUSTOM_DOMAIN}/{storage_path}"
