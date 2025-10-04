# tuleaj-plugin-aggregator 开发文档

## 项目概述

基于 PySide6 和 QML 构建的插件化聚合工具开发指南，支持动态加载、热启动/关闭插件，提供统一的进程管理界面。

## 开发环境搭建

### 1. 环境要求

#### 1.1 系统要求

- **操作系统**: Windows 10/11, macOS 10.15+, Ubuntu 18.04+
- **Python版本**: Python 3.11 或更高版本
- **内存**: 建议 4GB 以上
- **磁盘空间**: 建议 2GB 以上可用空间

#### 1.2 开发工具

- **Python包管理器**: uv (推荐) 或 pip
- **IDE**: VS Code, PyCharm, 或其他支持 Python 的编辑器
- **版本控制**: Git
- **调试工具**: Python 调试器, Qt Creator (可选)

### 2. 环境安装

#### 2.1 安装 uv

```
# Windows (PowerShell)
irm https://astral.sh/uv/install.ps1 | iex

# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh
```

#### 2.2 创建项目环境

```
# 创建项目目录
mkdir tuleaj-plugin-aggregator
cd tuleaj-plugin-aggregator

# 初始化 uv 项目
uv init

# 安装依赖
uv add PySide6>=6.5.0
uv add toml>=0.10.0
uv add watchdog>=3.0.0
```

## 项目结构

### 1. 目录结构

```
tuleaj-plugin-aggregator/
├── src/
│   ├── main.py                 # 主程序入口
│   ├── core/                   # 核心模块
│   │   ├── __init__.py
│   │   ├── plugin_manager.py   # 插件管理器
│   │   ├── process_manager.py  # 进程管理器
│   │   ├── communication.py    # 通信管理器
│   │   └── config_manager.py   # 配置管理器
│   ├── ui/                     # QML 界面
│   │   ├── main.qml
│   │   ├── PluginListPanel.qml
│   │   └── PluginDocumentViewer.qml
│   └── utils/                  # 工具模块
│       ├── __init__.py
│       ├── logger.py           # 日志管理器
│       ├── exception_handler.py # 异常管理器
│       └── markdown_renderer.py
├── tests/                      # 测试代码
├── docs/                       # 文档目录
├── pyproject.toml              # 项目配置
├── config.toml                 # 主程序配置
└── README.md
```

### 2. 核心文件说明

#### 2.1 主程序入口 (src/main.py)

```python
"""
主程序入口文件
"""

import sys
from pathlib import Path
from PySide6.QtWidgets import QApplication
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtCore import QObject, Signal, Slot

from core.plugin_manager import PluginManager
from core.process_manager import ProcessManager
from core.config_manager import ConfigManager
from utils.logger import Logger
from utils.exception_handler import ExceptionHandler

class MainApplication(QObject):
    """主应用程序类"""
  
    def __init__(self):
        super().__init__()
        # 初始化日志和异常处理
        self.logger = Logger()
        self.exception_handler = ExceptionHandler()
        
        # 初始化核心管理器
        self.config_manager = ConfigManager()
        self.plugin_manager = PluginManager(self.logger, self.exception_handler)
        self.process_manager = ProcessManager(self.logger, self.exception_handler)
      
    def initialize(self):
        """初始化应用程序"""
        try:
            self.logger.info("开始初始化应用程序")
            
            # 加载配置
            self.config_manager.load_config()
            self.logger.info("配置加载完成")
      
            # 初始化插件管理器
            self.plugin_manager.initialize()
            self.logger.info("插件管理器初始化完成")
      
            # 扫描可用插件
            self.plugin_manager.scan_plugins()
            self.logger.info("插件扫描完成")
            
            self.logger.info("应用程序初始化成功")
            return True
            
        except Exception as e:
            self.exception_handler.handle_exception(e, "应用程序初始化失败")
            return False

def main():
    """主函数"""
    app = QApplication(sys.argv)
    app.setApplicationName("Tuleaj Plugin Aggregator")
    app.setApplicationVersion("1.0.0")
  
    # 创建主应用程序
    main_app = MainApplication()
    if not main_app.initialize():
        return 1
  
    # 创建 QML 引擎
    engine = QQmlApplicationEngine()
  
    # 注册 Python 对象到 QML
    engine.rootContext().setContextProperty("mainApp", main_app)
    engine.rootContext().setContextProperty("pluginManager", main_app.plugin_manager)
    engine.rootContext().setContextProperty("processManager", main_app.process_manager)
  
    # 加载 QML 界面
    qml_path = Path(__file__).parent / "ui" / "main.qml"
    engine.load(str(qml_path))
  
    if not engine.rootObjects():
        return 1
  
    return app.exec()

if __name__ == "__main__":
    sys.exit(main())
```

## 核心模块开发

### 1. 插件管理器 (PluginManager)

#### 1.1 基本结构

```python
# src/core/plugin_manager.py
from pathlib import Path
from typing import List, Dict, Optional
import toml
import subprocess
import sys

class PluginManager(QObject):
    """插件管理器"""
  
    # 信号定义
    plugin_installed = Signal(str)  # 插件安装完成
    plugin_uninstalled = Signal(str)  # 插件卸载完成
    plugin_status_changed = Signal(str, str)  # 插件状态变化
  
    def __init__(self, logger=None, exception_handler=None):
        super().__init__()
        self.logger = logger
        self.exception_handler = exception_handler
        self.plugins = {}  # 插件信息字典
        self.plugin_directory = Path("plugins")
      
    def scan_plugins(self):
        """扫描可用插件"""
        # 实现插件扫描逻辑
        pass
      
    def install_plugin(self, plugin_path: Path) -> bool:
        """安装插件"""
        # 实现插件安装逻辑
        pass
      
    def uninstall_plugin(self, plugin_name: str) -> bool:
        """卸载插件"""
        # 实现插件卸载逻辑
        pass
      
    def get_plugin_readme(self, plugin_name: str) -> str:
        """获取插件 README 文档"""
        # 实现文档读取逻辑
        pass
```

