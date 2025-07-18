// 图片上传器主要JavaScript逻辑

let selectedFile = null;
let originalFileData = null;

// DOM元素引用
const uploadArea = document.getElementById('uploadArea');
const fileInput = document.getElementById('fileInput');
const fileInfo = document.getElementById('fileInfo');
const compressionOptions = document.getElementById('compressionOptions');
const uploadBtn = document.getElementById('uploadBtn');
const resetBtn = document.getElementById('resetBtn');
const result = document.getElementById('result');
const loading = document.getElementById('loading');

// 初始化事件监听器
function initializeEventListeners() {
    // 文件拖拽处理
    uploadArea.addEventListener('dragover', handleDragOver);
    uploadArea.addEventListener('dragleave', handleDragLeave);
    uploadArea.addEventListener('drop', handleDrop);

    // 文件选择处理 - 由于文件输入框覆盖整个uploadArea，点击任何地方都会触发文件选择
    fileInput.addEventListener('change', handleFileInputChange);

    // 粘贴图片处理
    document.addEventListener('paste', handlePaste);

    // 键盘快捷键提示
    document.addEventListener('keydown', handleKeyDown);

    // 压缩控制
    document.getElementById('enableCompression').addEventListener('change', toggleCompressionControls);
    document.getElementById('qualitySlider').addEventListener('input', handleQualityChange);

    // 按钮事件
    uploadBtn.addEventListener('click', uploadImage);
    resetBtn.addEventListener('click', resetForm);
}

// 拖拽事件处理
function handleDragOver(e) {
    e.preventDefault();
    uploadArea.classList.add('dragover');
}

function handleDragLeave() {
    uploadArea.classList.remove('dragover');
}

function handleDrop(e) {
    e.preventDefault();
    uploadArea.classList.remove('dragover');
    const files = e.dataTransfer.files;
    if (files.length > 0) {
        handleFileSelect(files[0]);
    }
}

function handleFileInputChange(e) {
    console.log('文件输入变化事件触发'); // 调试日志

    if (e.target.files.length > 0) {
        const file = e.target.files[0];
        console.log('选择的文件:', file.name, file.size, file.type); // 调试日志
        handleFileSelect(file);
    } else {
        console.log('没有选择文件'); // 调试日志
    }
}

// 粘贴事件处理
function handlePaste(e) {
    e.preventDefault();

    const items = e.clipboardData.items;
    for (let i = 0; i < items.length; i++) {
        const item = items[i];

        // 检查是否为图片
        if (item.type.indexOf('image') !== -1) {
            const file = item.getAsFile();
            if (file) {
                // 为粘贴的文件生成一个名称
                const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
                const extension = file.type.split('/')[1] || 'png';
                const fileName = `screenshot-${timestamp}.${extension}`;

                // 创建一个新的File对象，带有适当的名称
                const namedFile = new File([file], fileName, { type: file.type });

                // 显示粘贴成功提示
                showPasteSuccess();

                // 处理文件
                handleFileSelect(namedFile);
                return;
            }
        }
    }

    // 如果没有找到图片，显示提示
    if (items.length > 0) {
        showError('剪贴板中没有找到图片。请复制图片后再试。');
    }
}

// 键盘事件处理
function handleKeyDown(e) {
    if ((e.ctrlKey || e.metaKey) && e.key === 'v') {
        uploadArea.classList.add('paste-ready');
        setTimeout(() => {
            uploadArea.classList.remove('paste-ready');
        }, 500);
    }
}

// 质量滑块变化处理
function handleQualityChange(e) {
    document.getElementById('qualityValue').textContent = e.target.value;
    if (originalFileData) {
        estimateCompressedSize();
    }
}

// 处理文件选择
function handleFileSelect(file) {
    selectedFile = file;

    // 验证文件类型
    const allowedTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'image/webp'];
    if (!allowedTypes.includes(file.type)) {
        showError('不支持的文件类型。请选择 JPEG、PNG、GIF 或 WebP 格式的图片。');
        return;
    }

    // 验证文件大小（最大16MB）
    if (file.size > 16 * 1024 * 1024) {
        showError('文件太大，最大支持16MB。');
        return;
    }

    const fileSizeMB = (file.size / (1024 * 1024)).toFixed(2);

    // 显示文件信息
    document.getElementById('fileName').textContent = file.name;
    document.getElementById('fileSize').textContent = fileSizeMB;

    // 判断是否需要压缩
    const needsCompression = parseFloat(fileSizeMB) > 2;
    const compressionSuggestion = needsCompression ? '建议压缩（文件大于2MB）' : '可选压缩';
    document.getElementById('compressionSuggestion').textContent = compressionSuggestion;

    // 如果文件大于2MB，自动启用压缩并设置为80%
    const enableCompressionCheckbox = document.getElementById('enableCompression');
    const qualitySlider = document.getElementById('qualitySlider');
    if (needsCompression) {
        enableCompressionCheckbox.checked = true;
        qualitySlider.value = 80;
        document.getElementById('qualityValue').textContent = '80';
        toggleCompressionControls();
    }

    fileInfo.style.display = 'block';
    compressionOptions.style.display = 'block';
    uploadBtn.disabled = false;

    // 读取文件数据用于预估
    const reader = new FileReader();
    reader.onload = (e) => {
        originalFileData = e.target.result;
        if (enableCompressionCheckbox.checked) {
            estimateCompressedSize();
        }
    };
    reader.readAsArrayBuffer(file);
}

