document.addEventListener('DOMContentLoaded', function() {
    // 获取DOM元素
    const folderForm = document.getElementById('folder-form');
    const folderPathInput = document.getElementById('folder-path');
    const roiFileInput = document.getElementById('roi-file');
    const loader = document.getElementById('loader');
    const successMessage = document.getElementById('success-message');
    const errorMessage = document.getElementById('error-message');
    const dicomTableBody = document.getElementById('dicom-table-body');
    const exportBtn = document.getElementById('export-btn');

    // 存储DICOM目录数据
    let dicomData = [];

    // 隐藏所有消息
    function hideMessages() {
        successMessage.style.display = 'none';
        errorMessage.style.display = 'none';
    }

    // 显示成功消息
    function showSuccessMessage(message) {
        successMessage.textContent = message;
        successMessage.style.display = 'block';
        setTimeout(() => {
            successMessage.style.display = 'none';
        }, 9000);
    }

    // 显示错误消息
    function showErrorMessage(message) {
        errorMessage.textContent = message;
        errorMessage.style.display = 'block';
        setTimeout(() => {
            errorMessage.style.display = 'none';
        }, 9000);
    }

    // 遍历文件夹并获取DICOM目录
    function traverseFolder(folderPath, roiFile) {
        loader.style.display = 'block';
        hideMessages();

        fetch('/traverse_folder', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                folder_path: folderPath,
                roi_file: roiFile
            })
        })
        .then(response => response.json())
        .then(data => {
            loader.style.display = 'none';
            if (data.status === 'success') {
                dicomData = data.dicom_directories;
                renderDicomTable();
                showSuccessMessage(`成功遍历文件夹，找到 ${dicomData.length} 个DICOM目录`);
            } else {
                showErrorMessage(data.message);
            }
        })
        .catch(error => {
            loader.style.display = 'none';
            showErrorMessage(`遍历文件夹失败: ${error.message}`);
        });
    }

    // 渲染DICOM目录表格
    function renderDicomTable() {
        dicomTableBody.innerHTML = '';

        if (dicomData.length === 0) {
            const row = document.createElement('tr');
            row.innerHTML = '<td colspan="4" style="text-align: center;">未找到DICOM目录</td>';
            dicomTableBody.appendChild(row);
            return;
        }

        dicomData.forEach((item, index) => {
            const row = document.createElement('tr');
            // 确定状态类
            let statusClass = 'status-pending';
            if (item.is_processing) {
                statusClass = 'status-processing';
            } else if (item.volume_result) {
                statusClass = 'status-completed';
            }
            
            row.innerHTML = `
                <td><span class="status-dot ${statusClass}" id="status-${index}"></span></td>
                <td>${item.folder_path}</td>
                <td>${item.roi_file}</td>
                <td>
                    <button class="btn calculate-btn" data-index="${index}" ${item.is_processing ? 'disabled' : ''}>计算体积</button>
                </td>
                <td id="result-${index}">${item.volume_result || '-'}</td>
            `;
            dicomTableBody.appendChild(row);
        });

        // 绑定计算体积按钮事件
        document.querySelectorAll('.calculate-btn').forEach(btn => {
            btn.addEventListener('click', function() {
                const index = parseInt(this.getAttribute('data-index'));
                calculateVolume(index);
            });
        });
    }

    // 计算体积
    function calculateVolume(index) {
        const item = dicomData[index];
        const resultCell = document.getElementById(`result-${index}`);
        const calculateBtn = document.querySelector(`.calculate-btn[data-index="${index}"]`);
        const statusDot = document.getElementById(`status-${index}`);

        // 更新状态
        item.is_processing = true;
        statusDot.className = 'status-dot status-processing';
        
        // 禁用按钮
        calculateBtn.disabled = true;
        calculateBtn.textContent = '计算中...';
        resultCell.textContent = '计算中...';

        fetch('/calculate_volume', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                folder_path: item.folder_path,
                roi_file: item.roi_file
            })
        })
        .then(response => response.json())
        .then(data => {
            // 更新状态
            item.is_processing = false;
            const statusDot = document.getElementById(`status-${index}`);
            
            // 恢复按钮状态
            calculateBtn.disabled = false;
            calculateBtn.textContent = '计算体积';

            if (data.status === 'success') {
                // 更新结果
                dicomData[index].volume_result = data.volume_result;
                resultCell.textContent = data.volume_result;
                resultCell.className = 'result-success';
                statusDot.className = 'status-dot status-completed';
                showSuccessMessage('体积计算成功');
            } else {
                resultCell.textContent = '计算失败';
                resultCell.className = 'result-error';
                statusDot.className = 'status-dot status-pending';
                showErrorMessage(`体积计算失败: ${data.message}`);
            }
        })
        .catch(error => {
            // 更新状态
            item.is_processing = false;
            const statusDot = document.getElementById(`status-${index}`);
            statusDot.className = 'status-dot status-pending';
            
            // 恢复按钮状态
            calculateBtn.disabled = false;
            calculateBtn.textContent = '计算体积';

            resultCell.textContent = '计算失败';
            resultCell.className = 'result-error';
            showErrorMessage(`体积计算失败: ${error.message}`);
        });
    }

    // 导出CSV
    function exportToCsv() {
        if (dicomData.length === 0) {
            showErrorMessage('没有数据可导出');
            return;
        }

        // 构建CSV内容
        let csvContent = '子文件夹全路径,ROI文件名,计算结果(单位: mm³)\n';
        dicomData.forEach(item => {
            const folderPath = item.folder_path.replace(/,/g, ' ');
            const roiFile = item.roi_file.replace(/,/g, ' ');
            const volumeResult = item.volume_result || '未计算';
            csvContent += `${folderPath},${roiFile},${volumeResult}\n`;
        });

        // 创建Blob对象并下载
        const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
        const url = URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.setAttribute('href', url);
        link.setAttribute('download', `dicom_volume_results_${new Date().toISOString().slice(0, 10)}.csv`);
        link.style.visibility = 'hidden';
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);

        showSuccessMessage('数据已成功导出');
    }

    // 绑定表单提交事件
    if (folderForm) {
        folderForm.addEventListener('submit', function(event) {
            event.preventDefault();
            const folderPath = folderPathInput.value.trim();
            const roiFile = roiFileInput.value.trim();

            if (!folderPath) {
                showErrorMessage('请输入文件夹路径');
                return;
            }

            if (!roiFile) {
                showErrorMessage('请输入ROI文件名');
                return;
            }

            traverseFolder(folderPath, roiFile);
        });
    }

    // 绑定导出按钮事件
    if (exportBtn) {
        exportBtn.addEventListener('click', exportToCsv);
    }
});