#### 1.2 关键方法实现

**插件扫描**

```python
def scan_plugins(self):
    """扫描可用插件"""
    try:
        if self.logger:
            self.logger.info("开始扫描插件")
            
        if not self.plugin_directory.exists():
            if self.logger:
                self.logger.warning(f"插件目录不存在: {self.plugin_directory}")
            return
      
        for plugin_dir in self.plugin_directory.iterdir():
            if plugin_dir.is_dir():
                pyproject_path = plugin_dir / "pyproject.toml"
                if pyproject_path.exists():
                    try:
                        config = toml.load(pyproject_path)
                        plugin_info = self._parse_plugin_config(config, plugin_dir)
                        self.plugins[plugin_info['name']] = plugin_info
                        
                        if self.logger:
                            self.logger.info(f"发现插件: {plugin_info['name']}")
                            
                    except Exception as e:
                        if self.exception_handler:
                            self.exception_handler.handle_plugin_exception(plugin_dir.name, e)
                        else:
                            print(f"解析插件配置失败: {e}")
        
        if self.logger:
            self.logger.info(f"插件扫描完成，共发现 {len(self.plugins)} 个插件")
            
    except Exception as e:
        if self.exception_handler:
            self.exception_handler.handle_exception(e, "插件扫描")
        else:
            print(f"插件扫描失败: {e}")
```

**插件安装**

```python
def install_plugin(self, plugin_path: Path) -> bool:
    """安装插件"""
    try:
        if self.logger:
            self.logger.info(f"开始安装插件: {plugin_path.name}")
            
        # 1. 检查插件兼容性
        if not self._check_plugin_compatibility(plugin_path):
            if self.logger:
                self.logger.warning(f"插件兼容性检查失败: {plugin_path.name}")
            return False
          
        # 2. 安装插件 (不使用缓存)
        install_cmd = [
            "uv", "pip", "install", 
            "--no-cache",
            str(plugin_path)
        ]
      
        if self.logger:
            self.logger.debug(f"执行安装命令: {' '.join(install_cmd)}")
            
        result = subprocess.run(install_cmd, capture_output=True, text=True)
        if result.returncode != 0:
            error_msg = f"插件安装失败: {result.stderr}"
            if self.logger:
                self.logger.error(error_msg)
            else:
                print(error_msg)
            return False
          
        # 3. 安装依赖 (使用缓存)
        self._install_plugin_dependencies(plugin_path)
      
        # 4. 解析文档
        readme_content = self._parse_plugin_readme(plugin_path)
      
        # 5. 注册插件
        self._register_plugin(plugin_path, readme_content)
      
        if self.logger:
            self.logger.info(f"插件安装成功: {plugin_path.name}")
            
        self.plugin_installed.emit(plugin_path.name)
        return True
      
    except Exception as e:
        if self.exception_handler:
            self.exception_handler.handle_plugin_exception(plugin_path.name, e)
        else:
            print(f"安装插件失败: {e}")
        return False
```

### 2. 进程管理器 (ProcessManager)

#### 2.1 基本结构

```python
# src/core/process_manager.py
import subprocess
import time
from typing import Dict, Optional
from PySide6.QtCore import QObject, Signal, QTimer

class ProcessManager(QObject):
    """进程管理器"""
  
    # 信号定义
    process_started = Signal(str, int)  # 进程启动 (插件名, PID)
    process_stopped = Signal(str, int)  # 进程停止 (插件名, 退出码)
    process_error = Signal(str, str)    # 进程错误 (插件名, 错误信息)
  
    def __init__(self, logger=None, exception_handler=None):
        super().__init__()
        self.logger = logger
        self.exception_handler = exception_handler
        self.running_processes = {}  # 运行中的进程
      
    def start_plugin(self, plugin_name: str, plugin_config: Dict) -> bool:
        """启动插件进程"""
        # 实现进程启动逻辑
        pass
      
    def stop_plugin(self, plugin_name: str) -> bool:
        """停止插件进程"""
        # 实现进程停止逻辑
        pass
      
    def get_process_status(self, plugin_name: str) -> str:
        """获取进程状态"""
        # 实现状态查询逻辑
        pass
```

#### 2.2 关键方法实现

**启动插件进程**