// 压缩控制切换
function toggleCompressionControls() {
    const checkbox = document.getElementById('enableCompression');
    const controls = document.getElementById('compressionControls');
    controls.style.display = checkbox.checked ? 'block' : 'none';

    if (checkbox.checked && originalFileData) {
        estimateCompressedSize();
    }
}

// 预估压缩后大小
function estimateCompressedSize() {
    const quality = parseInt(document.getElementById('qualitySlider').value);
    const originalSizeMB = selectedFile.size / (1024 * 1024);

    // 简单的压缩比例估算（实际效果可能有差异）
    let compressionRatio;
    if (quality >= 90) compressionRatio = 0.8;
    else if (quality >= 80) compressionRatio = 0.6;
    else if (quality >= 70) compressionRatio = 0.4;
    else if (quality >= 60) compressionRatio = 0.3;
    else if (quality >= 50) compressionRatio = 0.25;
    else compressionRatio = 0.2;

    const estimatedSizeMB = (originalSizeMB * compressionRatio).toFixed(2);
    document.getElementById('estimatedSize').textContent = estimatedSizeMB + ' MB';
}

// 上传图片
async function uploadImage() {
    if (!selectedFile) return;

    showLoading();
    hideResult();

    const formData = new FormData();
    formData.append('file', selectedFile);
    formData.append('compress', document.getElementById('enableCompression').checked);
    formData.append('quality', document.getElementById('qualitySlider').value);

    try {
        const response = await fetch('/upload', {
            method: 'POST',
            body: formData
        });

        const data = await response.json();

        if (response.ok) {
            showSuccess(data);
        } else {
            showError(data.error || '上传失败');
        }
    } catch (error) {
        showError('网络错误：' + error.message);
    } finally {
        hideLoading();
    }
}

// 重置表单
function resetForm() {
    selectedFile = null;
    originalFileData = null;
    fileInput.value = '';
    fileInfo.style.display = 'none';
    compressionOptions.style.display = 'none';
    uploadBtn.disabled = true;
    document.getElementById('enableCompression').checked = false;
    document.getElementById('compressionControls').style.display = 'none';
    hideResult();
    hideLoading();
}

// 显示成功结果
function showSuccess(data) {
    const html = `
        <div class="success">
            <h3>上传成功！</h3>
            <p><strong>文件信息:</strong></p>
            <ul>
                <li>原始大小: ${data.original_size_mb} MB</li>
                <li>最终大小: ${data.final_size_mb} MB</li>
                <li>MD5哈希: ${data.md5_hash}</li>
                <li>存储路径: ${data.storage_path}</li>
            </ul>
            <p><strong>图片URL:</strong></p>
            <div class="url-box" id="imageUrl">${data.image_url}</div>
            <p class="copy-hint">💡 请手动选择并复制上面的链接</p>
        </div>
    `;
    result.innerHTML = html;
    result.style.display = 'block';
}

// 显示错误信息
function showError(message) {
    result.innerHTML = `<div class="error"><h3>错误</h3><p>${message}</p></div>`;
    result.style.display = 'block';
}

// 显示粘贴成功提示
function showPasteSuccess() {
    const pasteHint = document.querySelector('.paste-hint');
    const originalText = pasteHint.textContent;
    pasteHint.textContent = '✅ 图片粘贴成功！正在处理...';
    pasteHint.style.color = '#28a745';

    setTimeout(() => {
        pasteHint.textContent = originalText;
        pasteHint.style.color = '#666';
    }, 2000);
}

// 隐藏结果
function hideResult() {
    result.style.display = 'none';
}

// 显示加载状态
function showLoading() {
    loading.style.display = 'block';
}

// 隐藏加载状态
function hideLoading() {
    loading.style.display = 'none';
}

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', initializeEventListeners);
