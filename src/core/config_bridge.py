"""
配置桥接器
用于连接Python配置管理器和QML界面
提供QML可以直接调用的配置管理接口
"""

import sys
import subprocess
import os
from pathlib import Path
from typing import Dict, Any, List, Optional
from PySide6.QtCore import QObject, Signal, Property, QTimer, Slot, QThread
from PySide6.QtQml import qmlRegisterType

# 添加src目录到Python路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.config_manager import ConfigManager
from utils.logger import Logger
from utils.exception_handler import (
    ExceptionHandler, 
    set_global_exception_handler,
    handle_exceptions,
    silent_exceptions
)


class PythonEnvironmentWorker(QThread):
    """Python环境管理工作线程"""
    
    # 信号定义
    environmentCreated = Signal(str, bool, str)  # 环境名, 成功状态, 消息
    environmentDeleted = Signal(str, bool, str)  # 环境名, 成功状态, 消息
    environmentListUpdated = Signal(list)  # 环境列表
    environmentInfoUpdated = Signal(dict)  # 环境信息
    
    # 内部信号，用于在工作线程中触发操作
    createEnvironmentRequested = Signal(str, str, int)  # 环境名, Python版本, 超时时间
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.logger = Logger(log_level="INFO")
        # 设置环境目录为项目根目录下的envs目录
        project_root = Path(__file__).parent.parent.parent  # 从src/core/config_bridge.py回到项目根目录
        self.environments_dir = project_root / "envs"
        self.environments_dir.mkdir(exist_ok=True)
        
        # 连接内部信号，使用QueuedConnection确保在工作线程中执行
        from PySide6.QtCore import Qt
        self.createEnvironmentRequested.connect(self.create_environment, Qt.QueuedConnection)
    
    def run(self):
        """线程主循环"""
        try:
            # 检查是否需要扫描环境（如果父对象已经有环境信息，就不需要重复扫描）
            if hasattr(self.parent(), '_environments_cache') and self.parent()._environments_cache:
                self.logger.info("环境信息已从配置文件加载，跳过重复扫描")
                # 直接发送已加载的环境信息
                self.environmentListUpdated.emit(self.parent()._environments_cache)
            else:
                self.logger.info("配置文件没有环境信息，开始扫描环境")
                self.refresh_environments()
        except Exception as e:
            self.logger.error(f"环境工作线程启动时发生错误: {str(e)}")
            # 即使出错也要发送空列表，避免前端卡住
            self.environmentListUpdated.emit([])
    
    def create_environment(self, env_name: str, python_version: str = "3.11", timeout_seconds: int = 60):
        """使用uv init创建项目环境"""
        try:
            env_path = self.environments_dir / env_name
            
            if env_path.exists():
                self.environmentCreated.emit(env_name, False, f"环境 '{env_name}' 已存在")
                return
            
            # 创建环境目录
            env_path.mkdir(parents=True, exist_ok=True)
            self.logger.info(f"创建环境目录: {env_path}")
            
            # 创建 pyproject.toml 文件来管理环境
            try:
                self.logger.info(f"开始创建环境 {env_name}，超时时间: {timeout_seconds} 秒")
                
                # 检查 uv 是否可用
                try:
                    uv_check = subprocess.run(["uv", "--version"], capture_output=True, text=True, timeout=10, encoding='utf-8', errors='ignore')
                    self.logger.info(f"uv 版本检查: {uv_check.stdout.strip()}")
                except Exception as e:
                    self.logger.error(f"uv 命令检查失败: {str(e)}")
                    self.environmentCreated.emit(env_name, False, f"uv 命令不可用: {str(e)}")
                    return
                
                # 创建 pyproject.toml 文件
                pyproject_content = f'''[project]
name = "{env_name}"
version = "0.1.0"
description = "Virtual environment for {env_name}"
requires-python = ">={python_version}"

[tool.uv]
dev-dependencies = []
'''
                
                pyproject_path = env_path / "pyproject.toml"
                with open(pyproject_path, 'w', encoding='utf-8') as f:
                    f.write(pyproject_content)
                
                self.logger.info(f"创建 pyproject.toml 文件: {pyproject_path}")
                
                # 使用 uv venv 来创建虚拟环境（这会直接创建 .venv 目录）
                cmd = ["uv", "venv", "--python", f"{python_version}"]
                self.logger.info(f"执行命令: {' '.join(cmd)}")
                self.logger.info(f"工作目录: {env_path}")
                
                result = subprocess.run(cmd, check=True, capture_output=True, text=True, 
                                      timeout=timeout_seconds, cwd=str(env_path), encoding='utf-8', errors='ignore')
                self.logger.info(f"uv venv 输出: {result.stdout}")
                if result.stderr:
                    self.logger.info(f"uv venv 错误输出: {result.stderr}")
                    
            except subprocess.TimeoutExpired:
                self.logger.error(f"环境创建超时: {env_name}，超时时间: {timeout_seconds} 秒")
                self.environmentCreated.emit(env_name, False, f"环境创建超时（{timeout_seconds}秒），请检查网络连接或重试")
                return
            except subprocess.CalledProcessError as e:
                self.logger.error(f"环境创建失败: {env_name}，错误: {str(e)}")
                self.logger.error(f"错误输出: {e.stderr}")
                self.environmentCreated.emit(env_name, False, f"环境创建失败: {str(e)}")
                return
            
            # 检查 .venv 目录是否创建成功
            venv_path = env_path / ".venv"
            if not venv_path.exists():
                self.logger.error(f".venv 目录未创建: {venv_path}")
                self.environmentCreated.emit(env_name, False, "虚拟环境目录创建失败")
                return
            
            # 获取Python可执行文件路径
            if os.name == 'nt':  # Windows
                python_exe = venv_path / "Scripts" / "python.exe"
            else:  # Unix/Linux
                python_exe = venv_path / "bin" / "python"
            
            # 获取Python版本信息
            try:
                version_result = subprocess.run([str(python_exe), "--version"], 
                                              capture_output=True, text=True, check=True, timeout=30, encoding='utf-8', errors='ignore')
                python_version_info = version_result.stdout.strip()
            except subprocess.TimeoutExpired:
                self.environmentCreated.emit(env_name, False, "获取Python版本信息超时")
                return
            except subprocess.CalledProcessError as e:
                self.logger.warning(f"获取Python版本失败: {str(e)}")
                python_version_info = "版本信息获取失败"
            
            self.logger.info(f"成功使用uv创建虚拟环境: {env_name}")
            self.environmentCreated.emit(env_name, True, f"环境创建成功: {python_version_info}")
            
        except Exception as e:
            self.logger.error(f"创建环境时发生未预期错误: {str(e)}")
            self.environmentCreated.emit(env_name, False, f"创建环境时发生错误: {str(e)}")
    
    @handle_exceptions(context="删除虚拟环境", show_dialog=False, log_level="ERROR")
    def delete_environment(self, env_name: str):
        """删除虚拟环境"""
        env_path = self.environments_dir / env_name
        
        if not env_path.exists():
            self.environmentDeleted.emit(env_name, False, f"环境 '{env_name}' 不存在")
            return
        
        # 删除环境目录
        import shutil
        shutil.rmtree(env_path)
        
        self.logger.info(f"成功删除虚拟环境: {env_name}")
        self.environmentDeleted.emit(env_name, True, f"环境 '{env_name}' 删除成功")
    
    @handle_exceptions(context="刷新环境列表", show_dialog=False, log_level="WARNING")
    def refresh_environments(self):
        """刷新环境列表"""
        self.logger.info(f"开始扫描环境目录: {self.environments_dir}")
        environments = []
        
        if not self.environments_dir.exists():
            self.logger.warning(f"环境目录不存在: {self.environments_dir}")
            self.environmentListUpdated.emit(environments)
            return
        
        try:
            env_dirs = list(self.environments_dir.iterdir())
            self.logger.info(f"找到 {len(env_dirs)} 个目录")
            
            for env_dir in env_dirs:
                if env_dir.is_dir():
                    self.logger.info(f"扫描环境: {env_dir.name}")
                    env_info = self.get_environment_info(env_dir.name)
                    if env_info:
                        environments.append(env_info)
                        self.logger.info(f"成功获取环境信息: {env_dir.name}")
                    else:
                        self.logger.warning(f"无法获取环境信息: {env_dir.name}")
                else:
                    self.logger.debug(f"跳过非目录项: {env_dir.name}")
        except Exception as e:
            self.logger.error(f"扫描环境目录时发生错误: {str(e)}")
        
        self.logger.info(f"扫描完成，找到 {len(environments)} 个有效环境")
        self.environmentListUpdated.emit(environments)
    
    @silent_exceptions(return_value=None)
    def get_environment_info(self, env_name: str) -> Optional[Dict[str, Any]]:
        """获取环境信息"""
        env_path = self.environments_dir / env_name
        
        if not env_path.exists():
            self.logger.warning(f"环境路径不存在: {env_path}")
            return None
        
        # 检查是否是 uv init 创建的环境（有 .venv 目录）
        venv_path = env_path / ".venv"
        if venv_path.exists():
            # uv init 创建的环境
            if os.name == 'nt':  # Windows
                python_exe = venv_path / "Scripts" / "python.exe"
                pip_exe = venv_path / "Scripts" / "pip.exe"
            else:  # Unix/Linux
                python_exe = venv_path / "bin" / "python"
                pip_exe = venv_path / "bin" / "pip"
        else:
            # 传统的 venv 创建的环境
            if os.name == 'nt':  # Windows
                python_exe = env_path / "Scripts" / "python.exe"
                pip_exe = env_path / "Scripts" / "pip.exe"
            else:  # Unix/Linux
                python_exe = env_path / "bin" / "python"
                pip_exe = env_path / "bin" / "pip"
        
        if not python_exe.exists():
            self.logger.warning(f"Python可执行文件不存在: {python_exe}")
            return None
        
        # 获取Python版本
        try:
            result = subprocess.run([str(python_exe), "--version"], 
                                  capture_output=True, text=True, check=True, timeout=10)
            python_version = result.stdout.strip()
            self.logger.info(f"获取到Python版本: {python_version}")
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as e:
            self.logger.error(f"获取Python版本失败: {str(e)}")
            python_version = "未知版本"
        
        # 使用uv获取已安装的包
        packages = []
        try:
            # 使用uv pip list获取包列表
            uv_cmd = ["uv", "pip", "list", "--python", str(python_exe)]
            result = subprocess.run(uv_cmd, capture_output=True, text=True, check=True, timeout=30, encoding='utf-8', errors='replace')
            
            # 解析uv pip list的输出
            lines = result.stdout.strip().split('\n')
            for line in lines[2:]:  # 跳过标题行
                if line.strip():
                    parts = line.split()
                    if len(parts) >= 2:
                        packages.append({
                            "name": parts[0],
                            "version": parts[1]
                        })
            self.logger.info(f"使用uv获取到 {len(packages)} 个包")
        except (subprocess.CalledProcessError, IndexError, ValueError, subprocess.TimeoutExpired) as e:
            self.logger.warning(f"使用uv获取包列表失败: {str(e)}")
            # 如果uv失败，尝试使用pip
            try:
                result = subprocess.run([str(pip_exe), "list", "--format=json"], 
                                      capture_output=True, text=True, check=True, timeout=30)
                import json
                packages = json.loads(result.stdout)
                self.logger.info(f"使用pip获取到 {len(packages)} 个包")
            except (subprocess.CalledProcessError, json.JSONDecodeError, ValueError, subprocess.TimeoutExpired) as e:
                self.logger.warning(f"使用pip获取包列表也失败: {str(e)}")
                packages = []
        
        # 获取环境大小
        total_size = 0
        try:
            for file_path in env_path.rglob('*'):
                if file_path.is_file():
                    total_size += file_path.stat().st_size
        except Exception as e:
            self.logger.warning(f"计算环境大小时发生错误: {str(e)}")
            total_size = 0
        
        # 检查是否为当前环境
        # 通过父对象（ConfigBridge）获取当前环境名称
        current_env_name = ""
        if hasattr(self.parent(), 'currentEnvironmentName'):
            current_env_name = self.parent().currentEnvironmentName
        
        env_info = {
            "name": env_name,
            "path": str(env_path),
            "python_version": python_version,
            "packages_count": len(packages),
            "size_mb": round(total_size / (1024 * 1024), 2),
            "created_time": env_path.stat().st_ctime,
            "is_active": env_name == current_env_name
        }
        
        self.logger.info(f"构建环境信息: {env_info}")
        return env_info