```python
def start_plugin(self, plugin_name: str, plugin_config: Dict) -> bool:
    """启动插件进程"""
    try:
        if self.logger:
            self.logger.info(f"开始启动插件进程: {plugin_name}")
            
        # 检查是否已运行
        if plugin_name in self.running_processes:
            if self.logger:
                self.logger.warning(f"插件进程已在运行: {plugin_name}")
            return True
          
        # 构建启动命令
        plugin_path = plugin_config['path']
        entry_point = plugin_config['entry_point']
      
        cmd = [
            "uv", "run",
            "--python", plugin_config.get('python_path', 'python'),
            str(plugin_path / entry_point)
        ]
      
        if self.logger:
            self.logger.debug(f"执行启动命令: {' '.join(cmd)}")
      
        # 启动进程
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=str(plugin_path)
        )
      
        # 记录进程信息
        self.running_processes[plugin_name] = {
            'process': process,
            'config': plugin_config,
            'status': 'running',
            'start_time': time.time(),
            'pid': process.pid
        }
      
        # 开始监控
        self._monitor_process(plugin_name, process)
      
        if self.logger:
            self.logger.info(f"插件进程启动成功: {plugin_name} (PID: {process.pid})")
            
        self.process_started.emit(plugin_name, process.pid)
        return True
      
    except Exception as e:
        if self.exception_handler:
            self.exception_handler.handle_process_exception(plugin_name, e)
        else:
            self.process_error.emit(plugin_name, str(e))
        return False
```

### 3. 日志管理器 (Logger)

#### 3.1 基本结构

```python
# src/utils/logger.py
import logging
import os
from pathlib import Path
from datetime import datetime
from typing import Optional

class Logger:
    """日志管理器"""
    
    def __init__(self, log_level: str = "INFO", log_dir: str = "logs"):
        self.log_level = getattr(logging, log_level.upper())
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        
        # 设置日志格式
        self.formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        # 创建根日志器
        self.logger = logging.getLogger("tuleaj_plugin_aggregator")
        self.logger.setLevel(self.log_level)
        
        # 清除现有处理器
        self.logger.handlers.clear()
        
        # 添加控制台处理器
        self._setup_console_handler()
        
        # 添加文件处理器
        self._setup_file_handler()
    
    def _setup_console_handler(self):
        """设置控制台处理器"""
        console_handler = logging.StreamHandler()
        console_handler.setLevel(self.log_level)
        console_handler.setFormatter(self.formatter)
        self.logger.addHandler(console_handler)
    
    def _setup_file_handler(self):
        """设置文件处理器"""
        # 按日期创建日志文件
        log_file = self.log_dir / f"app_{datetime.now().strftime('%Y%m%d')}.log"
        
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(self.log_level)
        file_handler.setFormatter(self.formatter)
        self.logger.addHandler(file_handler)
    
    def debug(self, message: str):
        """记录调试信息"""
        self.logger.debug(message)
    
    def info(self, message: str):
        """记录信息"""
        self.logger.info(message)
    
    def warning(self, message: str):
        """记录警告"""
        self.logger.warning(message)
    
    def error(self, message: str):
        """记录错误"""
        self.logger.error(message)
    
    def critical(self, message: str):
        """记录严重错误"""
        self.logger.critical(message)
    
    def set_level(self, level: str):
        """设置日志级别"""
        self.log_level = getattr(logging, level.upper())
        self.logger.setLevel(self.log_level)
        for handler in self.logger.handlers:
            handler.setLevel(self.log_level)
```

### 4. 异常管理器 (ExceptionHandler)

#### 4.1 基本结构

```python
# src/utils/exception_handler.py
import traceback
import sys
from typing import Optional, Callable
from PySide6.QtWidgets import QMessageBox
from PySide6.QtCore import QObject, Signal

class ExceptionHandler(QObject):
    """异常管理器"""
    
    # 信号定义
    exception_occurred = Signal(str, str)  # 异常发生 (异常类型, 异常信息)
    
    def __init__(self, logger=None):
        super().__init__()
        self.logger = logger
        self.error_callbacks = []
        
        # 设置全局异常处理器
        sys.excepthook = self.handle_uncaught_exception
    
    def add_error_callback(self, callback: Callable[[Exception, str], None]):
        """添加错误回调函数"""
        self.error_callbacks.append(callback)
    
    def handle_exception(self, exception: Exception, context: str = ""):
        """处理异常"""
        try:
            # 获取异常信息
            exc_type = type(exception).__name__
            exc_message = str(exception)
            exc_traceback = traceback.format_exc()
            
            # 记录日志
            if self.logger:
                self.logger.error(f"异常发生 - {context}: {exc_type}: {exc_message}")
                self.logger.debug(f"异常堆栈:\n{exc_traceback}")
            
            # 发送信号
            self.exception_occurred.emit(exc_type, exc_message)
            
            # 执行回调函数
            for callback in self.error_callbacks:
                try:
                    callback(exception, context)
                except Exception as e:
                    if self.logger:
                        self.logger.error(f"错误回调执行失败: {e}")
            
            # 显示用户友好的错误信息
            self._show_error_dialog(exc_type, exc_message, context)
            
        except Exception as e:
            # 异常处理器本身出错时的处理
            print(f"异常处理器出错: {e}")
    
    def handle_uncaught_exception(self, exc_type, exc_value, exc_traceback):
        """处理未捕获的异常"""
        if issubclass(exc_type, KeyboardInterrupt):
            # 不处理键盘中断
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return
        
        # 创建异常对象
        exception = exc_type(exc_value)
        
        # 处理异常
        self.handle_exception(exception, "未捕获的异常")
    
    def _show_error_dialog(self, exc_type: str, exc_message: str, context: str):
        """显示错误对话框"""
        try:
            msg_box = QMessageBox()
            msg_box.setIcon(QMessageBox.Critical)
            msg_box.setWindowTitle("错误")
            
            if context:
                msg_box.setText(f"在 {context} 时发生错误")
            else:
                msg_box.setText("发生错误")
            
            msg_box.setDetailedText(f"错误类型: {exc_type}\n错误信息: {exc_message}")
            msg_box.setStandardButtons(QMessageBox.Ok)
            msg_box.exec()
            
        except Exception as e:
            # 如果无法显示对话框，则打印到控制台
            print(f"无法显示错误对话框: {e}")
            print(f"错误类型: {exc_type}")
            print(f"错误信息: {exc_message}")
    
    def handle_plugin_exception(self, plugin_name: str, exception: Exception):
        """处理插件相关异常"""
        context = f"插件 '{plugin_name}' 操作"
        self.handle_exception(exception, context)
    
    def handle_process_exception(self, process_name: str, exception: Exception):
        """处理进程相关异常"""
        context = f"进程 '{process_name}' 操作"
        self.handle_exception(exception, context)
```

