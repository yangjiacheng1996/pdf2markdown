// 全局变量
let currentFiles = [];
let conversionQueue = [];
let isConverting = false;
let results = [];

// DOM 元素
const serverUrlInput = document.getElementById('serverUrl');
const testConnectionBtn = document.getElementById('testConnection');
const forceOcrSelect = document.getElementById('forceOcr');
const outputFormatSelect = document.getElementById('outputFormat');
const dropZone = document.getElementById('dropZone');
const fileInput = document.getElementById('fileInput');
const fileList = document.getElementById('fileList');
const progressSection = document.getElementById('progressSection');
const progressFill = document.getElementById('progressFill');
const progressText = document.getElementById('progressText');
const logContent = document.getElementById('logContent');
const resultsList = document.getElementById('resultsList');
const noResults = document.getElementById('noResults');
const modal = document.getElementById('modal');
const modalTitle = document.getElementById('modalTitle');
const modalMessage = document.getElementById('modalMessage');
const modalConfirm = document.getElementById('modalConfirm');
const modalCancel = document.getElementById('modalCancel');
const closeModal = document.querySelector('.close');

// 初始化
document.addEventListener('DOMContentLoaded', function() {
    initEventListeners();
    loadResults();
});

// 初始化事件监听器
function initEventListeners() {
    // 服务器连接测试
    testConnectionBtn.addEventListener('click', testServerConnection);
    
    // 文件拖拽事件
    dropZone.addEventListener('dragover', handleDragOver);
    dropZone.addEventListener('dragleave', handleDragLeave);
    dropZone.addEventListener('drop', handleDrop);
    
    // 文件选择事件
    fileInput.addEventListener('change', handleFileSelect);
    
    // 模态对话框事件
    closeModal.addEventListener('click', hideModal);
    modalConfirm.addEventListener('click', handleModalConfirm);
    modalCancel.addEventListener('click', hideModal);
    modal.addEventListener('click', function(e) {
        if (e.target === modal) hideModal();
    });
}

// 测试服务器连接
async function testServerConnection() {
    const serverUrl = serverUrlInput.value.trim();
    if (!serverUrl) {
        showModal('错误', '请输入服务器地址');
        return;
    }
    
    const testBtn = testConnectionBtn;
    const originalText = testBtn.textContent;
    testBtn.innerHTML = '<span class="spinner"></span>测试中...';
    testBtn.disabled = true;
    
    try {
        const response = await fetch('/api/server/test', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ server_url: serverUrl })
        });
        
        const result = await response.json();
        
        if (result.success) {
            showModal('成功', '服务器连接成功！');
        } else {
            throw new Error(result.error);
        }
    } catch (error) {
        showModal('错误', `无法连接到服务器: ${error.message}`);
    } finally {
        testBtn.textContent = originalText;
        testBtn.disabled = false;
    }
}

// 文件拖拽处理
function handleDragOver(e) {
    e.preventDefault();
    dropZone.classList.add('drag-over');
}

function handleDragLeave(e) {
    e.preventDefault();
    dropZone.classList.remove('drag-over');
}

function handleDrop(e) {
    e.preventDefault();
    dropZone.classList.remove('drag-over');
    
    const files = Array.from(e.dataTransfer.files).filter(file => 
        file.type === 'application/pdf' || file.name.toLowerCase().endsWith('.pdf')
    );
    
    if (files.length > 0) {
        addFilesToQueue(files);
    } else {
        showModal('错误', '请拖拽PDF文件');
    }
}

// 文件选择处理
function handleFileSelect(e) {
    const files = Array.from(e.target.files).filter(file => 
        file.type === 'application/pdf' || file.name.toLowerCase().endsWith('.pdf')
    );
    
    if (files.length > 0) {
        addFilesToQueue(files);
    }
    
    // 重置文件输入，允许重复选择相同文件
    e.target.value = '';
}

