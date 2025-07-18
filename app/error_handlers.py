#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
错误处理模块
"""

from flask import jsonify


def register_error_handlers(app):
    """注册错误处理器"""
    
    @app.errorhandler(413)
    def request_entity_too_large(error):
        """处理文件过大错误"""
        return jsonify({'error': '文件太大，最大支持16MB'}), 413

    @app.errorhandler(500)
    def internal_server_error(error):
        """处理服务器内部错误"""
        app.logger.error(f"服务器内部错误: {error}")
        return jsonify({'error': '服务器内部错误'}), 500

    @app.errorhandler(404)
    def not_found(error):
        """处理404错误"""
        return jsonify({'error': '页面未找到'}), 404

    @app.errorhandler(400)
    def bad_request(error):
        """处理400错误"""
        return jsonify({'error': '请求错误'}), 400