### 5. 配置管理器 (ConfigManager)

#### 5.1 基本结构

```python
# src/core/config_manager.py
import toml
from pathlib import Path
from typing import Dict, Any, Optional

class ConfigManager:
    """配置管理器"""
    
    def __init__(self, config_file: str = "config.toml"):
        self.config_file = Path(config_file)
        self.config = {}
        self.default_config = {
            "app": {
                "name": "Tuleaj Plugin Aggregator",
                "version": "1.0.0",
                "log_level": "INFO",
                "log_dir": "logs"
            },
            "environments": {
                "default": "python",
                "available": ["python", "python3.11", "python3.12"]
            },
            "plugins": {
                "directory": "plugins",
                "auto_scan": True,
                "cache_enabled": True
            },
            "proxy": {
                "enabled": False,
                "type": "http",
                "host": "localhost",
                "port": 8080
            }
        }
    
    def load_config(self) -> bool:
        """加载配置文件"""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    self.config = toml.load(f)
            else:
                self.config = self.default_config.copy()
                self.save_config()
            return True
        except Exception as e:
            print(f"加载配置失败: {e}")
            self.config = self.default_config.copy()
            return False
    
    def save_config(self) -> bool:
        """保存配置文件"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                toml.dump(self.config, f)
            return True
        except Exception as e:
            print(f"保存配置失败: {e}")
            return False
    
    def get(self, key: str, default: Any = None) -> Any:
        """获取配置值"""
        keys = key.split('.')
        value = self.config
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        return value
    
    def set(self, key: str, value: Any) -> bool:
        """设置配置值"""
        try:
            keys = key.split('.')
            config = self.config
            for k in keys[:-1]:
                if k not in config:
                    config[k] = {}
                config = config[k]
            config[keys[-1]] = value
            return True
        except Exception as e:
            print(f"设置配置失败: {e}")
            return False
```

### 6. 通信管理器 (CommunicationManager)

#### 6.1 基本结构

```python
# src/core/communication.py
import json
import socket
import threading
from typing import Dict, Callable, Optional
from PySide6.QtCore import QObject, Signal, QTimer

class CommunicationManager(QObject):
    """通信管理器"""
    
    # 信号定义
    message_received = Signal(str, dict)  # 消息接收 (来源, 消息内容)
    connection_established = Signal(str)  # 连接建立 (插件名)
    connection_lost = Signal(str)         # 连接断开 (插件名)
    
    def __init__(self, logger=None):
        super().__init__()
        self.logger = logger
        self.connections = {}  # 活跃连接
        self.message_handlers = {}  # 消息处理器
        self.server_socket = None
        self.running = False
        
    def start_server(self, host: str = "localhost", port: int = 0) -> int:
        """启动通信服务器"""
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.bind((host, port))
            self.server_socket.listen(5)
            
            # 获取实际端口
            actual_port = self.server_socket.getsockname()[1]
            
            self.running = True
            server_thread = threading.Thread(target=self._accept_connections)
            server_thread.daemon = True
            server_thread.start()
            
            if self.logger:
                self.logger.info(f"通信服务器启动: {host}:{actual_port}")
            
            return actual_port
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"启动通信服务器失败: {e}")
            return 0
    
    def stop_server(self):
        """停止通信服务器"""
        self.running = False
        if self.server_socket:
            self.server_socket.close()
            self.server_socket = None
    
    def register_message_handler(self, message_type: str, handler: Callable):
        """注册消息处理器"""
        self.message_handlers[message_type] = handler
    
    def send_message(self, plugin_name: str, message: dict) -> bool:
        """发送消息到插件"""
        if plugin_name not in self.connections:
            return False
        
        try:
            connection = self.connections[plugin_name]
            message_str = json.dumps(message) + '\n'
            connection.send(message_str.encode('utf-8'))
            return True
        except Exception as e:
            if self.logger:
                self.logger.error(f"发送消息失败: {e}")
            return False
    
    def _accept_connections(self):
        """接受连接"""
        while self.running:
            try:
                client_socket, address = self.server_socket.accept()
                client_thread = threading.Thread(
                    target=self._handle_client,
                    args=(client_socket, address)
                )
                client_thread.daemon = True
                client_thread.start()
            except Exception as e:
                if self.logger:
                    self.logger.error(f"接受连接失败: {e}")
    
    def _handle_client(self, client_socket, address):
        """处理客户端连接"""
        plugin_name = None
        try:
            while self.running:
                data = client_socket.recv(1024)
                if not data:
                    break
                
                message_str = data.decode('utf-8').strip()
                if not message_str:
                    continue
                
                try:
                    message = json.loads(message_str)
                    message_type = message.get('type', 'unknown')
                    
                    # 处理注册消息
                    if message_type == 'register':
                        plugin_name = message.get('plugin_name')
                        if plugin_name:
                            self.connections[plugin_name] = client_socket
                            self.connection_established.emit(plugin_name)
                            if self.logger:
                                self.logger.info(f"插件连接: {plugin_name}")
                    
                    # 处理其他消息
                    elif plugin_name:
                        self.message_received.emit(plugin_name, message)
                        
                        # 调用注册的处理器
                        if message_type in self.message_handlers:
                            self.message_handlers[message_type](plugin_name, message)
                
                except json.JSONDecodeError:
                    if self.logger:
                        self.logger.warning(f"无效的JSON消息: {message_str}")
        
        except Exception as e:
            if self.logger:
                self.logger.error(f"处理客户端连接失败: {e}")
        
        finally:
            if plugin_name and plugin_name in self.connections:
                del self.connections[plugin_name]
                self.connection_lost.emit(plugin_name)
                if self.logger:
                    self.logger.info(f"插件断开连接: {plugin_name}")
            client_socket.close()
```

