#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
主要路由模块
"""

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

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def index():
    """主页面"""
    return render_template('index.html')


@main_bp.route('/upload', methods=['POST'])
def upload_file():
    """处理文件上传"""
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
        
        # 获取文件扩展名
        filename = secure_filename(file.filename)
        file_extension = filename.rsplit('.', 1)[1].lower()
        
        # 检查是否需要压缩
        compress = request.form.get('compress', '').lower() == 'true'
        quality = int(request.form.get('quality', 80))
        
        final_data = file_data
        
        if compress:
            # 压缩图片
            try:
                # 确定压缩格式
                compress_format = 'JPEG' if file_extension in ['jpg', 'jpeg'] else 'PNG'
                final_data = compress_image(file_data, quality, compress_format)
                print(f"图片压缩完成，质量: {quality}%")
            except Exception as e:
                print(f"图片压缩失败: {e}")
                return jsonify({'error': f'图片压缩失败: {str(e)}'}), 500
        
        final_size_mb = get_file_size_mb(final_data)
        
        # 计算MD5哈希
        md5_hash = calculate_md5(final_data)
        
        # 生成存储路径
        storage_path = generate_file_path(md5_hash, file_extension)
        
        # 上传到R2
        content_type = get_content_type(file_extension)
        if not upload_to_r2(final_data, storage_path, content_type):
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
