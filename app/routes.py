#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
主要路由模块
"""

import gc
from flask import Blueprint, request, jsonify, render_template
from werkzeug.utils import secure_filename

from .utils import (
    allowed_file,
    get_file_size_mb,
    calculate_md5,
    compress_image,
    get_content_type,
    upload_to_r2,
    delete_from_r2,
    generate_file_path,
    generate_image_url
)
from .config import MAX_FILE_SIZE_MB

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def index():
    """主页面"""
    return render_template('index.html')


@main_bp.route('/upload', methods=['POST'])
def upload_file():
    """处理文件上传"""
    file_data = None
    final_data = None
    
    try:
        # 检查是否有文件
        if 'file' not in request.files:
            return jsonify({'error': '没有选择文件'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': '没有选择文件'}), 400
        
        # 验证文件类型
        if not allowed_file(file.filename):
            return jsonify({'error': '不支持的文件类型'}), 400
        
        # 读取文件数据
        file_data = file.read()
        original_size_mb = get_file_size_mb(file_data)
        
        # 检查文件大小限制
        if original_size_mb > MAX_FILE_SIZE_MB:
            return jsonify({'error': f'文件太大，最大支持{MAX_FILE_SIZE_MB}MB'}), 400
        
        # 获取文件扩展名
        filename = secure_filename(file.filename)
        file_extension = filename.rsplit('.', 1)[1].lower()
        
        # 检查是否需要压缩
        compress = request.form.get('compress', '').lower() == 'true'
        quality = int(request.form.get('quality', 80))
        
        if compress:
            # 压缩图片 - 压缩后立即释放原始数据
            try:
                compress_format = 'JPEG' if file_extension in ['jpg', 'jpeg'] else 'PNG'
                final_data = compress_image(file_data, quality, compress_format)
                # 立即释放原始文件数据内存
                del file_data
                file_data = None
                print(f"图片压缩完成，质量: {quality}%")
            except Exception as e:
                print(f"图片压缩失败: {e}")
                return jsonify({'error': f'图片压缩失败: {str(e)}'}), 500
        else:
            # 不压缩时直接使用原始数据
            final_data = file_data
            file_data = None  # 避免重复引用
        
        final_size_mb = get_file_size_mb(final_data)
        
        # 计算MD5哈希
        md5_hash = calculate_md5(final_data)
        
        # 生成存储路径
        storage_path = generate_file_path(md5_hash, file_extension)
        
        # 上传到R2
        content_type = get_content_type(file_extension)
        upload_success = upload_to_r2(final_data, storage_path, content_type)
        
        # 上传完成后立即释放内存
        del final_data
        final_data = None
        
        if not upload_success:
            return jsonify({'error': '上传到云存储失败，请检查配置'}), 500
        
        # 生成最终URL
        image_url = generate_image_url(storage_path)
        
        # 返回结果
        return jsonify({
            'success': True,
            'original_size_mb': round(original_size_mb, 2),
            'final_size_mb': round(final_size_mb, 2),
            'md5_hash': md5_hash,
            'storage_path': storage_path,
            'image_url': image_url,
            'compressed': compress,
            'compression_quality': quality if compress else None
        })
        
    except Exception as e:
        print(f"上传处理失败: {e}")
        return jsonify({'error': f'服务器内部错误: {str(e)}'}), 500
    finally:
        # 确保内存清理
        if 'file_data' in locals() and file_data is not None:
            del file_data
        if 'final_data' in locals() and final_data is not None:
            del final_data
        # 强制垃圾回收
        gc.collect()


@main_bp.route('/delete', methods=['POST'])
def delete_file():
    """删除上传的文件"""
    try:
        data = request.get_json()
        if not data or 'storage_path' not in data:
            return jsonify({'error': '缺少必需参数: storage_path'}), 400
        
        storage_path = data['storage_path']
        
        # 从R2删除文件
        if delete_from_r2(storage_path):
            return jsonify({
                'success': True,
                'message': '文件删除成功'
            })
        else:
            return jsonify({'error': '删除文件失败，请稍后重试'}), 500
            
    except Exception as e:
        print(f"删除文件失败: {e}")
        return jsonify({'error': f'服务器内部错误: {str(e)}'}), 500