### 7. QML 界面开发

#### 7.1 主界面 (main.qml)

```qml
import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

ApplicationWindow {
    id: mainWindow
    title: "插件聚合器"
    width: 1200
    height: 800
    visible: true
  
    SplitView {
        anchors.fill: parent
      
        // 左侧插件列表
        PluginListPanel {
            id: pluginPanel
            width: 300
          
            onPluginSelected: function(pluginName) {
                documentViewer.loadPluginDocument(pluginName)
            }
          
            onPluginStartRequested: function(pluginName) {
                processManager.startPlugin(pluginName)
            }
          
            onPluginStopRequested: function(pluginName) {
                processManager.stopPlugin(pluginName)
            }
        }
      
        // 右侧文档展示区域
        PluginDocumentViewer {
            id: documentViewer
            Layout.fillWidth: true
        }
    }
}
```

#### 3.2 插件列表面板 (PluginListPanel.qml)

```qml
import QtQuick 2.15
import QtQuick.Controls 2.15

ScrollView {
    id: root
  
    property alias pluginList: pluginListModel
  
    signal pluginSelected(string pluginName)
    signal pluginStartRequested(string pluginName)
    signal pluginStopRequested(string pluginName)
  
    ListView {
        id: pluginListView
        anchors.fill: parent
        model: ListModel {
            id: pluginListModel
        }
      
        delegate: PluginItem {
            width: parent.width
            height: 80
          
            pluginName: model.name
            pluginStatus: model.status
            pluginDescription: model.description
          
            onStartClicked: {
                root.pluginStartRequested(model.name)
            }
          
            onStopClicked: {
                root.pluginStopRequested(model.name)
            }
          
            onItemClicked: {
                root.pluginSelected(model.name)
            }
        }
    }
}
```

#### 3.3 文档查看器 (PluginDocumentViewer.qml)

```qml
import QtQuick 2.15
import QtQuick.Controls 2.15

ScrollView {
    id: root
  
    property string currentPluginName: ""
  
    function loadPluginDocument(pluginName) {
        currentPluginName = pluginName
        // 从插件管理器获取 README 内容
        var readmeContent = pluginManager.getPluginReadme(pluginName)
        markdownViewer.text = readmeContent
    }
  
    TextArea {
        id: markdownViewer
        anchors.fill: parent
        readOnly: true
        wrapMode: TextArea.Wrap
        textFormat: TextArea.MarkdownText
      
        text: "请选择一个插件查看文档"
    }
}
```

## 插件开发指南

### 1. 插件项目结构

```
my_plugin/
├── main.py              # 插件入口文件 (必需)
├── README.md            # 插件文档 (必需)
├── pyproject.toml       # 插件配置
├── ui/
│   └── main.qml         # 插件UI界面
└── resources/
    ├── icon.png         # 插件图标
    └── tray_icon.png    # 托盘图标
```

### 2. 插件配置文件 (pyproject.toml)

```toml
[project]
name = "my-plugin"
version = "1.0.0"
description = "我的插件"
authors = [
    {name = "Plugin Author", email = "author@example.com"}
]
requires-python = ">=3.11"
dependencies = [
    "PySide6>=6.5.0",
    "psutil>=5.9.0",
]

[project.scripts]
my-plugin = "main:main"

[tool.plugin]
entry_point = "main.py"
executable_name = "my-plugin"
icon_path = "resources/icon.png"
auto_start = false
```

### 3. 插件入口文件 (main.py)