class ConfigBridge(QObject):
    """配置桥接器 - 连接Python配置管理器和QML界面"""
    
    # 信号定义
    configLoaded = Signal()
    configSaved = Signal() 
    configError = Signal(str)  # 错误信息
    mirrorSourceAdded = Signal(str, str, int)  # 名称, URL, 优先级
    mirrorSourceRemoved = Signal(str)
    mirrorSourcesChanged = Signal()  # 镜像源列表变化
    pluginAdded = Signal(str)  # 插件名称
    pluginRemoved = Signal(str)
    
    # Python环境管理信号
    environmentCreated = Signal(str, bool, str)  # 环境名, 成功状态, 消息
    environmentDeleted = Signal(str, bool, str)  # 环境名, 成功状态, 消息
    environmentListUpdated = Signal(list)  # 环境列表
    environmentsListChanged = Signal()  # 环境列表变化
    currentEnvironmentChanged = Signal(str)  # 当前环境变化
    
    # 统一消息提示信号
    showMessageSignal = Signal(str, str, str, int)  # 类型, 标题, 内容, 持续时间
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # 初始化日志和异常处理器
        self.logger = Logger(log_level="INFO")
        self.exception_handler = ExceptionHandler(self.logger)
        set_global_exception_handler(self.exception_handler)
        
        # 初始化配置管理器
        self.config_manager = ConfigManager("config.toml")
        
        # 连接配置管理器信号
        self.config_manager.config_loaded.connect(self.configLoaded.emit)
        self.config_manager.config_saved.connect(self.configSaved.emit)
        self.config_manager.config_error.connect(self.configError.emit)
        
        # 加载配置
        self.config_manager.load_config()
        
        # 定时保存配置
        self.save_timer = QTimer()
        self.save_timer.timeout.connect(self.auto_save_config)
        self.save_timer.start(30000)  # 30秒自动保存一次
        
        # 初始化Python环境工作线程
        self.env_worker = PythonEnvironmentWorker(self)
        self.env_worker.environmentCreated.connect(self._on_environment_created)
        self.env_worker.environmentDeleted.connect(self._on_environment_deleted)
        self.env_worker.environmentListUpdated.connect(self._update_environments_cache)
        self.env_worker.environmentListUpdated.connect(self.environmentListUpdated.emit)
        
        # 启动环境工作线程
        self.env_worker.start()
        
        # 环境列表缓存
        self._environments_cache = []
        
        # 镜像源列表缓存
        self._mirror_sources_cache = self.config_manager.get("mirrors.sources", [])
        
        # 从配置文件加载已保存的环境信息（快速加载）
        self._load_environments_from_config()
        
    
    # === 应用配置属性 ===
    @Property(str, constant=True)
    def appName(self) -> str:
        """应用名称"""
        return self.config_manager.get("app.name", "Tuleaj Plugin Aggregator")
    
    @Property(str, constant=True)
    def appVersion(self) -> str:
        """应用版本"""
        return self.config_manager.get("app.version", "1.0.0")
    
    @Property(str, constant=True)
    def logLevel(self) -> str:
        """日志级别"""
        return self.config_manager.get("logging.log_level", "INFO")
    
    # === UI配置属性 ===
    @Property(str, constant=True)
    def theme(self) -> str:
        """主题"""
        return self.config_manager.get("ui.theme", "auto")
    
    # 移除不再需要的UI配置属性，因为配置文件中只有theme是有用的
    
    # === 环境配置属性 ===
    @Property(str, constant=True)
    def defaultEnvironment(self) -> str:
        """默认环境"""
        return self.config_manager.get("environments.default", "python3.11")
    
    @Property(list, constant=True)
    def availableEnvironments(self) -> List[str]:
        """可用环境列表"""
        return self.config_manager.get("environments.available", ["python3.11", "python3.12"])
    
    @Property(list, notify=environmentsListChanged)
    def environmentsList(self) -> List[Dict[str, Any]]:
        """环境列表（包含详细信息）"""
        return self._environments_cache
    
    @Property(str, notify=currentEnvironmentChanged)
    def currentEnvironmentName(self) -> str:
        """当前环境名称"""
        return self.config_manager.get("environments.current", "tuleaj-plugin-aggregator")
    
    @Property(str, notify=currentEnvironmentChanged)
    def currentEnvironmentPath(self) -> str:
        """当前环境路径"""
        return self.config_manager.get("environments.current_path", "")
    
    @Property(str, notify=currentEnvironmentChanged)
    def currentPythonVersion(self) -> str:
        """当前Python版本"""
        return self.config_manager.get("environments.current_python_version", "Python 3.11.0")
    
    # === 插件配置属性 ===
    @Property(str, constant=True)
    def pluginDirectory(self) -> str:
        """插件目录"""
        return self.config_manager.get("plugins.directory", "plugins")
    
    @Property(bool, constant=True)
    def autoScan(self) -> bool:
        """自动扫描"""
        return self.config_manager.get("plugins.auto_scan", True)
    
    @Property(int, constant=True)
    def pluginTimeout(self) -> int:
        """插件超时时间"""
        return self.config_manager.get("plugins.plugin_timeout_seconds", 30)
    
    @Property(list, constant=True)
    def installedPlugins(self) -> List[Dict[str, Any]]:
        """已安装插件列表"""
        return self.config_manager.get("plugins.installed_plugins", [])
    
    # === 镜像源配置属性 ===
    @Property(bool, constant=True)
    def mirrorEnabled(self) -> bool:
        """镜像源是否启用"""
        return self.config_manager.get("mirrors.enabled", True)
    
    @Property(str, constant=True)
    def defaultMirrorSource(self) -> str:
        """默认镜像源"""
        return self.config_manager.get("mirrors.default_source", "tsinghua")
    
    @Property(list, notify=mirrorSourcesChanged)
    def mirrorSources(self) -> List[Dict[str, Any]]:
        """镜像源列表"""
        return self._mirror_sources_cache
    
    @Property(int, constant=True)
    def mirrorTimeout(self) -> int:
        """镜像源超时时间"""
        return self.config_manager.get("mirrors.timeout_seconds", 30)
    
    @Property(int, constant=True)
    def mirrorRetryCount(self) -> int:
        """镜像源重试次数"""
        return self.config_manager.get("mirrors.retry_count", 3)
    
    @Property(bool, constant=True)
    def sslVerify(self) -> bool:
        """SSL验证"""
        return self.config_manager.get("mirrors.verify_ssl", True)
    
    # === 高级配置属性 ===
    @Property(bool, constant=True)
    def debugMode(self) -> bool:
        """调试模式"""
        return self.config_manager.get("advanced.debug_mode", False)
    
    # === 配置操作方法 ===
    @Slot(str, result=bool)
    def setTheme(self, theme: str) -> bool:
        """设置主题"""
        if theme in ["light", "dark", "auto"]:
            return self.config_manager.set_theme(theme)
        return False
    
    @Slot(str, result=bool)
    def setLogLevel(self, level: str) -> bool:
        """设置日志级别"""
        if level in ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]:
            return self.config_manager.set_log_level(level)
        return False
    
    @Slot(int, int, result=bool)
    def setWindowSize(self, width: int, height: int) -> bool:
        """设置窗口大小（已移除，保留接口兼容性）"""
        # 窗口大小配置已移除，此方法保留用于兼容性
        return True
    
    @Slot(bool, result=bool)
    def setMirrorEnabled(self, enabled: bool) -> bool:
        """设置镜像源启用状态"""
        return self.config_manager.set_mirror_enabled(enabled)
    
    @Slot(str, result=bool)
    def setDefaultMirrorSource(self, source_name: str) -> bool:
        """设置默认镜像源"""
        return self.config_manager.set_default_mirror_source(source_name)
    
    @Slot(str, str, int, result=bool)
    def addMirrorSource(self, name: str, url: str, priority: int) -> bool:
        """添加镜像源"""
        result = self.config_manager.add_mirror_source(name, url, priority)
        if result:
            # 更新缓存
            self._mirror_sources_cache = self.config_manager.get("mirrors.sources", [])
            self.mirrorSourceAdded.emit(name, url, priority)
            self.mirrorSourcesChanged.emit()  # 触发镜像源列表变化信号
        return result
    
    @Slot(str, result=bool)
    def removeMirrorSource(self, name: str) -> bool:
        """移除镜像源"""
        result = self.config_manager.remove_mirror_source(name)
        if result:
            # 更新缓存
            self._mirror_sources_cache = self.config_manager.get("mirrors.sources", [])
            self.mirrorSourceRemoved.emit(name)
            self.mirrorSourcesChanged.emit()  # 触发镜像源列表变化信号
        return result
    
    @Slot(str, bool, result=bool)
    def setMirrorSourceEnabled(self, name: str, enabled: bool) -> bool:
        """设置镜像源启用状态"""
        result = self.config_manager.set_mirror_source_enabled(name, enabled)
        if result:
            # 更新缓存
            self._mirror_sources_cache = self.config_manager.get("mirrors.sources", [])
            self.mirrorSourcesChanged.emit()  # 触发镜像源列表变化信号
        return result
    
    @Slot(str, str, int, result=bool)
    def updateMirrorSource(self, name: str, url: str = None, priority: int = None) -> bool:
        """更新镜像源"""
        return self.config_manager.update_mirror_source(name, url, priority)
    
    @Slot(int, result=bool)
    def setMirrorTimeout(self, timeout: int) -> bool:
        """设置镜像源超时时间"""
        return self.config_manager.set_mirror_timeout(timeout)
    
    @Slot(int, result=bool)
    def setMirrorRetryCount(self, count: int) -> bool:
        """设置镜像源重试次数"""
        return self.config_manager.set_mirror_retry_count(count)
    
    @Slot(bool, result=bool)
    def setSslVerify(self, enabled: bool) -> bool:
        """设置SSL验证"""
        return self.config_manager.set_ssl_verify_enabled(enabled)
    
    @Slot('QVariantMap', result=bool)
    def addPlugin(self, plugin_info: Dict[str, Any]) -> bool:
        """添加插件"""
        result = self.config_manager.add_plugin(plugin_info)
        if result:
            self.pluginAdded.emit(plugin_info.get("name", ""))
        return result
    
    @Slot(str, result=bool)
    def removePlugin(self, plugin_name: str) -> bool:
        """移除插件"""
        result = self.config_manager.remove_plugin(plugin_name)
        if result:
            self.pluginRemoved.emit(plugin_name)
        return result
    
    @Slot(bool, result=bool)
    def setDebugMode(self, enabled: bool) -> bool:
        """设置调试模式"""
        return self.config_manager.set_debug_mode(enabled)
    
    @Slot(bool, result=bool)
    def setAutoScan(self, enabled: bool) -> bool:
        """设置自动扫描"""
        return self.config_manager.set("plugins.auto_scan", enabled)
    
    @Slot(int, result=bool)
    def setPluginTimeout(self, timeout: int) -> bool:
        """设置插件超时时间"""
        if 5 <= timeout <= 60:
            return self.config_manager.set("plugins.plugin_timeout_seconds", timeout)
        return False
    
    @Slot(result=bool)
    def saveConfig(self) -> bool:
        """保存配置"""
        return self.config_manager.save_config()
    
    @Slot(result=bool)
    def loadConfig(self) -> bool:
        """重新加载配置"""
        return self.config_manager.load_config()
    
    @Slot(result=bool)
    def resetToDefault(self) -> bool:
        """重置为默认配置"""
        return self.config_manager.reset_to_default()
    
    @Slot(str, result=bool)
    def exportConfig(self, file_path: str) -> bool:
        """导出配置"""
        return self.config_manager.export_config(file_path)
    
    @Slot(str, result=bool)
    def importConfig(self, file_path: str) -> bool:
        """导入配置"""
        return self.config_manager.import_config(file_path)
    
    @Slot(result='QVariantMap')
    def getConfigStats(self) -> Dict[str, Any]:
        """获取配置统计信息"""
        return self.config_manager.get_config_stats()
    
    def auto_save_config(self):
        """自动保存配置"""
        if self.config_manager.has_changes():
            self.config_manager.save_config()
    
    @Slot(str, result=bool)
    def testMirrorConnection(self, url: str) -> bool:
        """测试镜像源连接"""
        try:
            import urllib.request
            import urllib.error
            
            # 构建测试URL
            test_url = url.rstrip('/') + '/simple/'
            
            # 设置超时时间
            timeout = self.mirrorTimeout
            
            # 创建请求
            request = urllib.request.Request(test_url)
            request.add_header('User-Agent', 'Tuleaj Plugin Aggregator/1.0')
            
            # 测试连接
            with urllib.request.urlopen(request, timeout=timeout) as response:
                if response.status == 200:
                    self.logger.info(f"镜像源连接测试成功: {url}")
                    return True
                else:
                    self.logger.warning(f"镜像源连接测试失败: {url}, 状态码: {response.status}")
                    return False
                    
        except urllib.error.URLError as e:
            self.logger.error(f"镜像源连接测试失败: {url}, 错误: {str(e)}")
            return False
        except Exception as e:
            self.logger.error(f"镜像源连接测试异常: {url}, 错误: {str(e)}")
            return False
    
    @Slot(result='QStringList')
    def getMirrorSourceNames(self) -> List[str]:
        """获取镜像源名称列表"""
        sources = self.mirrorSources
        return [source.get("name", "") for source in sources]
    
    @Slot(str, result='QVariantMap')
    def getMirrorSourceByName(self, name: str) -> Optional[Dict[str, Any]]:
        """根据名称获取镜像源信息"""
        sources = self.mirrorSources
        for source in sources:
            if source.get("name") == name:
                return source
        return None
    
    @Slot(result='QVariantList')
    def getEnabledMirrorSources(self) -> List[Dict[str, Any]]:
        """获取启用的镜像源列表（按优先级排序）"""
        sources = self.mirrorSources
        # 过滤启用的镜像源
        enabled_sources = [source for source in sources if source.get("enabled", True)]
        # 按优先级排序
        enabled_sources.sort(key=lambda x: x.get("priority", 999))
        return enabled_sources
    
    @Slot(result=str)
    def getDefaultMirrorUrl(self) -> str:
        """获取默认镜像源的URL"""
        default_source = self.defaultMirrorSource
        sources = self.mirrorSources
        
        # 首先尝试找到默认的镜像源
        for source in sources:
            if source.get("name") == default_source and source.get("enabled", True):
                return source.get("url", "https://pypi.org/simple/")
        
        # 如果默认镜像源不可用，返回第一个启用的镜像源
        for source in sources:
            if source.get("enabled", True):
                return source.get("url", "https://pypi.org/simple/")
        
        # 如果都没有启用的，返回默认URL
        return "https://pypi.org/simple/"
    
    # === Python环境管理方法 ===
    @Slot(str, str, int, result=bool)
    @handle_exceptions(context="创建虚拟环境", show_dialog=False, log_level="ERROR", return_value=False)
    def createEnvironment(self, env_name: str, python_version: str = "3.11", timeout_seconds: int = 60) -> bool:
        """创建虚拟环境"""
        if not env_name or env_name.strip() == "":
            self.configError.emit("环境名称不能为空")
            return False
        
        # 验证环境名称
        if not env_name.replace("_", "").replace("-", "").isalnum():
            self.configError.emit("环境名称只能包含字母、数字、下划线和连字符")
            return False
        
        # 通过信号在工作线程中创建环境
        self.env_worker.createEnvironmentRequested.emit(env_name.strip(), python_version, timeout_seconds)
        return True
    
    @Slot(str, result=bool)
    @handle_exceptions(context="删除虚拟环境", show_dialog=False, log_level="ERROR", return_value=False)
    def deleteEnvironment(self, env_name: str) -> bool:
        """删除虚拟环境"""
        if not env_name:
            self.configError.emit("环境名称不能为空")
            return False
        
        # 检查是否是当前环境
        if env_name == self.currentEnvironmentName:
            self.configError.emit("不能删除当前正在使用的环境")
            return False
        
        # 在工作线程中删除环境
        self.env_worker.delete_environment(env_name)
        return True
    
    @Slot(result=bool)
    def refreshEnvironments(self) -> bool:
        """刷新环境列表"""
        # 首先尝试从配置文件加载已保存的环境信息
        self._load_environments_from_config()
        
        # 然后启动工作线程重新扫描环境
        self.env_worker.refresh_environments()
        return True
    
    @Slot(str, result=bool)
    def switchEnvironment(self, env_name: str) -> bool:
        """切换环境"""
        if not env_name:
            self.configError.emit("环境名称不能为空")
            return False
        
        # 查找环境信息
        env_info = None
        for env in self._environments_cache:
            if env.get("name") == env_name:
                env_info = env
                break
        
        if not env_info:
            self.configError.emit(f"环境 '{env_name}' 不存在")
            return False
        
        # 更新当前环境配置
        self.config_manager.set("environments.current", env_name)
        self.config_manager.set("environments.current_path", env_info.get("path", ""))
        self.config_manager.set("environments.current_python_version", env_info.get("python_version", ""))
        
        # 更新环境列表中的激活状态
        self._update_environment_active_status(env_name)
        
        # 发送信号
        self.currentEnvironmentChanged.emit(env_name)
        
        # 显示成功消息
        self.showSuccessMessage("环境切换成功", f"已切换到环境 '{env_name}'", 3000)
        
        self.logger.info(f"切换到环境: {env_name}")
        return True
    
    @Slot(str, result='QVariantMap')
    def getEnvironmentInfo(self, env_name: str) -> Optional[Dict[str, Any]]:
        """获取环境详细信息"""
        for env in self._environments_cache:
            if env.get("name") == env_name:
                return env
        return None
    
    @Slot(str, result=bool)
    def testEnvironment(self, env_name: str) -> bool:
        """测试环境是否可用"""
        env_info = self.getEnvironmentInfo(env_name)
        if not env_info:
            return False
        
        try:
            env_path = Path(env_info.get("path", ""))
            if not env_path.exists():
                return False
            
            # 获取Python可执行文件路径
            if os.name == 'nt':  # Windows
                python_exe = env_path / "Scripts" / "python.exe"
            else:  # Unix/Linux
                python_exe = env_path / "bin" / "python"
            
            if not python_exe.exists():
                return False
            
            # 测试Python是否可执行
            result = subprocess.run([str(python_exe), "--version"], 
                                  capture_output=True, text=True, timeout=10)
            return result.returncode == 0
            
        except Exception as e:
            self.logger.error(f"测试环境时发生错误: {str(e)}")
            return False
    
    def _update_environments_cache(self, environments: List[Dict[str, Any]]):
        """更新环境列表缓存"""
        self.logger.info(f"更新环境缓存，收到 {len(environments)} 个环境")
        for i, env in enumerate(environments):
            self.logger.info(f"环境 {i+1}: {env}")
        
        self._environments_cache = environments
        
        # 将环境信息保存到配置文件
        self._save_environments_to_config(environments)
        
        # 发送属性变化信号
        self.environmentsListChanged.emit()
    
    def _save_environments_to_config(self, environments: List[Dict[str, Any]]):
        """将环境信息保存到配置文件"""
        try:
            self.logger.info(f"开始保存环境信息到配置文件，共 {len(environments)} 个环境")
            
            # 更新配置文件中的扫描环境信息
            result = self.config_manager.set("environments.scanned_environments", environments)
            self.logger.info(f"设置环境信息到配置管理器: {result}")
            
            # 如果有环境，设置第一个为当前环境（如果没有设置的话）
            if environments and not self.config_manager.get("environments.current"):
                first_env = environments[0]
                self.config_manager.set("environments.current", first_env.get("name", ""))
                self.config_manager.set("environments.current_path", first_env.get("path", ""))
                self.config_manager.set("environments.current_python_version", first_env.get("python_version", ""))
                self.logger.info(f"设置当前环境: {first_env.get('name', '')}")
            
            # 保存配置
            save_result = self.config_manager.save_config()
            self.logger.info(f"保存配置文件结果: {save_result}")
            
            if save_result:
                self.logger.info(f"环境信息已保存到配置文件，共 {len(environments)} 个环境")
            else:
                self.logger.error("保存配置文件失败")
            
        except Exception as e:
            self.logger.error(f"保存环境信息到配置文件失败: {str(e)}")
            import traceback
            self.logger.error(f"详细错误信息: {traceback.format_exc()}")
    
    def _load_environments_from_config(self):
        """从配置文件加载环境信息"""
        try:
            # 从配置文件读取已保存的环境信息
            saved_environments = self.config_manager.get("environments.scanned_environments", [])
            
            if saved_environments:
                self._environments_cache = saved_environments
                self.logger.info(f"从配置文件加载了 {len(saved_environments)} 个环境信息")
                
                # 更新当前环境的激活状态
                current_env = self.config_manager.get("environments.current", "")
                if current_env:
                    self._update_environment_active_status(current_env)
                
                # 发送属性变化信号，通知前端更新
                self.environmentsListChanged.emit()
            else:
                self.logger.info("配置文件中没有保存的环境信息")
                
        except Exception as e:
            self.logger.error(f"从配置文件加载环境信息失败: {str(e)}")
            import traceback
            self.logger.error(f"详细错误信息: {traceback.format_exc()}")
    
    def _update_environment_active_status(self, active_env_name: str):
        """更新环境列表中的激活状态"""
        try:
            # 更新缓存中的激活状态
            for env in self._environments_cache:
                env["is_active"] = (env.get("name") == active_env_name)
            
            # 保存到配置文件
            self.config_manager.set("environments.scanned_environments", self._environments_cache)
            self.config_manager.save_config()
            
            # 发送信号通知前端更新
            self.environmentsListChanged.emit()
            self.currentEnvironmentChanged.emit(active_env_name)
            
            self.logger.info(f"更新环境激活状态: {active_env_name}")
            
        except Exception as e:
            self.logger.error(f"更新环境激活状态失败: {str(e)}")
    
    # === uv特有的环境管理方法 ===
    @Slot(str, str, result=bool)
    @handle_exceptions(context="安装包", show_dialog=False, log_level="ERROR", return_value=False)
    def installPackage(self, env_name: str, package_name: str) -> bool:
        """使用uv在指定环境中安装包"""
        env_info = self.getEnvironmentInfo(env_name)
        if not env_info:
            self.configError.emit(f"环境 '{env_name}' 不存在")
            return False
        
        env_path = Path(env_info.get("path", ""))
        if not env_path.exists():
            self.configError.emit(f"环境路径不存在: {env_path}")
            return False
        
        # 构建uv安装命令
        cmd = ["uv", "pip", "install", package_name, "--python", str(env_path / ("Scripts" if os.name == 'nt' else "bin") / "python.exe")]
        
        # 如果启用了镜像源，添加镜像源参数
        if self.mirrorEnabled:
            mirror_url = self.getDefaultMirrorUrl()
            cmd.extend(["--index-url", mirror_url])
            self.logger.info(f"使用镜像源安装包: {mirror_url}")
        
        subprocess.run(cmd, check=True, capture_output=True, text=True, encoding='utf-8', errors='replace')
        
        self.logger.info(f"在环境 {env_name} 中成功安装包: {package_name}")
        return True
    
    @Slot(str, str, result=bool)
    @handle_exceptions(context="卸载包", show_dialog=False, log_level="ERROR", return_value=False)
    def uninstallPackage(self, env_name: str, package_name: str) -> bool:
        """使用uv在指定环境中卸载包"""
        env_info = self.getEnvironmentInfo(env_name)
        if not env_info:
            self.configError.emit(f"环境 '{env_name}' 不存在")
            return False
        
        env_path = Path(env_info.get("path", ""))
        if not env_path.exists():
            self.configError.emit(f"环境路径不存在: {env_path}")
            return False
        
        # 使用uv卸载包
        cmd = ["uv", "pip", "uninstall", package_name, "--python", str(env_path / ("Scripts" if os.name == 'nt' else "bin") / "python.exe")]
        subprocess.run(cmd, check=True, capture_output=True, text=True, encoding='utf-8', errors='replace')
        
        self.logger.info(f"在环境 {env_name} 中成功卸载包: {package_name}")
        return True
    
    @Slot(str, result='QVariantList')
    @silent_exceptions(return_value=[])
    def getEnvironmentPackages(self, env_name: str) -> List[Dict[str, Any]]:
        """获取环境中已安装的包列表"""
        env_info = self.getEnvironmentInfo(env_name)
        if not env_info:
            return []
        
        env_path = Path(env_info.get("path", ""))
        if not env_path.exists():
            return []
        
        python_exe = env_path / ("Scripts" if os.name == 'nt' else "bin") / "python.exe"
        
        # 使用uv获取包列表
        cmd = ["uv", "pip", "list", "--python", str(python_exe)]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True, encoding='utf-8', errors='replace')
        
        packages = []
        lines = result.stdout.strip().split('\n')
        for line in lines[2:]:  # 跳过标题行
            if line.strip():
                parts = line.split()
                if len(parts) >= 2:
                    packages.append({
                        "name": parts[0],
                        "version": parts[1]
                    })
        
        return packages
    
    @Slot(str, result=bool)
    @handle_exceptions(context="同步环境依赖", show_dialog=False, log_level="ERROR", return_value=False)
    def syncEnvironment(self, env_name: str) -> bool:
        """使用uv同步环境依赖"""
        env_info = self.getEnvironmentInfo(env_name)
        if not env_info:
            self.configError.emit(f"环境 '{env_name}' 不存在")
            return False
        
        env_path = Path(env_info.get("path", ""))
        if not env_path.exists():
            self.configError.emit(f"环境路径不存在: {env_path}")
            return False
        
        # 构建uv同步命令
        cmd = ["uv", "sync", "--python", str(env_path / ("Scripts" if os.name == 'nt' else "bin") / "python.exe")]
        
        # 如果启用了镜像源，添加镜像源参数
        if self.mirrorEnabled:
            mirror_url = self.getDefaultMirrorUrl()
            cmd.extend(["--index-url", mirror_url])
            self.logger.info(f"使用镜像源同步环境: {mirror_url}")
        
        subprocess.run(cmd, check=True, capture_output=True, text=True, encoding='utf-8', errors='replace')
        
        self.logger.info(f"成功同步环境 {env_name} 的依赖")
        return True
    
    # === 统一消息提示方法 ===
    @Slot(str, str, str, int)
    def showMessage(self, message_type: str, title: str, content: str, duration: int = 3000):
        """显示消息提示"""
        self.showMessageSignal.emit(message_type, title, content, duration)
    
    @Slot(str, str, int)
    def showSuccessMessage(self, title: str, content: str, duration: int = 3000):
        """显示成功消息"""
        self.showMessageSignal.emit("success", title, content, duration)
    
    @Slot(str, str, int)
    def showErrorMessage(self, title: str, content: str, duration: int = 5000):
        """显示错误消息"""
        self.showMessageSignal.emit("error", title, content, duration)
    
    @Slot(str, str, int)
    def showWarningMessage(self, title: str, content: str, duration: int = 4000):
        """显示警告消息"""
        self.showMessageSignal.emit("warning", title, content, duration)
    
    @Slot(str, str, int)
    def showInfoMessage(self, title: str, content: str, duration: int = 3000):
        """显示信息消息"""
        self.showMessageSignal.emit("info", title, content, duration)
    
    # === 环境操作消息处理 ===
    def _on_environment_created(self, env_name: str, success: bool, message: str):
        """处理环境创建结果"""
        self.environmentCreated.emit(env_name, success, message)
        
        if success:
            self.showSuccessMessage("环境创建成功", f"虚拟环境 '{env_name}' 创建成功", 3000)
        else:
            self.showErrorMessage("环境创建失败", message or f"创建环境 '{env_name}' 时发生错误", 5000)
    
    def _on_environment_deleted(self, env_name: str, success: bool, message: str):
        """处理环境删除结果"""
        self.environmentDeleted.emit(env_name, success, message)
        
        if success:
            self.showSuccessMessage("环境删除成功", f"虚拟环境 '{env_name}' 删除成功", 3000)
        else:
            self.showErrorMessage("环境删除失败", message or f"删除环境 '{env_name}' 时发生错误", 5000)


# 注册QML类型
def register_qml_types():
    """注册QML类型"""
    qmlRegisterType(ConfigBridge, "ConfigBridge", 1, 0, "ConfigBridge")


