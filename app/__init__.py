#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Flask应用程序初始化模块
"""

import os
from flask import Flask
from dotenv import load_dotenv

def create_app():
    """创建并配置Flask应用程序"""
    # 在这里加载环境变量，确保在config导入之前
    load_dotenv()
    
    app = Flask(__name__)
    
    # 基本配置
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 最大16MB文件
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    
    # 注册蓝图
    from .routes import main_bp
    app.register_blueprint(main_bp)
    
    # 注册错误处理器
    from .error_handlers import register_error_handlers
    register_error_handlers(app)
    
    return app
