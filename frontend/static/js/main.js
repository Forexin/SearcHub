// 插件管理
async function togglePlugin(pluginName) {
    const status = document.querySelector(`#plugin-${pluginName} .status`).textContent;
    const action = status === 'running' ? 'stop' : 'start';
    
    try {
        const response = await fetch(`/api/plugins/${pluginName}/${action}`, {
            method: 'POST'
        });
        if (response.ok) {
            location.reload();
        }
    } catch (error) {
        console.error('Error:', error);
    }
}

// 配置管理
async function saveSystemConfig() {
    const config = document.querySelector('#systemConfigEditor textarea').value;
    try {
        const response = await fetch('/api/config/system', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ config })
        });
        if (response.ok) {
            alert('配置已保存');
        }
    } catch (error) {
        console.error('Error:', error);
    }
}

// 系统控制
async function controlSystem(action) {
    try {
        const response = await fetch(`/api/system/${action}`, {
            method: 'POST'
        });
        
        if (response.ok) {
            const result = await response.json();
            alert(result.message);
            if (action === 'stop') {
                setTimeout(() => {
                    location.reload();
                }, 2000);
            }
        }
    } catch (error) {
        console.error('Error:', error);
        alert('操作失败，请检查系统状态');
    }
}

// 主题切换
function toggleTheme() {
    document.body.classList.toggle('dark');
    localStorage.setItem('theme', document.body.classList.contains('dark') ? 'dark' : 'light');
}

// 初始化主题
document.addEventListener('DOMContentLoaded', () => {
    const theme = localStorage.getItem('theme') || 'light';
    if (theme === 'dark') {
        document.body.classList.add('dark');
    }
});

// 移动端菜单切换
document.getElementById('menu-toggle')?.addEventListener('click', () => {
    const sidebar = document.querySelector('aside');
    sidebar.classList.toggle('hidden');
});
