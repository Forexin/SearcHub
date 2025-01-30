document.addEventListener('DOMContentLoaded', function() {
    // 获取插件列表容器
    const pluginsList = document.getElementById('pluginsList');
    if (!pluginsList) return;

    // 为所有插件控制按钮添加事件监听
    const toggleButtons = pluginsList.querySelectorAll('.toggle-plugin');
    toggleButtons.forEach(button => {
        button.addEventListener('click', async function() {
            const pluginName = this.dataset.pluginName;
            const currentStatus = this.dataset.currentStatus;
            const action = currentStatus === 'running' ? 'stop' : 'start';
            
            try {
                // 禁用按钮，防止重复点击
                this.disabled = true;
                
                // 发送请求
                const response = await fetch(`/api/plugins/${pluginName}/${action}`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    }
                });
                
                const result = await response.json();
                
                if (response.ok) {
                    // 更新按钮状态
                    const newStatus = action === 'start' ? 'running' : 'stopped';
                    this.dataset.currentStatus = newStatus;
                    this.textContent = newStatus === 'running' ? '停止' : '启动';
                    
                    // 更新插件状态显示
                    const statusElement = this.closest('.plugin-item')
                        .querySelector('.plugin-status');
                    statusElement.textContent = newStatus;
                    statusElement.className = `plugin-status ${newStatus}`;
                    
                    // 显示成功消息
                    showMessage('success', result.message);
                } else {
                    throw new Error(result.message || '操作失败');
                }
            } catch (error) {
                console.error('Plugin operation failed:', error);
                showMessage('error', error.message || '操作失败');
            } finally {
                // 重新启用按钮
                this.disabled = false;
            }
        });
    });
});

// 显示消息提示
function showMessage(type, message) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${type}`;
    messageDiv.textContent = message;
    
    document.body.appendChild(messageDiv);
    
    // 3秒后自动移除消息
    setTimeout(() => {
        messageDiv.remove();
    }, 3000);
} 