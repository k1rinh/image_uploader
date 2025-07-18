#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
图片处理工具模块
"""

import io
import hashlib
from PIL import Image
from flask import current_app
from ..config import ALLOWED_EXTENSIONS


def allowed_file(filename: str) -> bool:
    """检查文件类型是否允许"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def get_file_size_mb(file_data: bytes) -> float:
    """计算文件大小（MB）"""
    return len(file_data) / (1024 * 1024)


def calculate_md5(file_data: bytes) -> str:
    """计算文件的MD5哈希值"""
    md5_hash = hashlib.md5()
    md5_hash.update(file_data)
    return md5_hash.hexdigest()


def compress_image(image_data: bytes, quality: int = 80, format: str = 'JPEG') -> bytes:
    """压缩图片并返回压缩后的字节数据"""
    img = None
    background = None
    output = None
    input_stream = None
    
    try:
        # 将字节数据转换为PIL图像对象
        input_stream = io.BytesIO(image_data)
        img = Image.open(input_stream)
        
        # 如果是PNG格式且有透明度，转换为RGBA模式
        if img.mode in ('RGBA', 'LA') or (img.mode == 'P' and 'transparency' in img.info):
            if format.upper() == 'JPEG':
                # JPEG不支持透明度，创建白色背景
                background = Image.new('RGB', img.size, (255, 255, 255))
                if img.mode == 'P':
                    img = img.convert('RGBA')
                background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                # 立即释放原图内存
                img.close()
                img = background
                background = None
        else:
            # 确保图像为RGB模式（JPEG需要）
            if img.mode != 'RGB' and format.upper() == 'JPEG':
                rgb_img = img.convert('RGB')
                img.close()
                img = rgb_img
        
        # 压缩图像
        output = io.BytesIO()
        img.save(output, format=format, quality=quality, optimize=True)
        compressed_data = output.getvalue()
        
        return compressed_data
        
    except Exception as e:
        current_app.logger.error(f"图片压缩失败: {e}")
        raise
    finally:
        # 确保释放所有资源
        if img is not None:
            img.close()
        if background is not None:
            background.close()
        if output is not None:
            output.close()
        if input_stream is not None:
            input_stream.close()


def get_content_type(extension: str) -> str:
    """根据文件扩展名获取Content-Type"""
    content_types = {
        'jpg': 'image/jpeg',
        'jpeg': 'image/jpeg',
        'png': 'image/png',
        'gif': 'image/gif',
        'webp': 'image/webp'
    }
    return content_types.get(extension.lower(), 'application/octet-stream')