// 添加文件到队列
function addFilesToQueue(files) {
    files.forEach(file => {
        // 检查是否已存在同名文件
        if (currentFiles.some(f => f.name === file.name)) {
            showModal('提示', `文件 "${file.name}" 已在队列中`);
            return;
        }
        
        // 检查是否已有同名结果
        const zipName = `${file.name.replace('.pdf', '')}.zip`;
        if (results.some(result => result.name === zipName)) {
            showModal('提示', `文件 "${file.name}" 已转换过，请先删除已有结果再重新转换`);
            return;
        }
        
        currentFiles.push(file);
        conversionQueue.push(file);
    });
    
    updateFileList();
    
    // 如果没有正在转换，开始转换
    if (!isConverting && conversionQueue.length > 0) {
        startConversion();
    }
}

// 更新文件列表显示
function updateFileList() {
    fileList.innerHTML = '';
    
    currentFiles.forEach((file, index) => {
        const fileItem = document.createElement('div');
        fileItem.className = 'file-item';
        fileItem.innerHTML = `
            <div class="file-info">
                <span class="file-icon">📄</span>
                <span class="file-name">${file.name}</span>
                <span class="file-size">(${formatFileSize(file.size)})</span>
            </div>
            <div class="file-actions">
                <button class="btn btn-danger" onclick="removeFile(${index})">移除</button>
            </div>
        `;
        fileList.appendChild(fileItem);
    });
}

// 移除文件
function removeFile(index) {
    const file = currentFiles[index];
    currentFiles.splice(index, 1);
    
    // 从队列中移除
    const queueIndex = conversionQueue.findIndex(f => f.name === file.name);
    if (queueIndex !== -1) {
        conversionQueue.splice(queueIndex, 1);
    }
    
    updateFileList();
}

// 开始转换
async function startConversion() {
    if (isConverting || conversionQueue.length === 0) return;
    
    isConverting = true;
    progressSection.style.display = 'block';
    updateProgress(0, '开始转换...');
    
    const totalFiles = conversionQueue.length;
    let processedFiles = 0;
    
    for (const file of conversionQueue) {
        const fileIndex = conversionQueue.indexOf(file);
        const progress = (processedFiles / totalFiles) * 100;
        updateProgress(progress, `正在转换: ${file.name} (${processedFiles + 1}/${totalFiles})`);
        
        addLog(`开始转换文件: ${file.name}`, 'info');
        
        try {
            await convertFile(file);
            addLog(`✅ 文件转换成功: ${file.name}`, 'info');
        } catch (error) {
            addLog(`❌ 文件转换失败: ${file.name} - ${error.message}`, 'error');
        }
        
        processedFiles++;
        
        // 从队列中移除已处理文件
        const index = conversionQueue.indexOf(file);
        if (index !== -1) {
            conversionQueue.splice(index, 1);
        }
        
        // 从当前文件列表中移除
        const currentIndex = currentFiles.findIndex(f => f.name === file.name);
        if (currentIndex !== -1) {
            currentFiles.splice(currentIndex, 1);
        }
    }
    
    updateProgress(100, '所有文件转换完成！');
    updateFileList();
    isConverting = false;
    
    // 3秒后隐藏进度区域
    setTimeout(() => {
        progressSection.style.display = 'none';
    }, 3000);
}

// 转换单个文件
async function convertFile(file) {
    const serverUrl = serverUrlInput.value.trim();
    const forceOcr = forceOcrSelect.value;
    const outputFormat = outputFormatSelect.value;
    
    const formData = new FormData();
    formData.append('file', file);
    formData.append('server_url', serverUrl);
    formData.append('force_ocr', forceOcr);
    formData.append('output_format', outputFormat);
    
    addLog(`正在上传文件到后端服务器...`, 'info');
    
    const response = await fetch('/api/convert', {
        method: 'POST',
        body: formData
    });
    
    const result = await response.json();
    
    if (!result.success) {
        throw new Error(result.error);
    }
    
    addLog(`✅ ${result.message}`, 'info');
    
    // 重新加载结果列表
    loadResults();
}

