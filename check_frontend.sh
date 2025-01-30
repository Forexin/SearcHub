#!/bin/bash

# 创建前端目录结构
mkdir -p frontend/static/{css,js,img}
mkdir -p frontend/templates/{components,pages}

# 复制静态文件
cat > frontend/static/css/style.css << 'EOL'
/* 暗色主题 */
.dark {
    background-color: #1a1a1a;
    color: #ffffff;
}

.dark .bg-white {
    background-color: #2d2d2d;
}

.dark .text-gray-600 {
    color: #a0aec0;
}

.dark .text-gray-800 {
    color: #e2e8f0;
}

.dark .border {
    border-color: #4a5568;
}

.dark .shadow {
    box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.3);
}

/* 模态框样式 */
.modal {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background-color: rgba(0, 0, 0, 0.5);
    display: flex;
    justify-content: center;
    align-items: center;
    z-index: 1000;
}

.modal-content {
    background-color: white;
    padding: 2rem;
    border-radius: 0.5rem;
    width: 90%;
    max-width: 600px;
    max-height: 90vh;
    overflow-y: auto;
}

.dark .modal-content {
    background-color: #2d2d2d;
}

/* 响应式设计 */
@media (max-width: 768px) {
    .container {
        padding-left: 1rem;
        padding-right: 1rem;
    }
    
    aside {
        position: fixed;
        z-index: 50;
        height: 100vh;
        transform: translateX(0);
        transition: transform 0.3s ease-in-out;
    }
    
    aside.hidden {
        transform: translateX(-100%);
    }
}

/* 自定义滚动条 */
::-webkit-scrollbar {
    width: 8px;
    height: 8px;
}

::-webkit-scrollbar-track {
    background: #f1f1f1;
}

::-webkit-scrollbar-thumb {
    background: #888;
    border-radius: 4px;
}

::-webkit-scrollbar-thumb:hover {
    background: #555;
}

/* 动画效果 */
.fade-enter {
    opacity: 0;
}

.fade-enter-active {
    opacity: 1;
    transition: opacity 200ms ease-in;
}

.fade-exit {
    opacity: 1;
}

.fade-exit-active {
    opacity: 0;
    transition: opacity 200ms ease-out;
}
EOL

cat > frontend/static/js/main.js << 'EOL'
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
EOL

# 复制模板文件
cat > frontend/templates/index.html << 'EOL'
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Data Aggregator</title>
    <link rel="stylesheet" href="{{ url_for('static', path='/css/style.css') }}">
    <link href="https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css" rel="stylesheet">
</head>
<body class="bg-gray-100">
    <div class="flex h-screen">
        <!-- 侧边栏 -->
        {% include "components/sidebar.html" %}
        
        <div class="flex-1 flex flex-col overflow-hidden">
            <!-- 顶部导航 -->
            {% include "components/header.html" %}
            
            <!-- 主内容区 -->
            <main class="flex-1 overflow-x-hidden overflow-y-auto bg-gray-200 p-6">
                {% block content %}{% endblock %}
            </main>
            
            <!-- 底部 -->
            {% include "components/footer.html" %}
        </div>
    </div>
    
    <script src="{{ url_for('static', path='/js/main.js') }}"></script>
</body>
</html>
EOL

cat > frontend/templates/error.html << 'EOL'
{% extends "index.html" %}

{% block content %}
<div class="container mx-auto text-center py-16">
    <div class="bg-white rounded-lg shadow p-8 max-w-lg mx-auto">
        <i class="fas fa-exclamation-circle text-6xl text-red-500 mb-4"></i>
        <h1 class="text-4xl font-bold mb-4">{{ error_code }}</h1>
        <p class="text-xl text-gray-600 mb-8">{{ error_message }}</p>
        <a href="/" class="bg-blue-500 text-white px-6 py-3 rounded hover:bg-blue-600">
            返回首页
        </a>
    </div>
</div>
{% endblock %}
EOL

# 复制组件
cat > frontend/templates/components/header.html << 'EOL'
<header class="bg-white shadow">
    <div class="container mx-auto px-6 py-4">
        <div class="flex items-center justify-between">
            <div class="flex items-center">
                <button id="menu-toggle" class="text-gray-500 focus:outline-none lg:hidden">
                    <i class="fas fa-bars"></i>
                </button>
                <h2 class="text-xl font-semibold text-gray-800 ml-4">
                    {% if request.url.path == '/dashboard' %}仪表盘
                    {% elif request.url.path == '/plugins' %}插件管理
                    {% elif request.url.path == '/config' %}配置管理
                    {% elif request.url.path == '/tools' %}工具管理
                    {% else %}首页{% endif %}
                </h2>
            </div>
            
            <div class="flex items-center">
                <button onclick="toggleTheme()" class="text-gray-500 hover:text-gray-600">
                    <i class="fas fa-moon"></i>
                </button>
            </div>
        </div>
    </div>
