#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
图片上传器测试脚本
用于测试核心功能而无需实际的R2配置
"""

import io
import hashlib
from PIL import Image

def test_image_compression():
    """测试图片压缩功能"""
    print("=== 测试图片压缩功能 ===")
    
    # 创建一个测试图片
    img = Image.new('RGB', (800, 600), color='red')
    
    # 保存为字节数据
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='JPEG', quality=95)
    original_data = img_bytes.getvalue()
    original_size = len(original_data) / 1024 / 1024
    
    print(f"原始图片大小: {original_size:.2f} MB")
    
    # 测试不同质量级别的压缩
    qualities = [90, 80, 70, 60, 50]
    
    for quality in qualities:
        compressed_bytes = io.BytesIO()
        img.save(compressed_bytes, format='JPEG', quality=quality, optimize=True)
        compressed_data = compressed_bytes.getvalue()
        compressed_size = len(compressed_data) / 1024 / 1024
        compression_ratio = (1 - compressed_size / original_size) * 100
        
        print(f"质量 {quality}%: {compressed_size:.2f} MB (压缩率: {compression_ratio:.1f}%)")

def test_md5_calculation():
    """测试MD5哈希计算"""
    print("\n=== 测试MD5哈希计算 ===")
    
    test_data = b"Hello, World!"
    md5_hash = hashlib.md5()
    md5_hash.update(test_data)
    result = md5_hash.hexdigest()
    
    expected = "65a8e27d8879283831b664bd8b7f0ad4"
    print(f"测试数据: {test_data}")
    print(f"计算结果: {result}")
    print(f"预期结果: {expected}")
    print(f"测试{'通过' if result == expected else '失败'}")

def test_file_path_generation():
    """测试文件路径生成"""
    print("\n=== 测试文件路径生成 ===")
    
    import datetime
    
    md5_hash = "d41d8cd98f00b204e9800998ecf8427e"
    extension = "jpg"
    
    now = datetime.datetime.now()
    year = now.strftime('%Y')
    month = now.strftime('%m')
    expected_path = f"img/{year}/{month}/{md5_hash}.{extension}"
    
    print(f"MD5哈希: {md5_hash}")
    print(f"文件扩展名: {extension}")
    print(f"生成路径: {expected_path}")

def test_file_size_calculation():
    """测试文件大小计算"""
    print("\n=== 测试文件大小计算 ===")
    
    # 创建不同大小的测试数据
    test_sizes = [1024, 1024*1024, 2*1024*1024, 5*1024*1024]  # 1KB, 1MB, 2MB, 5MB
    
    for size in test_sizes:
        test_data = b'0' * size
        size_mb = len(test_data) / (1024 * 1024)
        print(f"数据大小: {size} bytes = {size_mb:.2f} MB")

def main():
    """运行所有测试"""
    print("图片上传器核心功能测试")
    print("=" * 50)
    
    try:
        test_image_compression()
        test_md5_calculation()
        test_file_path_generation()
        test_file_size_calculation()
        
        print("\n" + "=" * 50)
        print("所有测试完成！")
        
    except ImportError as e:
        print(f"导入错误: {e}")
        print("请先安装依赖包: pip install pillow")
    except Exception as e:
        print(f"测试过程中出现错误: {e}")

if __name__ == "__main__":
    main()
