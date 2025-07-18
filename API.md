# Image Uploader API 文档

## 概述

Image Uploader 是一个基于 Flask 的图片上传服务，支持图片压缩、MD5 哈希计算和 Cloudflare R2 存储。

- **基础 URL**: `http://localhost:5005`
- **版本**: v1.0
- **支持格式**: PNG, JPG, JPEG, GIF, WEBP
- **最大文件大小**: 根据服务器配置

## 端点列表

### 1. 主页面

**GET** `/`

获取上传界面的HTML页面。

#### 响应

- **Content-Type**: `text/html`
- **状态码**: 200

返回包含文件上传表单的HTML页面，支持：

- 拖拽上传
- 点击选择文件
- 粘贴上传（Ctrl+V/Cmd+V）

---

### 2. 图片上传

**POST** `/upload`

上传图片文件到云存储服务。

#### 请求格式

- **Content-Type**: `multipart/form-data`

#### 请求参数

| 参数名 | 类型 | 必需 | 描述 |
|--------|------|------|------|
| `file` | File | 是 | 要上传的图片文件 |
| `compress` | String | 否 | 是否压缩图片，值为 "true" 或 "false"，默认 "false" |
| `quality` | Integer | 否 | 压缩质量，范围 1-100，默认 80 |

#### 支持的文件格式

- PNG
- JPG/JPEG  
- GIF
- WEBP

#### 请求示例

```bash
# 基础上传
curl -X POST http://localhost:5005/upload \
  -F "file=@/path/to/image.jpg"

# 带压缩的上传
curl -X POST http://localhost:5005/upload \
  -F "file=@/path/to/image.jpg" \
  -F "compress=true" \
  -F "quality=60"
```

#### 响应格式

**成功响应 (200)**

```json
{
  "success": true,
  "original_size_mb": 2.45,
  "final_size_mb": 0.98,
  "md5_hash": "d41d8cd98f00b204e9800998ecf8427e",
  "storage_path": "2024/01/15/d41d8cd98f00b204e9800998ecf8427e.jpg",
  "image_url": "https://static.k1r.in/2024/01/15/d41d8cd98f00b204e9800998ecf8427e.jpg",
  "compressed": true,
  "compression_quality": 60
}
```

**响应字段说明**

| 字段名 | 类型 | 描述 |
|--------|------|------|
| `success` | Boolean | 操作是否成功 |
| `original_size_mb` | Float | 原始文件大小（MB） |
| `final_size_mb` | Float | 最终文件大小（MB） |
| `md5_hash` | String | 文件的MD5哈希值 |
| `storage_path` | String | 在存储服务中的路径 |
| `image_url` | String | 图片的完整访问URL |
| `compressed` | Boolean | 是否进行了压缩 |
| `compression_quality` | Integer/Null | 压缩质量（如果未压缩则为null） |

## 错误处理

### 错误响应格式

所有错误响应都遵循以下格式：

```json
{
  "error": "错误描述信息"
}
```

### 常见错误码

| 状态码 | 错误类型 | 描述 |
|--------|----------|------|
| 400 | Bad Request | 请求参数错误 |
| 500 | Internal Server Error | 服务器内部错误 |

### 具体错误情况

#### 400 错误

**没有选择文件**

```json
{
  "error": "没有选择文件"
}
```

**不支持的文件类型**

```json
{
  "error": "不支持的文件类型"
}
```

#### 500 错误

**图片压缩失败**

```json
{
  "error": "图片压缩失败: [具体错误信息]"
}
```

**云存储上传失败**

```json
{
  "error": "上传到云存储失败，请检查配置"
}
```

**服务器内部错误**

```json
{
  "error": "服务器内部错误: [具体错误信息]"
}
```

## 功能特性

### 1. 图片压缩

- 支持JPEG和PNG格式压缩
- 质量范围：1-100
- 自动处理透明度（PNG转JPEG时添加白色背景）
- 保持图片原始尺寸比例

### 2. MD5去重

- 为每个文件计算MD5哈希值
- 使用MD5作为文件名，避免重复上传
- 确保相同文件只存储一份

### 3. 智能存储路径

存储路径格式：`YYYY/MM/DD/MD5_HASH.EXTENSION`