// 更新进度条
function updateProgress(percent, text) {
    progressFill.style.width = `${percent}%`;
    progressText.textContent = text;
}

// 添加日志
function addLog(message, type = 'info') {
    const timestamp = new Date().toLocaleTimeString();
    const logEntry = document.createElement('div');
    logEntry.className = `log-entry ${type}`;
    logEntry.textContent = `[${timestamp}] ${message}`;
    logContent.appendChild(logEntry);
    logContent.scrollTop = logContent.scrollHeight;
}

// 加载结果列表
async function loadResults() {
    try {
        const response = await fetch('/api/results');
        const result = await response.json();
        
        if (result.success) {
            results = result.results;
            updateResultsList();
        } else {
            console.error('获取结果列表失败:', result.error);
        }
    } catch (error) {
        console.error('加载结果列表失败:', error);
    }
}

// 更新结果列表显示
function updateResultsList() {
    resultsList.innerHTML = '';
    
    if (results.length === 0) {
        noResults.style.display = 'block';
        return;
    }
    
    noResults.style.display = 'none';
    
    results.forEach((result, index) => {
        const resultItem = document.createElement('div');
        resultItem.className = 'result-item';
        resultItem.innerHTML = `
            <div class="result-header">
                <span class="result-name">${result.name}</span>
                <span class="result-size">${result.size}</span>
            </div>
            <div class="result-date">创建时间: ${result.date}</div>
            <div class="result-actions">
                <button class="btn btn-success" onclick="downloadResult('${result.name}')">下载</button>
                <button class="btn btn-danger" onclick="deleteResult('${result.name}')">删除</button>
            </div>
        `;
        resultsList.appendChild(resultItem);
    });
}

// 下载结果文件
async function downloadResult(fileName) {
    try {
        addLog(`开始下载: ${fileName}`, 'info');
        
        const response = await fetch(`/api/results/${fileName}`);
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || '下载失败');
        }
        
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = fileName;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        window.URL.revokeObjectURL(url);
        
        addLog(`✅ 下载完成: ${fileName}`, 'info');
    } catch (error) {
        addLog(`❌ 下载失败: ${fileName} - ${error.message}`, 'error');
        showModal('错误', `下载文件失败: ${error.message}`);
    }
}

// 删除结果文件
async function deleteResult(fileName) {
    showModal('确认删除', `确定要删除文件 "${fileName}" 吗？`, async () => {
        try {
            const response = await fetch(`/api/results/${fileName}`, {
                method: 'DELETE'
            });
            
            const result = await response.json();
            
            if (result.success) {
                addLog(`🗑️ 已删除文件: ${fileName}`, 'info');
                showModal('成功', `文件 ${fileName} 已删除`);
                loadResults(); // 重新加载结果列表
            } else {
                throw new Error(result.error);
            }
        } catch (error) {
            addLog(`❌ 删除文件失败: ${fileName} - ${error.message}`, 'error');
            showModal('错误', `删除文件失败: ${error.message}`);
        }
    }, true);
}

// 模态对话框函数
function showModal(title, message, onConfirm = null, showCancel = false) {
    modalTitle.textContent = title;
    modalMessage.textContent = message;
    modal.style.display = 'flex';
    
    if (onConfirm) {
        modalConfirm.onclick = function() {
            onConfirm();
            hideModal();
        };
    } else {
        modalConfirm.onclick = hideModal;
    }
    
    modalCancel.style.display = showCancel ? 'inline-block' : 'none';
}

function hideModal() {
    modal.style.display = 'none';
}

function handleModalConfirm() {
    // 在showModal中设置具体的确认处理
    hideModal();
}

// 工具函数
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

// 导出函数到全局作用域
window.removeFile = removeFile;
window.downloadResult = downloadResult;
window.deleteResult = deleteResult;