</header>
EOL

cat > frontend/templates/components/footer.html << 'EOL'
<footer class="bg-white shadow mt-auto">
    <div class="container mx-auto px-6 py-3">
        <div class="flex items-center justify-between">
            <div class="text-gray-600">
                © 2024 Data Aggregator. All rights reserved.
            </div>
            <div class="text-gray-600">
                Version 1.0.0
            </div>
        </div>
    </div>
</footer>
EOL

cat > frontend/templates/components/sidebar.html << 'EOL'
<aside class="w-64 bg-gray-800 text-white">
    <div class="p-4">
        <h1 class="text-2xl font-bold">Data Aggregator</h1>
    </div>
    
    <nav class="mt-4">
        <a href="/dashboard" class="block px-4 py-2 hover:bg-gray-700 {% if request.url.path == '/dashboard' %}bg-gray-700{% endif %}">
            <i class="fas fa-chart-line mr-2"></i>仪表盘
        </a>
        <a href="/plugins" class="block px-4 py-2 hover:bg-gray-700 {% if request.url.path == '/plugins' %}bg-gray-700{% endif %}">
            <i class="fas fa-puzzle-piece mr-2"></i>插件管理
        </a>
        <a href="/config" class="block px-4 py-2 hover:bg-gray-700 {% if request.url.path == '/config' %}bg-gray-700{% endif %}">
            <i class="fas fa-cog mr-2"></i>配置管理
        </a>
        <a href="/tools" class="block px-4 py-2 hover:bg-gray-700 {% if request.url.path == '/tools' %}bg-gray-700{% endif %}">
            <i class="fas fa-tools mr-2"></i>工具管理
        </a>
    </nav>
</aside>
EOL

# 复制页面
cat > frontend/templates/pages/dashboard.html << 'EOL'
{% extends "index.html" %}

{% block content %}
<div class="container mx-auto">
    <!-- 系统状态卡片 -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
        <div class="bg-white rounded-lg shadow p-6">
            <h3 class="text-lg font-semibold mb-2">活跃插件</h3>
            <p class="text-3xl font-bold text-blue-600">{{ active_plugins_count }}</p>
        </div>
        
        <div class="bg-white rounded-lg shadow p-6">
            <h3 class="text-lg font-semibold mb-2">总请求数</h3>
            <p class="text-3xl font-bold text-green-600">{{ total_requests }}</p>
        </div>
        
        <div class="bg-white rounded-lg shadow p-6">
            <h3 class="text-lg font-semibold mb-2">系统运行时间</h3>
            <p class="text-3xl font-bold text-purple-600">{{ uptime }}</p>
        </div>
    </div>
    
    <!-- 系统控制按钮 -->
    <div class="mb-6">
        <div class="bg-white rounded-lg shadow p-6">
            <div class="flex items-center justify-between">
                <h3 class="text-lg font-semibold">系统控制</h3>
                <div class="space-x-2">
                    <button onclick="controlSystem('start')" 
                            class="bg-green-500 text-white px-4 py-2 rounded hover:bg-green-600">
                        启动系统
                    </button>
                    <button onclick="controlSystem('stop')" 
                            class="bg-red-500 text-white px-4 py-2 rounded hover:bg-red-600">
                        停止系统
                    </button>
                    <button onclick="controlSystem('restart')" 
                            class="bg-yellow-500 text-white px-4 py-2 rounded hover:bg-yellow-600">
                        重启系统
                    </button>
                </div>
            </div>
        </div>
    </div>
    
    <!-- 插件状态列表 -->
    <div class="bg-white rounded-lg shadow p-6">
        <h2 class="text-xl font-semibold mb-4">插件状态</h2>
        <div class="overflow-x-auto">
            <table class="min-w-full">
                <thead>
                    <tr class="bg-gray-100">
                        <th class="px-6 py-3 text-left">插件名称</th>
                        <th class="px-6 py-3 text-left">状态</th>
                        <th class="px-6 py-3 text-left">请求数</th>
                        <th class="px-6 py-3 text-left">最后请求时间</th>
                    </tr>
                </thead>
                <tbody>
                    {% for plugin in plugins_status %}
                    <tr class="border-t">
                        <td class="px-6 py-4">{{ plugin.name }}</td>
                        <td class="px-6 py-4">
                            <span class="px-2 py-1 rounded text-sm 
                                {% if plugin.status == 'running' %}bg-green-100 text-green-800
                                {% else %}bg-red-100 text-red-800{% endif %}">
                                {{ plugin.status }}
                            </span>
                        </td>
                        <td class="px-6 py-4">{{ plugin.requests }}</td>
                        <td class="px-6 py-4">{{ plugin.last_request }}</td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
    </div>
