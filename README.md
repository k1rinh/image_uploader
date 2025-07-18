# 图片上传器 (Image Uploader)

一个基于 Flask 的图片上传 Web 应用程序，支持图片压缩、MD5 哈希计算和 Cloudflare R2 云存储。

本项目完全由 GitHub Copilot 提供代码和文档支持。

## 🎯 功能特性

- 📸 **多格式支持**: 支持 JPEG、PNG、GIF、WebP 等常见图片格式
- 🗜️ **智能压缩**: 可选图片压缩，大于 2MB 自动建议压缩
- 📊 **文件信息**: 实时显示文件大小和压缩预估
- 🔐 **MD5 哈希**: 自动计算文件 MD5 哈希值防重复
- ☁️ **云存储**: 使用 Cloudflare R2 存储，支持自定义域名
- 🎨 **友好界面**: 现代化 Web 界面，支持拖拽上传
- 📋 **粘贴上传**: 支持直接粘贴截图上传（Ctrl+V / Cmd+V）
- 🛡️ **安全验证**: 完善的文件类型和大小验证

## 📁 项目结构

```
image_uploader/
├── run.py                          # 应用程序入口文件
├── app/                            # 主应用包
│   ├── __init__.py                 # Flask 应用初始化
│   ├── config.py                   # 配置文件
│   ├── routes.py                   # 路由处理
│   ├── error_handlers.py           # 错误处理
│   ├── utils/                      # 工具模块
│   │   ├── __init__.py             # 工具包初始化
│   │   ├── image_utils.py          # 图片处理工具
│   │   └── storage_utils.py        # 云存储工具
│   ├── templates/                  # HTML 模板
│   │   └── index.html              # 主页模板
│   └── static/                     # 静态资源
│       ├── css/
│       │   └── style.css           # 样式文件
│       └── js/
│           └── main.js             # JavaScript 逻辑
├── docs/                           # 项目文档
│   ├── API.md                      # API 接口文档
│   └── DEPLOYMENT.md               # 部署指南
├── .github/                        # GitHub 配置
│   └── copilot-instructions.md     # Copilot 指令文件
├── pyproject.toml                  # 项目依赖配置
├── uv.lock                         # UV 依赖锁定文件
├── .env.example                    # 环境变量模板
├── .env                            # 环境变量配置（本地）
├── .gitignore                      # Git 忽略文件
├── .python-version                 # Python 版本指定
├── README.md                       # 项目说明
├── test_core.py                    # 核心功能测试
└── wrangler.toml                   # Cloudflare Workers 配置
```

## 🚀 快速开始

### 1. 安装依赖

```bash
# 使用 uv（推荐）
uv sync
```

### 2. 配置环境变量

```bash
cp .env.example .env
# 编辑 .env 文件，填入您的 Cloudflare R2 配置
```

### 3. 运行应用

```bash
uv run run.py
```

访问 `http://localhost:5005` 使用应用程序。

## 📋 使用方法

### Web 界面

1. 访问应用程序首页
2. **三种上传方式**：
   - 拖拽图片到上传区域
   - 点击选择文件
   - **直接粘贴图片**（Ctrl+V 或 Cmd+V）
3. 查看文件信息和压缩建议
4. 可选择启用压缩并调整质量
5. 点击"上传图片"开始处理
6. 获取最终的图片链接

### API 接口

详细的API文档请参考 [API.md](./docs/API.md)

#### 上传图片

**POST** `/upload`

**参数：**
- `file`: 图片文件（multipart/form-data）
- `compress`: 是否启用压缩（可选，true/false）
- `quality`: 压缩质量（可选，10-95）

## 🔧 模块说明

### 核心模块

- **`app/__init__.py`**: Flask 应用程序工厂，负责创建和配置应用
- **`app/config.py`**: 集中管理配置信息和环境变量
- **`app/routes.py`**: 定义所有的路由处理函数
- **`app/error_handlers.py`**: 统一的错误处理机制

### 工具模块

- **`app/utils/image_utils.py`**: 图片处理相关功能
  - 文件验证
  - 图片压缩
  - MD5 计算
  - 文件大小计算

- **`app/utils/storage_utils.py`**: 云存储相关功能
  - R2 客户端创建
  - 文件上传
  - 路径生成
  - URL生成

### 前端资源

- **`app/templates/index.html`**: 主页面 HTML 模板
- **`app/static/css/style.css`**: 所有样式定义
- **`app/static/js/main.js`**: 前端交互逻辑

## ⚙️ 配置说明

### 环境变量

| 变量名 | 说明 | 必需 |
|--------|------|------|
| `R2_ENDPOINT` | R2 存储端点 URL | ✅ |
| `R2_ACCESS_KEY_ID` | R2 访问密钥 ID | ✅ |
| `R2_SECRET_ACCESS_KEY` | R2 密钥 | ✅ |
| `R2_BUCKET_NAME` | R2 存储桶名称 | ✅ |
| `SECRET_KEY` | Flask 密钥（生产环境） | ❌ |

### 应用配置

在 `app/config.py` 中可以修改：

- 支持的文件类型
- 自定义域名
- 文件大小限制

## 🆕 新功能：粘贴上传

现在支持直接粘贴图片上传！特别适合截图后快速上传：

1. **截图或复制图片**到剪贴板
2. **在上传页面按 Ctrl+V**（Windows/Linux）或 **Cmd+V**（Mac）
3. 图片会自动开始处理，文件名格式为 `screenshot-时间戳.扩展名`

### 粘贴功能特点

- ✅ 支持所有主流浏览器
- ✅ 自动生成文件名
- ✅ 实时反馈粘贴状态
- ✅ 键盘快捷键高亮提示

## 🧪 测试

```bash
# 运行核心功能测试
python test_core.py
```

## 📦 部署

详细的部署指南请参考 [DEPLOYMENT.md](./docs/DEPLOYMENT.md)

支持多种部署方式：

- 传统VPS部署
- Docker容器部署
- Cloudflare Workers部署

## 🎨 技术栈

- **后端**: Flask 3.1.1
- **图片处理**: Pillow 11.3.0
- **云存储**: boto3 1.39.8 (S3兼容)
- **前端**: 原生HTML/CSS/JavaScript
- **环境变量**: python-dotenv 1.1.1

## 📝 更新日志

### v2.0 - 结构化重构

- 🔄 **重构代码结构**：将单文件应用拆分为模块化结构
- 📋 **新增粘贴上传**：支持 Ctrl+V/Cmd+V 直接粘贴图片
- 🎨 **分离前端资源**：CSS 和 JavaScript 独立文件
- 🔧 **优化配置管理**：集中化配置和环境变量处理
- 📱 **响应式设计**：改进移动端适配

### v1.0 - 初始版本

- 基础图片上传功能
- 图片压缩和 MD5 计算
- Cloudflare R2 存储集成

## 🤝 贡献

欢迎提交 Issue 和 Pull Request 来改进这个项目！

## 📄 许可证

本项目采用 MIT 许可证。详见 LICENSE 文件。