```python
"""
插件入口文件
"""

import sys
import os
from pathlib import Path
from PySide6.QtWidgets import QApplication, QSystemTrayIcon, QMenu
from PySide6.QtCore import QObject, Signal, QTimer
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtGui import QIcon

class PluginApplication(QObject):
    """插件应用程序类"""
  
    # 定义信号
    window_closed = Signal()
    tray_activated = Signal()
  
    def __init__(self):
        super().__init__()
        self.app = None
        self.engine = None
        self.tray_icon = None
        self.window_visible = True
      
    def initialize(self):
        """初始化插件"""
        self.app = QApplication(sys.argv)
        self.app.setApplicationName("My Plugin")
        self.app.setApplicationVersion("1.0.0")
      
        # 设置托盘图标
        self.setup_tray_icon()
      
        # 创建QML引擎
        self.engine = QQmlApplicationEngine()
      
        # 加载QML界面
        qml_path = Path(__file__).parent / "ui" / "main.qml"
        self.engine.load(str(qml_path))
      
        return True
      
    def setup_tray_icon(self):
        """设置系统托盘"""
        if not QSystemTrayIcon.isSystemTrayAvailable():
            return
          
        self.tray_icon = QSystemTrayIcon()
        icon_path = Path(__file__).parent / "resources" / "tray_icon.png"
        if icon_path.exists():
            self.tray_icon.setIcon(QIcon(str(icon_path)))
          
        # 创建托盘菜单
        tray_menu = QMenu()
        show_action = tray_menu.addAction("显示窗口")
        hide_action = tray_menu.addAction("隐藏窗口")
        quit_action = tray_menu.addAction("退出")
      
        show_action.triggered.connect(self.show_window)
        hide_action.triggered.connect(self.hide_window)
        quit_action.triggered.connect(self.quit_application)
      
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.activated.connect(self.on_tray_activated)
        self.tray_icon.show()
      
    def show_window(self):
        """显示窗口"""
        if self.engine and self.engine.rootObjects():
            window = self.engine.rootObjects()[0]
            window.show()
            window.raise_()
            window.activateWindow()
            self.window_visible = True
          
    def hide_window(self):
        """隐藏窗口"""
        if self.engine and self.engine.rootObjects():
            window = self.engine.rootObjects()[0]
            window.hide()
            self.window_visible = False
          
    def on_tray_activated(self, reason):
        """托盘图标激活处理"""
        if reason == QSystemTrayIcon.DoubleClick:
            if self.window_visible:
                self.hide_window()
            else:
                self.show_window()
        self.tray_activated.emit()
      
    def quit_application(self):
        """退出应用程序"""
        if self.tray_icon:
            self.tray_icon.hide()
        self.app.quit()
      
    def run(self):
        """运行插件"""
        if not self.initialize():
            return 1
          
        # 连接窗口关闭信号
        if self.engine and self.engine.rootObjects():
            window = self.engine.rootObjects()[0]
            window.closing.connect(self.on_window_closing)
          
        return self.app.exec()
      
    def on_window_closing(self):
        """窗口关闭处理"""
        self.window_closed.emit()
        # 不直接退出，而是隐藏到托盘
        self.hide_window()

def main():
    """插件主入口函数"""
    plugin_app = PluginApplication()
    return plugin_app.run()

if __name__ == "__main__":
    sys.exit(main())
```

### 4. 插件 QML 界面 (ui/main.qml)

```qml
import QtQuick 2.15
import QtQuick.Controls 2.15

ApplicationWindow {
    id: root
    title: "我的插件"
    width: 600
    height: 400
    visible: true
  
    Rectangle {
        anchors.fill: parent
        color: "#f8f9fa"
      
        Column {
            anchors.centerIn: parent
            spacing: 20
          
            Text {
                text: "我的插件"
                font.pixelSize: 24
                font.bold: true
                anchors.horizontalCenter: parent.horizontalCenter
            }
          
            Text {
                text: "这是一个示例插件"
                font.pixelSize: 16
                anchors.horizontalCenter: parent.horizontalCenter
            }
          
            Button {
                text: "点击我"
                anchors.horizontalCenter: parent.horizontalCenter
                onClicked: {
                    console.log("按钮被点击了")
                }
            }
        }
    }
  
    // 窗口关闭处理
    onClosing: {
        close.accepted = false
        hide()
    }
}
```

### 5. 插件文档 (README.md)

```markdown
# 我的插件

## 插件描述

这是一个示例插件，用于演示插件开发的基本结构。

## 功能特性

- 独立的用户界面
- 系统托盘支持
- 窗口最小化到托盘
- 与主程序进程隔离

## 使用方法

1. 安装插件后，在主程序中点击启动
2. 插件会显示独立的窗口
3. 关闭窗口时，插件会最小化到系统托盘
4. 双击托盘图标可以重新显示窗口

## 配置说明

插件支持以下配置选项：

- `auto_start`: 是否自动启动
- `window_size`: 默认窗口大小
- `tray_enabled`: 是否启用托盘功能

## 开发信息

- **版本**: 1.0.0
- **作者**: Plugin Author
- **依赖**: PySide6, psutil
- **Python版本**: >=3.11
```

## 测试指南

### 1. 单元测试

```python
# tests/test_plugin_manager.py
import unittest
from pathlib import Path
from src.core.plugin_manager import PluginManager
from src.utils.logger import Logger
from src.utils.exception_handler import ExceptionHandler

class TestPluginManager(unittest.TestCase):
    def setUp(self):
        self.logger = Logger(log_level="DEBUG")
        self.exception_handler = ExceptionHandler(self.logger)
        self.plugin_manager = PluginManager(self.logger, self.exception_handler)
      
    def test_scan_plugins(self):
        """测试插件扫描"""
        self.plugin_manager.scan_plugins()
        # 验证插件是否正确扫描
      
    def test_install_plugin(self):
        """测试插件安装"""
        plugin_path = Path("test_plugin")
        result = self.plugin_manager.install_plugin(plugin_path)
        self.assertTrue(result)

# tests/test_logger.py
import unittest
import tempfile
import os
from src.utils.logger import Logger

class TestLogger(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.logger = Logger(log_level="DEBUG", log_dir=self.temp_dir)
    
    def test_log_levels(self):
        """测试不同日志级别"""
        self.logger.debug("调试信息")
        self.logger.info("信息")
        self.logger.warning("警告")
        self.logger.error("错误")
        self.logger.critical("严重错误")
    
    def test_log_file_creation(self):
        """测试日志文件创建"""
        self.logger.info("测试日志")
        # 验证日志文件是否创建

# tests/test_exception_handler.py
import unittest
from src.utils.exception_handler import ExceptionHandler
from src.utils.logger import Logger

class TestExceptionHandler(unittest.TestCase):
    def setUp(self):
        self.logger = Logger(log_level="DEBUG")
        self.exception_handler = ExceptionHandler(self.logger)
    
    def test_handle_exception(self):
        """测试异常处理"""
        try:
            raise ValueError("测试异常")
        except ValueError as e:
            self.exception_handler.handle_exception(e, "测试上下文")
    
    def test_error_callback(self):
        """测试错误回调"""
        callback_called = False
        
        def test_callback(exception, context):
            nonlocal callback_called
            callback_called = True
        
        self.exception_handler.add_error_callback(test_callback)
        
        try:
            raise RuntimeError("测试回调异常")
        except RuntimeError as e:
            self.exception_handler.handle_exception(e, "测试回调")
        
        self.assertTrue(callback_called)

if __name__ == '__main__':
    unittest.main()
```