</div>
{% endblock %}
EOL

cat > frontend/templates/pages/plugins.html << 'EOL'
{% extends "index.html" %}

{% block content %}
<div class="container mx-auto">
    <div class="bg-white rounded-lg shadow p-6">
        <h2 class="text-2xl font-bold mb-4">插件管理</h2>
        
        <!-- 插件列表 -->
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {% for plugin in plugins %}
            <div class="border rounded-lg p-4">
                <div class="flex justify-between items-center mb-2">
                    <h3 class="text-lg font-semibold">{{ plugin.name }}</h3>
                    <span class="px-2 py-1 rounded text-sm 
                        {% if plugin.status == 'running' %}bg-green-100 text-green-800
                        {% else %}bg-red-100 text-red-800{% endif %}">
                        {{ plugin.status }}
                    </span>
                </div>
                <p class="text-gray-600 text-sm mb-2">版本: {{ plugin.version }}</p>
                <p class="text-gray-600 text-sm mb-4">类型: {{ plugin.type }}</p>
                
                <div class="flex space-x-2">
                    <button onclick="togglePlugin('{{ plugin.name }}')" 
                            class="bg-blue-500 text-white px-3 py-1 rounded hover:bg-blue-600">
                        {% if plugin.status == 'running' %}停止{% else %}启动{% endif %}
                    </button>
                    <button onclick="showPluginConfig('{{ plugin.name }}')"
                            class="bg-gray-500 text-white px-3 py-1 rounded hover:bg-gray-600">
                        配置
                    </button>
                </div>
            </div>
            {% endfor %}
        </div>
        
        <!-- 添加新插件按钮 -->
        <div class="mt-6">
            <button onclick="showNewPluginForm()" 
                    class="bg-green-500 text-white px-4 py-2 rounded hover:bg-green-600">
                添加新插件
            </button>
        </div>
    </div>
</div>
{% endblock %}
EOL

cat > frontend/templates/pages/config.html << 'EOL'
{% extends "index.html" %}

{% block content %}
<div class="container mx-auto">
    <div class="bg-white rounded-lg shadow p-6">
        <h2 class="text-2xl font-bold mb-4">配置管理</h2>
        
        <!-- 配置文件列表 -->
        <div class="space-y-4">
            <div class="border rounded-lg p-4">
                <h3 class="text-lg font-semibold mb-2">系统配置</h3>
                <div id="systemConfigEditor" class="mb-4">
                    <textarea class="w-full h-64 font-mono">{{ system_config }}</textarea>
                </div>
                <div class="flex justify-end">
                    <button onclick="saveSystemConfig()" 
                            class="bg-blue-500 text-white px-4 py-2 rounded">
                        保存
                    </button>
                </div>
            </div>
            
            <div class="border rounded-lg p-4">
                <h3 class="text-lg font-semibold mb-2">环境变量</h3>
                <div id="envConfigEditor" class="mb-4">
                    <textarea class="w-full h-64 font-mono">{{ env_config }}</textarea>
                </div>
                <div class="flex justify-end">
                    <button onclick="saveEnvConfig()" 
                            class="bg-blue-500 text-white px-4 py-2 rounded">
                        保存
                    </button>
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}
EOL

cat > frontend/templates/pages/tools.html << 'EOL'
{% extends "index.html" %}

{% block content %}
<div class="container mx-auto">
    <div class="bg-white rounded-lg shadow p-6">
        <h2 class="text-2xl font-bold mb-4">工具管理</h2>
        
        <!-- 插件生成器 -->
        <div class="border rounded-lg p-6 mb-6">
            <h3 class="text-xl font-semibold mb-4">插件生成器</h3>
            <form id="pluginGeneratorForm" class="space-y-4">
                <div>
                    <label class="block text-sm font-medium text-gray-700">配置文件 (YAML)</label>
                    <textarea id="pluginConfig" rows="10" 
                              class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"></textarea>
                </div>
                
                <div>
                    <label class="block text-sm font-medium text-gray-700">代码片段</label>
                    <textarea id="codeSnippet" rows="10" 
                              class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"></textarea>
                </div>
                
                <div class="flex justify-end">
                    <button type="submit" 
                            class="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600">
                        生成插件
                    </button>
                </div>
            </form>
        </div>
    </div>
</div>
{% endblock %}
EOL

echo "前端目录结构检查完成" 