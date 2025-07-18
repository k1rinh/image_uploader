# 部署指南

## 本地开发环境设置

### 1. 安装依赖

```bash
# 使用uv（推荐）
uv sync

# 或者使用pip
pip install flask pillow boto3 python-dotenv werkzeug
```

### 2. 配置环境变量

创建`.env`文件：

```bash
cp .env.example .env
```

编辑`.env`文件，填入您的Cloudflare R2配置：

```env
# Cloudflare R2配置
R2_ENDPOINT=https://your-account-id.r2.cloudflarestorage.com
R2_ACCESS_KEY_ID=your_access_key_id
R2_SECRET_ACCESS_KEY=your_secret_access_key
R2_BUCKET_NAME=your_bucket_name

# Flask配置
FLASK_ENV=development
FLASK_DEBUG=True
```

### 3. 获取Cloudflare R2配置

#### 创建R2存储桶

1. 登录 [Cloudflare Dashboard](https://dash.cloudflare.com/)
2. 选择您的账户
3. 导航到 R2 Object Storage
4. 点击 "Create bucket"
5. 输入存储桶名称
6. 选择区域（推荐选择离用户最近的区域）
7. 点击 "Create bucket"

#### 获取API凭证

1. 在R2页面，点击右侧的 "Manage R2 API tokens"
2. 点击 "Create API token"
3. 配置权限：
   - **Token name**: 输入描述性名称（如：image-uploader-token）
   - **Permissions**: 选择 "Object Read & Write"
   - **Resources**: 选择 "Apply to specific buckets only"，然后选择您创建的存储桶
4. 点击 "Create API token"
5. 复制显示的凭证信息：
   - Access Key ID
   - Secret Access Key
   - Token value (这个是给CLI使用的，Web应用不需要)

#### 获取账户ID和端点

1. 在R2概览页面，您可以找到：
   - **Account ID**: 在页面右侧显示
   - **Endpoint**: 格式为 `https://<account-id>.r2.cloudflarestorage.com`

### 4. 测试配置

运行测试脚本验证核心功能：

```bash
python test_core.py
```

### 5. 启动应用

```bash
python main.py
```

应用将在 `http://localhost:5000` 启动。

## 生产环境部署

### 选项1：传统VPS部署

#### 1. 准备服务器

```bash
# 更新系统
sudo apt update && sudo apt upgrade -y

# 安装Python和依赖
sudo apt install python3 python3-pip python3-venv nginx -y

# 创建应用目录
sudo mkdir -p /var/www/image-uploader
cd /var/www/image-uploader
```

#### 2. 部署应用

```bash
# 克隆代码
git clone <your-repo-url> .

# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 或者如果使用pyproject.toml
pip install -e .
```

#### 3. 配置环境变量

```bash
# 创建生产环境配置
sudo nano .env

# 添加内容（使用您的实际配置）
R2_ENDPOINT=https://your-account-id.r2.cloudflarestorage.com
R2_ACCESS_KEY_ID=your_access_key_id
R2_SECRET_ACCESS_KEY=your_secret_access_key
R2_BUCKET_NAME=your_bucket_name
FLASK_ENV=production
```

#### 4. 配置Gunicorn

创建Gunicorn配置文件：

```bash
sudo nano gunicorn.conf.py
```

内容：

```python
bind = "127.0.0.1:5000"
workers = 2
worker_class = "sync"
timeout = 120
keepalive = 5
max_requests = 1000
max_requests_jitter = 100
```

#### 5. 创建systemd服务

```bash
sudo nano /etc/systemd/system/image-uploader.service
```

内容：

```ini
[Unit]
Description=Image Uploader Flask App
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/image-uploader
Environment="PATH=/var/www/image-uploader/venv/bin"
ExecStart=/var/www/image-uploader/venv/bin/gunicorn -c gunicorn.conf.py main:app
Restart=always

[Install]
WantedBy=multi-user.target
```

启动服务：

```bash
sudo systemctl daemon-reload
sudo systemctl enable image-uploader
sudo systemctl start image-uploader
sudo systemctl status image-uploader
```

#### 6. 配置Nginx

```bash
sudo nano /etc/nginx/sites-available/image-uploader
```

内容：

```nginx
server {
    listen 80;
    server_name your-domain.com;

    client_max_body_size 20M;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 120;
        proxy_connect_timeout 120;
        proxy_send_timeout 120;
    }
}
```

启用站点：

```bash
sudo ln -s /etc/nginx/sites-available/image-uploader /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

#### 7. 配置SSL（可选但推荐）

```bash
# 安装Certbot
sudo apt install certbot python3-certbot-nginx -y

# 获取SSL证书
sudo certbot --nginx -d your-domain.com

# 设置自动续期
sudo crontab -e
# 添加: 0 12 * * * /usr/bin/certbot renew --quiet
```

### 选项2：Docker部署

#### 1. 创建Dockerfile

```dockerfile
FROM python:3.12-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY pyproject.toml .

# 安装Python依赖
RUN pip install -e .

# 复制应用代码
COPY . .

# 创建非root用户
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 5000

CMD ["python", "main.py"]
```

#### 2. 创建docker-compose.yml

```yaml
version: '3.8'

services:
  image-uploader:
    build: .
    ports:
      - "5000:5000"
    environment:
      - R2_ENDPOINT=${R2_ENDPOINT}
      - R2_ACCESS_KEY_ID=${R2_ACCESS_KEY_ID}
      - R2_SECRET_ACCESS_KEY=${R2_SECRET_ACCESS_KEY}
      - R2_BUCKET_NAME=${R2_BUCKET_NAME}
      - FLASK_ENV=production
    volumes:
      - ./.env:/app/.env:ro
    restart: unless-stopped
```

#### 3. 部署

```bash
# 构建并启动
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止
docker-compose down
```

### 选项3：Cloudflare Workers部署

如果您想将应用部署为Cloudflare Workers（需要修改代码以适配Workers环境）：

#### 1. 安装Wrangler CLI

```bash
npm install -g wrangler
```

#### 2. 登录Cloudflare

```bash
wrangler login
```

#### 3. 配置wrangler.toml

```toml
name = "image-uploader"
compatibility_date = "2024-07-01"

[[r2_buckets]]
binding = "IMAGE_BUCKET"
bucket_name = "your-bucket-name"

[vars]
CUSTOM_DOMAIN = "static.k1r.in"
```

#### 4. 部署

```bash
wrangler deploy
```

## 监控和维护

### 日志监控

```bash
# 查看应用日志
sudo journalctl -u image-uploader -f

# 查看Nginx日志
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

### 性能监控

建议设置以下监控指标：

1. **应用响应时间**
2. **上传成功率**
3. **R2存储使用量**
4. **服务器资源使用率**

### 备份策略

1. **代码备份**: 使用Git版本控制
2. **配置备份**: 定期备份`.env`文件
3. **R2数据**: Cloudflare R2自带高可用性，但建议定期检查

### 安全建议

1. **定期更新依赖包**
2. **设置防火墙规则**
3. **使用强密码和密钥**
4. **定期轮换API密钥**
5. **监控异常访问**

## 故障排除

### 常见问题

1. **R2连接失败**
   - 检查网络连接
   - 验证API凭证
   - 确认存储桶名称正确

2. **文件上传失败**
   - 检查文件大小限制
   - 验证文件类型
   - 查看应用日志

3. **服务无法启动**
   - 检查端口占用
   - 验证环境变量
   - 查看系统日志

### 日志分析

应用会记录详细的操作日志，包括：

- 文件上传状态
- 压缩处理结果
- R2上传结果
- 错误详情和堆栈跟踪

定期分析日志可以帮助发现潜在问题并优化性能。