### 2. 集成测试

```python
# tests/test_integration.py
import unittest
from src.main import MainApplication

class TestIntegration(unittest.TestCase):
    def setUp(self):
        self.app = MainApplication()
      
    def test_app_initialization(self):
        """测试应用程序初始化"""
        result = self.app.initialize()
        self.assertTrue(result)
      
    def test_plugin_lifecycle(self):
        """测试插件生命周期"""
        # 测试插件安装、启动、停止、卸载
        pass

if __name__ == '__main__':
    unittest.main()
```

## 部署指南

### 1. 主程序打包

```bash
# 使用 PyInstaller 打包
pyinstaller --onedir --windowed --name "TuleajPluginAggregator" src/main.py

# 添加额外文件
pyinstaller --add-data "ui;ui" --add-data "config.toml;." src/main.py
```

### 2. 插件打包

```bash
# 进入插件目录
cd plugins/my_plugin

# 使用 uv 打包
uv build --wheel

# 生成的文件在 dist/ 目录
```

### 3. 分发部署

```bash
# 创建分发目录
mkdir TuleajPluginAggregator-Distribution
cp dist/TuleajPluginAggregator/* TuleajPluginAggregator-Distribution/
cp plugins/*.whl TuleajPluginAggregator-Distribution/plugins/

# 创建安装脚本
echo "uv pip install plugins/*.whl" > install_plugins.bat
```

## 常见问题

### 1. 插件无法启动

**问题**: 插件安装后无法启动
**解决方案**:

- 检查插件入口文件是否正确
- 验证依赖是否完整安装
- 查看错误日志

### 2. QML 界面不显示

**问题**: 插件启动后界面不显示
**解决方案**:

- 检查 QML 文件路径
- 验证 QML 语法
- 确保 ApplicationWindow 设置了 visible: true

### 3. 托盘功能不工作

**问题**: 系统托盘图标不显示
**解决方案**:

- 检查系统是否支持托盘
- 验证图标文件路径
- 确保 QSystemTrayIcon 正确初始化

### 4. 日志文件过大

**问题**: 日志文件占用过多磁盘空间
**解决方案**:

- 调整日志级别，减少不必要的日志记录
- 实现日志轮转机制，定期清理旧日志
- 设置日志文件大小限制

### 5. 异常处理不生效

**问题**: 程序崩溃时异常处理器没有捕获到异常
**解决方案**:

- 检查异常处理器是否正确初始化
- 确保在关键代码块中使用 try-except
- 验证全局异常处理器设置

## 性能优化指南

### 1. 内存优化

#### 1.1 进程管理优化
- **进程池**: 使用进程池管理插件进程，避免频繁创建/销毁
- **内存监控**: 定期监控插件进程内存使用情况
- **资源清理**: 及时清理不再使用的插件资源
- **弱引用**: 使用弱引用避免循环引用导致的内存泄漏

#### 1.2 QML 界面优化
- **组件复用**: 避免重复创建相同的 QML 组件
- **延迟加载**: 使用 Loader 组件实现按需加载
- **属性绑定优化**: 减少不必要的属性绑定
- **动画优化**: 使用硬件加速的动画效果

### 2. 启动性能优化

#### 2.1 应用启动优化
- **异步初始化**: 将耗时操作放在后台线程
- **预加载**: 预加载常用插件配置
- **缓存机制**: 缓存插件元数据和配置信息
- **延迟加载**: 按需加载插件界面

#### 2.2 插件启动优化
- **并行启动**: 支持多个插件并行启动
- **启动超时**: 设置合理的启动超时时间
- **状态缓存**: 缓存插件状态信息

### 3. 网络性能优化

#### 3.1 通信优化
- **连接池**: 复用网络连接
- **消息压缩**: 对大型消息进行压缩
- **批量处理**: 批量处理多个消息
- **超时控制**: 设置合理的网络超时时间

## 安全考虑

### 1. 插件安全

#### 1.1 沙箱隔离
- **进程隔离**: 插件运行在独立进程中
- **权限控制**: 限制插件访问系统资源
- **文件系统隔离**: 限制插件文件访问范围
- **网络隔离**: 控制插件的网络访问权限

#### 1.2 代码安全
- **代码签名**: 对插件包进行数字签名验证
- **依赖检查**: 验证插件依赖的安全性
- **恶意代码检测**: 扫描插件代码中的恶意行为
- **权限最小化**: 只授予插件必要的权限