示例：`2024/01/15/d41d8cd98f00b204e9800998ecf8427e.jpg`

### 4. 自定义域名

- 支持自定义域名访问
- 当前配置域名：`static.k1r.in`
- 生成的URL格式：`https://static.k1r.in/存储路径`

## 环境配置

### 必需的环境变量

| 变量名 | 描述 | 示例 |
|--------|------|------|
| `R2_ENDPOINT` | Cloudflare R2端点 | `https://xxx.r2.cloudflarestorage.com` |
| `R2_ACCESS_KEY_ID` | R2访问密钥ID | `xxx` |
| `R2_SECRET_ACCESS_KEY` | R2密钥 | `xxx` |
| `R2_BUCKET_NAME` | R2存储桶名称 | `my-bucket` |

### 配置文件

创建 `.env` 文件：

```env
R2_ENDPOINT=https://xxx.r2.cloudflarestorage.com
R2_ACCESS_KEY_ID=your_access_key_id
R2_SECRET_ACCESS_KEY=your_secret_access_key
R2_BUCKET_NAME=your_bucket_name
```

## 使用示例

### JavaScript 前端集成

```javascript
// 文件上传
async function uploadImage(file, compress = false, quality = 80) {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('compress', compress.toString());
    formData.append('quality', quality.toString());
    
    try {
        const response = await fetch('/upload', {
            method: 'POST',
            body: formData
        });
        
        const result = await response.json();
        
        if (result.success) {
            console.log('上传成功:', result.image_url);
            return result;
        } else {
            console.error('上传失败:', result.error);
            throw new Error(result.error);
        }
    } catch (error) {
        console.error('请求失败:', error);
        throw error;
    }
}

// 使用示例
const fileInput = document.getElementById('fileInput');
fileInput.addEventListener('change', async (event) => {
    const file = event.target.files[0];
    if (file) {
        try {
            const result = await uploadImage(file, true, 70);
            document.getElementById('result').src = result.image_url;
        } catch (error) {
            alert('上传失败: ' + error.message);
        }
    }
});
```

### Python 客户端示例

```python
import requests

def upload_image(file_path, compress=False, quality=80):
    """上传图片到服务器"""
    url = "http://localhost:5005/upload"
    
    with open(file_path, 'rb') as f:
        files = {'file': f}
        data = {
            'compress': str(compress).lower(),
            'quality': str(quality)
        }
        
        response = requests.post(url, files=files, data=data)
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                return result
            else:
                raise Exception(result.get('error', '未知错误'))
        else:
            response.raise_for_status()

# 使用示例
try:
    result = upload_image('/path/to/image.jpg', compress=True, quality=70)
    print(f"上传成功: {result['image_url']}")
    print(f"文件大小: {result['original_size_mb']} MB -> {result['final_size_mb']} MB")
except Exception as e:
    print(f"上传失败: {e}")
```

## 安全说明

1. **文件类型验证**: 只允许指定的图片格式
2. **文件名安全**: 使用 `secure_filename()` 处理文件名
3. **内存处理**: 文件在内存中处理，不存储在本地磁盘
4. **环境变量**: 敏感配置通过环境变量管理
5. **错误处理**: 完善的异常捕获和错误信息返回

## 性能说明

1. **内存优化**: 文件完全在内存中处理，避免磁盘I/O
2. **压缩效率**: 使用PIL库进行高效图片压缩
3. **去重机制**: MD5哈希避免重复文件上传
4. **CDN加速**: 通过自定义域名支持CDN加速访问

## 限制说明

1. **文件大小**: 受Flask和服务器配置限制
2. **并发处理**: 单个Flask进程的并发能力有限
3. **内存使用**: 大文件会占用较多内存
4. **网络依赖**: 需要稳定的网络连接到Cloudflare R2

## 故障排除

### 常见问题

1. **上传失败**: 检查网络连接和R2配置
2. **压缩错误**: 确认图片文件完整性
3. **权限错误**: 验证R2访问密钥权限
4. **域名无法访问**: 检查域名DNS配置

### 调试建议

1. 查看服务器日志获取详细错误信息
2. 验证环境变量配置
3. 测试R2连接和权限
4. 检查文件格式和大小

---

**最后更新**: 2025年07月18日  
**API版本**: v1.0  
**文档版本**: 1.0
