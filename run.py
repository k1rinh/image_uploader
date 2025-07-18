#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
图片上传器主入口文件
"""

from dotenv import load_dotenv

def main():
    """主函数"""
    try:
        # 首先加载环境变量
        load_dotenv()
        
        # 然后导入其他模块
        from app import create_app
        from app.config import validate_config
        
        # 验证配置
        validate_config()
        
        # 创建应用
        app = create_app()
        
        # 启动应用
        print("正在启动图片上传器...")
        print("访问地址: http://localhost:5005")
        print("文件结构已优化，代码更加模块化！")
        
        app.run(debug=True, host='0.0.0.0', port=5005)
        
    except ValueError as e:
        print(f"配置错误: {e}")
        print("请在.env文件中设置这些变量")
        print("您可以复制 .env.example 到 .env 并填入实际配置")
        return 1
    except Exception as e:
        print(f"启动失败: {e}")
        return 1

if __name__ == '__main__':
    main()