### 2. 数据安全

#### 2.1 配置安全
- **敏感信息加密**: 加密存储敏感配置信息
- **访问控制**: 限制配置文件的访问权限
- **备份加密**: 对配置文件备份进行加密

#### 2.2 通信安全
- **消息加密**: 对敏感消息进行加密传输
- **身份验证**: 验证插件身份
- **消息完整性**: 确保消息传输的完整性

## 国际化支持

### 1. 多语言支持

#### 1.1 文本国际化
- **Qt 国际化**: 使用 Qt 的国际化框架
- **翻译文件**: 支持 .ts 翻译文件
- **动态语言切换**: 支持运行时切换语言
- **本地化资源**: 支持本地化的图标和资源文件

#### 1.2 插件国际化
- **插件翻译**: 支持插件的多语言翻译
- **翻译管理**: 提供翻译文件管理功能
- **自动翻译**: 支持自动翻译检测

### 2. 区域设置

#### 2.1 日期时间格式
- **本地化格式**: 根据系统设置显示日期时间
- **时区支持**: 支持不同时区设置
- **格式配置**: 允许用户自定义格式

#### 2.2 数字和货币
- **数字格式**: 支持不同地区的数字格式
- **货币显示**: 支持不同货币符号和格式
- **单位转换**: 支持不同单位系统

## 开发最佳实践

### 1. 代码规范

- 使用 Python 类型提示
- 遵循 PEP 8 代码风格
- 添加详细的文档字符串
- 使用有意义的变量和函数名

### 2. 错误处理

- 使用 try-except 处理异常
- 提供有意义的错误信息
- 记录详细的错误日志
- 优雅地处理失败情况
- 使用统一的异常处理器
- 为不同类型的异常提供专门的处理器

### 3. 日志管理

- 使用适当的日志级别 (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- 记录关键操作和状态变化
- 避免在循环中记录过多日志
- 定期清理和轮转日志文件
- 在生产环境中使用合适的日志级别

### 4. 性能优化

- 避免阻塞主线程
- 使用异步操作处理耗时任务
- 及时释放不需要的资源
- 优化 QML 界面渲染

### 5. 测试策略

- 编写单元测试
- 进行集成测试
- 测试错误处理
- 验证用户界面功能
- 测试日志记录功能
- 验证异常处理机制

## 贡献指南

### 1. 代码贡献

1. Fork 项目仓库
2. 创建功能分支
3. 编写代码和测试
4. 提交 Pull Request

### 2. 插件贡献

1. 按照插件开发指南创建插件
2. 编写完整的文档
3. 进行充分测试
4. 提交插件包

### 3. 文档贡献

1. 更新相关文档
2. 添加使用示例
3. 修复文档错误
4. 改进文档结构

## 许可证

本项目采用 MIT 许可证，详见 LICENSE 文件。

## 文档完整性评估

### 已涵盖的核心内容

#### ✅ 基础架构
- **项目概述**: 清晰的项目定位和技术栈说明
- **环境搭建**: 完整的开发环境配置指南
- **项目结构**: 详细的目录结构和文件说明

#### ✅ 核心模块开发
- **插件管理器**: 完整的插件生命周期管理
- **进程管理器**: 插件进程的启动、监控、停止
- **通信管理器**: 主程序与插件间的通信机制
- **配置管理器**: 配置文件的加载、保存、管理
- **日志管理器**: 多级别日志记录和文件管理
- **异常管理器**: 全局异常处理和用户友好提示

#### ✅ 界面开发
- **QML 界面**: 主界面、插件列表、文档查看器
- **UI 组件**: 完整的 QML 组件实现
- **交互逻辑**: 用户交互和事件处理

#### ✅ 插件开发
- **插件结构**: 标准化的插件项目结构
- **配置规范**: 插件配置文件和元数据
- **独立运行**: 插件作为独立程序的设计
- **文档要求**: README.md 文档规范

#### ✅ 测试和部署
- **单元测试**: 各模块的测试用例
- **集成测试**: 整体功能测试
- **打包部署**: PyInstaller 和 uv 的混合打包
- **分发策略**: 完整的部署流程

#### ✅ 高级特性
- **性能优化**: 内存、启动、网络性能优化
- **安全考虑**: 插件安全、数据安全
- **国际化支持**: 多语言和本地化支持
- **最佳实践**: 开发规范和代码质量

#### ✅ 运维支持
- **常见问题**: 问题诊断和解决方案
- **故障排除**: 详细的调试指南
- **贡献指南**: 代码和插件贡献流程

### 文档特色

1. **结构完整**: 从环境搭建到部署运维的完整覆盖
2. **实用性强**: 提供大量可执行的代码示例
3. **技术深度**: 涵盖架构设计、性能优化、安全考虑
4. **易于理解**: 清晰的层次结构和详细的说明
5. **可扩展性**: 为未来功能扩展预留了空间

### 适用人群

- **初级开发者**: 通过详细的环境搭建和基础教程快速上手
- **中级开发者**: 通过核心模块开发指南深入理解架构
- **高级开发者**: 通过性能优化和安全考虑提升代码质量
- **插件开发者**: 通过插件开发指南创建自己的插件
- **运维人员**: 通过部署和故障排除指南进行系统维护

## 联系方式

- **项目主页**: https://github.com/tuleaj/tuleaj-plugin-aggregator
- **问题反馈**: https://github.com/tuleaj/tuleaj-plugin-aggregator/issues
- **邮箱**: contact@tuleaj.com
