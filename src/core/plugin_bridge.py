#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
插件桥接器
用于读取和管理插件信息
"""

import toml
from pathlib import Path
from typing import Dict, List, Optional, Any
from PySide6.QtCore import QObject, Signal, QThread, Slot
from PySide6.QtQml import qmlRegisterType

# 导入依赖管理器
from core.dependency_manager import DependencyManager
# 导入插件进程管理器
from core.plugin_process_manager import PluginProcessManager
# 导入日志管理器
from utils.logger import Logger
# 导入异常处理器
from utils.exception_handler import ExceptionHandler, handle_exceptions


class PluginInfo:
    """插件信息类"""
    
    def __init__(self, plugin_data: Dict[str, Any]):
        self.name = plugin_data.get('name', '')
        self.version = plugin_data.get('version', '1.0.0')
        self.author = plugin_data.get('author', '')
        self.icon = plugin_data.get('icon', '📦')
        self.entry_point = plugin_data.get('entry_point', 'main.py')
        self.path = plugin_data.get('path', '')
        self.status = plugin_data.get('status', 'stopped')
        self.description = plugin_data.get('description', '')


class PluginScanner(QThread):
    """插件扫描线程"""
    
    pluginsScanned = Signal(list)  # 扫描完成的信号
    
    def __init__(self, plugins_dir: str, parent=None):
        super().__init__(parent)
        self.plugins_dir = Path(plugins_dir)
        self.plugins_info = []
        
        # 初始化日志管理器
        self.logger = Logger(log_level="INFO", log_dir="logs")
    
    def run(self):
        """扫描插件目录"""
        self.plugins_info = []
        
        if not self.plugins_dir.exists():
            self.logger.warning(f"插件目录不存在: {self.plugins_dir}")
            self.pluginsScanned.emit([])
            return
        
        for plugin_dir in self.plugins_dir.iterdir():
            if plugin_dir.is_dir():
                plugin_info = self._read_plugin_info(plugin_dir)
                if plugin_info:
                    self.plugins_info.append(plugin_info)
        
        self.logger.info(f"扫描到 {len(self.plugins_info)} 个插件")
        self.pluginsScanned.emit(self.plugins_info)
    
    def _read_plugin_info(self, plugin_dir: Path) -> Optional[Dict[str, Any]]:
        """读取单个插件的配置信息"""
        pyproject_file = plugin_dir / "pyproject.toml"
        
        if not pyproject_file.exists():
            self.logger.warning(f"插件 {plugin_dir.name} 缺少 pyproject.toml 文件")
            return None
        
        try:
            with open(pyproject_file, 'r', encoding='utf-8') as f:
                data = toml.load(f)
            
            # 提取插件元数据
            plugin_metadata = data.get('plugin-metadata', {})
            if not plugin_metadata:
                self.logger.warning(f"插件 {plugin_dir.name} 缺少 plugin-metadata 配置")
                return None
            
            plugin_info = {
                'name': plugin_metadata.get('name', plugin_dir.name),
                'version': plugin_metadata.get('version', '1.0.0'),
                'author': plugin_metadata.get('author', ''),
                'icon': plugin_metadata.get('icon', '📦'),
                'entry_point': plugin_metadata.get('entry_point', 'main.py'),
                'path': str(plugin_dir),
                'status': 'stopped',  # 默认状态
                'description': data.get('project', {}).get('description', '')
            }
            
            return plugin_info
            
        except Exception as e:
            self.logger.error(f"读取插件 {plugin_dir.name} 配置失败: {e}")
            return None


class PluginBridge(QObject):
    """插件桥接器 - 连接Python后端和QML前端"""
    
    # 信号定义
    pluginsLoaded = Signal(list)  # 插件列表加载完成
    pluginStatusChanged = Signal(str, str)  # 插件状态变化 (name, status)
    pluginError = Signal(str, str)  # 插件错误 (name, error)
    dependencyInstalling = Signal(str, str)  # 依赖安装中 (plugin_name, package_name)
    dependencyInstalled = Signal(str, str, bool, str)  # 依赖安装完成 (env_name, package_name, success, message)
    dependencySyncStarted = Signal(str)  # 依赖同步开始 (env_name)
    dependencySyncCompleted = Signal(str, bool, str)  # 依赖同步完成 (env_name, success, message)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.plugins_info = []
        self.plugin_scanner = None
        self.plugins_dir = "plugins"
        
        # 初始化日志管理器
        self.logger = Logger(log_level="INFO", log_dir="logs")
        
        # 初始化异常处理器
        self.exception_handler = ExceptionHandler(self.logger)
        
        # 初始化进程管理器
        self.process_manager = PluginProcessManager(self)
        
        # 连接进程管理器信号
        self.process_manager.processStarted.connect(self._on_plugin_process_started)
        self.process_manager.processFinished.connect(self._on_plugin_process_finished)
        self.process_manager.processError.connect(self._on_plugin_process_error)
        self.process_manager.processOutput.connect(self._on_plugin_process_output)
        
        # 初始化依赖管理器
        self.dependency_manager = DependencyManager(self)
        
        # 连接依赖管理器信号
        self.dependency_manager.dependencyInstalled.connect(self.dependencyInstalled.emit)
        self.dependency_manager.dependencyConflictResolved.connect(self._on_dependency_conflict_resolved)
        self.dependency_manager.environmentUpdated.connect(self._on_environment_updated)
        self.dependency_manager.dependencySyncStarted.connect(self.dependencySyncStarted.emit)
        self.dependency_manager.dependencySyncCompleted.connect(self.dependencySyncCompleted.emit)
        
        # 启动插件扫描
        self.scan_plugins()
    
    def scan_plugins(self):
        """扫描插件目录"""
        self.logger.info("开始扫描插件...")
        
        if self.plugin_scanner and self.plugin_scanner.isRunning():
            self.plugin_scanner.quit()
            self.plugin_scanner.wait()
        
        self.plugin_scanner = PluginScanner(self.plugins_dir)
        self.plugin_scanner.pluginsScanned.connect(self._on_plugins_scanned)
        self.plugin_scanner.start()
    
    def _on_plugins_scanned(self, plugins_info: List[Dict[str, Any]]):
        """插件扫描完成回调"""
        self.plugins_info = plugins_info
        self.logger.info(f"插件扫描完成，共 {len(plugins_info)} 个插件")
        
        # 发射信号给QML
        self.pluginsLoaded.emit(plugins_info)
    
    def get_plugins(self) -> List[Dict[str, Any]]:
        """获取插件列表"""
        return self.plugins_info.copy()
    
    def get_plugin_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """根据名称获取插件信息"""
        for plugin in self.plugins_info:
            if plugin['name'] == name:
                return plugin
        return None
    
    @Slot(str, result=bool)
    @handle_exceptions("启动插件", show_dialog=False, log_level="ERROR", return_value=False)
    def start_plugin(self, plugin_name: str) -> bool:
        """启动插件（集成依赖管理和uv sync）"""
        plugin = self.get_plugin_by_name(plugin_name)
        if not plugin:
            self.pluginError.emit(plugin_name, "插件不存在")
            return False
        
        # 检查插件是否已经在运行
        if self.process_manager.is_plugin_running(plugin_name):
            self.pluginError.emit(plugin_name, "插件已经在运行中")
            return False
        
        try:
            plugin_path = Path(plugin['path'])
            entry_point = plugin['entry_point']
            
            # 构建插件启动命令
            if entry_point.endswith('.py'):
                # Python 插件
                main_file = plugin_path / entry_point
                if not main_file.exists():
                    self.pluginError.emit(plugin_name, f"插件入口文件不存在: {main_file}")
                    return False
                
                # 获取当前环境名称
                current_env_name = self._get_current_environment()
                self.logger.info(f"使用当前环境: {current_env_name}")
                
                # 步骤1：懒加载安装依赖（集成uv sync）
                self.logger.info("开始依赖管理和同步...")
                self.dependencyInstalling.emit(plugin_name, "正在管理依赖...")
                
                # 读取插件依赖
                plugin_deps = self.dependency_manager.read_plugin_dependencies(plugin_path)
                if plugin_deps:
                    self.logger.info(f"发现插件 {plugin_name} 的依赖: {[str(dep) for dep in plugin_deps]}")
                    
                    # 解决依赖冲突
                    resolved_deps = self.dependency_manager.resolve_dependencies(current_env_name)
                    self.logger.info(f"协商后的依赖: {resolved_deps}")
                    
                    # 使用 uv sync 同步依赖
                    sync_success = self.dependency_manager.sync_dependencies_with_uv(current_env_name, resolved_deps)
                    
                    if not sync_success:
                        self.pluginError.emit(plugin_name, "依赖同步失败")
                        return False
                    
                        self.logger.info("依赖同步成功")
                else:
                    self.logger.info(f"插件 {plugin_name} 没有依赖")
                
                # 步骤2：启动插件进程
                self.logger.info(f"启动插件 {plugin_name}...")
                
                # 直接使用环境中的 Python 运行插件
                python_path = self.dependency_manager.get_environment_python_path(current_env_name)
                
                if not python_path.exists():
                    self.pluginError.emit(plugin_name, f"环境 {current_env_name} 不存在")
                    return False
                
                # 准备环境变量
                env_vars = {
                    "VIRTUAL_ENV": str(python_path.parent.parent),
                    "PLUGIN_NAME": plugin_name,
                    "PLUGIN_PATH": str(plugin_path)
                }
                
                self.logger.info(f"启动插件 {plugin_name}:")
                self.logger.info(f"  Python路径: {python_path}")
                self.logger.info(f"  脚本文件: {main_file}")
                self.logger.info(f"  工作目录: {plugin_path}")
                self.logger.info(f"  环境: {current_env_name}")
                
                # 使用进程管理器启动插件
                success = self.process_manager.start_plugin(
                    plugin_name=plugin_name,
                    python_path=str(python_path),
                    script_path=entry_point,
                    working_dir=str(plugin_path),
                    env_vars=env_vars
                )
                
                if success:
                    # 进程管理器会通过信号自动更新状态，不需要手动更新
                    return True
                else:
                    return False
            else:
                self.pluginError.emit(plugin_name, f"不支持的插件类型: {entry_point}")
                return False
                
        except Exception as e:
            self.pluginError.emit(plugin_name, f"启动插件时发生错误: {str(e)}")
            return False
    
    @Slot(str, result=bool)
    @handle_exceptions("停止插件", show_dialog=False, log_level="ERROR", return_value=False)
    def stop_plugin(self, plugin_name: str) -> bool:
        """停止插件"""
        try:
            if not self.process_manager.is_plugin_running(plugin_name):
                self.logger.warning(f"插件 {plugin_name} 不在运行中")
                return False
            
            # 使用进程管理器停止插件
            success = self.process_manager.stop_plugin(plugin_name)
            
            if success:
                # 更新状态
                self._update_plugin_status(plugin_name, "stopped")
                return True
            else:
                return False
                
        except Exception as e:
            self.pluginError.emit(plugin_name, f"停止插件时发生错误: {str(e)}")
            return False
    
    @Slot(str, result=bool)
    @handle_exceptions("卸载插件", show_dialog=False, log_level="ERROR", return_value=False)
    def uninstall_plugin(self, plugin_name: str) -> bool:
        """卸载插件"""
        plugin = self.get_plugin_by_name(plugin_name)
        if not plugin:
            self.pluginError.emit(plugin_name, "插件不存在")
            return False
        
        try:
            # 步骤1：如果插件正在运行，先停止它
            if plugin_name in self.running_processes:
                self.logger.info(f"插件 {plugin_name} 正在运行，先停止它...")
                if not self.stop_plugin(plugin_name):
                    self.pluginError.emit(plugin_name, "无法停止正在运行的插件")
                    return False
            
            plugin_path = Path(plugin['path'])
            
            # 步骤2：检查插件目录是否存在
            if not plugin_path.exists():
                self.logger.error(f"插件目录不存在: {plugin_path}")
                # 即使目录不存在，也要从列表中移除
                self.plugins_info = [p for p in self.plugins_info if p['name'] != plugin_name]
                self.pluginsLoaded.emit(self.plugins_info)
                self.logger.info(f"插件 {plugin_name} 已从列表中移除")
                return True
            
            # 步骤3：删除插件目录
            self.logger.info(f"删除插件目录: {plugin_path}")
            
            # 在Windows上，需要特殊处理
            import shutil
            try:
                shutil.rmtree(plugin_path)
                self.logger.info(f"插件目录 {plugin_path} 删除成功")
            except Exception as e:
                self.logger.error(f"删除插件目录失败: {e}")
                # 尝试使用系统命令删除
                import subprocess
                try:
                    subprocess.run(['rmdir', '/s', '/q', str(plugin_path)], 
                                 shell=True, check=True, capture_output=True)
                    self.logger.info("使用系统命令删除插件目录成功")
                except subprocess.CalledProcessError as e:
                    self.pluginError.emit(plugin_name, f"删除插件目录失败: {e}")
                    return False
            
            # 步骤4：从插件列表中移除
            self.plugins_info = [p for p in self.plugins_info if p['name'] != plugin_name]
            
            # 步骤5：更新插件列表
            self.pluginsLoaded.emit(self.plugins_info)
            
            self.logger.info(f"插件 {plugin_name} 卸载完成")
            return True
            
        except Exception as e:
            self.pluginError.emit(plugin_name, f"卸载插件时发生错误: {str(e)}")
            return False
    
    def _on_plugin_process_started(self, plugin_name: str):
        """插件进程启动成功回调"""
        self.logger.info(f"插件 {plugin_name} 进程启动成功")
        self._update_plugin_status(plugin_name, "running")
    
    def _on_plugin_process_finished(self, plugin_name: str, exit_code: int, exit_status: int):
        """插件进程结束回调"""
        self.logger.info(f"插件 {plugin_name} 进程结束，退出码: {exit_code}, 状态: {exit_status}")
        
        # 智能判断退出状态
        is_normal_exit = self._is_normal_exit(exit_code, exit_status)
        
        # 更新状态
        if is_normal_exit:
            self._update_plugin_status(plugin_name, "stopped")
        else:
            self._update_plugin_status(plugin_name, "error")
            self.pluginError.emit(plugin_name, f"插件异常退出，退出码: {exit_code}")
    
    def _is_normal_exit(self, exit_code: int, exit_status: int) -> bool:
        """判断是否为正常退出"""
        # 导入QProcess以使用ExitStatus枚举
        from PySide6.QtCore import QProcess
        
        self.logger.info(f"判断退出状态: 退出码={exit_code}, 退出状态={exit_status}")
        
        # 检查退出状态
        if exit_status == QProcess.ExitStatus.NormalExit:
            self.logger.info("正常退出状态: NormalExit")
            return True
        
        # 检查退出码
        # 0 通常表示正常退出
        if exit_code == 0:
            self.logger.info("正常退出码: 0")
            return True
        
        # Windows系统中的一些常见正常退出码
        # 62097 (0xF1F1) 在某些情况下是正常的
        # 1 通常表示正常退出但有警告
        if exit_code in [1, 62097]:
            self.logger.info(f"Windows正常退出码: {exit_code}")
            return True
        
        # 其他非零退出码通常表示异常
        self.logger.warning(f"异常退出: 退出码={exit_code}, 退出状态={exit_status}")
        return False
    
    def _on_plugin_process_error(self, plugin_name: str, error_message: str):
        """插件进程错误回调"""
        self.logger.error(f"插件 {plugin_name} 进程错误: {error_message}")
        self._update_plugin_status(plugin_name, "error")
        self.pluginError.emit(plugin_name, error_message)
    
    def _on_plugin_process_output(self, plugin_name: str, output_type: str, output: str):
        """插件进程输出回调"""
        if output.strip():
            self.logger.debug(f"插件 {plugin_name} {output_type}: {output.strip()}")
    
    def _update_plugin_status(self, plugin_name: str, status: str):
        """更新插件状态"""
        self.logger.info(f"更新插件状态: {plugin_name} -> {status}")
        
        # 查找并更新插件状态
        plugin_found = False
        for plugin in self.plugins_info:
            if plugin['name'] == plugin_name:
                old_status = plugin['status']
                plugin['status'] = status
                plugin_found = True
                self.logger.info(f"插件 {plugin_name} 状态从 {old_status} 更新为 {status}")
                break
        
        if not plugin_found:
            self.logger.warning(f"警告: 未找到插件 {plugin_name}，无法更新状态")
            return
        
        # 发射状态变化信号
        self.logger.info(f"发射状态变化信号: {plugin_name} -> {status}")
        self.pluginStatusChanged.emit(plugin_name, status)
    
    def _get_current_environment(self) -> str:
        """获取当前环境路径"""
        try:
            # 尝试从配置管理器获取当前环境
            from core.config_manager import ConfigManager
            config_manager = ConfigManager("config.toml")
            config_manager.load_config()  # 确保加载配置
            
            # 优先获取当前环境的完整路径
            current_path = config_manager.get("environments.current_path", "")
            self.logger.info(f"从配置读取的当前环境路径: '{current_path}'")
            
            if current_path:
                self.logger.info(f"使用配置中的当前环境路径: {current_path}")
                return current_path
            
            # 如果没有路径，尝试从环境名称构建路径
            current_env = config_manager.get("environments.current", "")
            self.logger.info(f"从配置读取的当前环境名称: '{current_env}'")
            
            if current_env:
                # 构建环境路径
                from pathlib import Path
                project_root = Path(__file__).parent.parent.parent
                env_path = project_root / "envs" / current_env
                self.logger.info(f"构建的环境路径: {env_path}")
                return str(env_path)
            else:
                # 如果没有配置当前环境，使用默认环境
                from pathlib import Path
                project_root = Path(__file__).parent.parent.parent
                default_env_path = project_root / "envs" / "tuleaj-plugin-aggregator"
                self.logger.info(f"使用默认环境路径: {default_env_path}")
                return str(default_env_path)
                
        except Exception as e:
            self.logger.error(f"获取当前环境失败: {str(e)}")
            from pathlib import Path
            project_root = Path(__file__).parent.parent.parent
            return str(project_root / "envs" / "tuleaj-plugin-aggregator")
    
    def _get_mirror_url(self) -> str:
        """获取镜像源URL"""
        try:
            # 尝试从配置管理器获取镜像源
            from core.config_manager import ConfigManager
            config_manager = ConfigManager("config.toml")
            config_manager.load_config()  # 确保加载配置
            
            # 检查是否启用了镜像源
            mirror_enabled = config_manager.get("mirrors.enabled", False)
            self.logger.info(f"镜像源启用状态: {mirror_enabled}")
            
            if not mirror_enabled:
                self.logger.info("镜像源未启用")
                return ""
            
            # 获取启用的镜像源列表
            mirror_sources = config_manager.get("mirrors.sources", [])
            self.logger.info(f"镜像源列表: {mirror_sources}")
            
            enabled_sources = [source for source in mirror_sources if source.get("enabled", False)]
            self.logger.info(f"启用的镜像源: {enabled_sources}")
            
            if enabled_sources:
                # 按优先级排序，选择优先级最高的
                enabled_sources.sort(key=lambda x: x.get("priority", 999))
                mirror_url = enabled_sources[0].get("url", "")
                self.logger.info(f"使用镜像源: {mirror_url}")
                return mirror_url
            else:
                self.logger.info("没有启用的镜像源")
                return ""
                
        except Exception as e:
            self.logger.error(f"获取镜像源失败: {str(e)}")
            return ""
    
    @Slot()
    def refresh_plugins(self):
        """刷新插件列表"""
        self.scan_plugins()
    
    def _on_dependency_conflict_resolved(self, package_name: str, original_versions: str, resolved_version: str):
        """处理依赖冲突解决"""
        self.logger.info(f"依赖冲突解决: {package_name}")
        self.logger.info(f"  原始版本: {original_versions}")
        self.logger.info(f"  协商版本: {resolved_version}")
    
    def _on_environment_updated(self, env_name: str):
        """处理环境更新"""
        self.logger.info(f"环境 {env_name} 已更新")
    
    @Slot(str, result='QVariantList')
    @handle_exceptions("获取插件依赖", show_dialog=False, log_level="ERROR", return_value=[])
    def get_plugin_dependencies(self, plugin_name: str) -> List[Dict[str, Any]]:
        """获取插件的依赖信息"""
        try:
            plugin_path = Path(self.plugins_dir) / plugin_name
            if not plugin_path.exists():
                return []
            
            dependencies = self.dependency_manager.read_plugin_dependencies(plugin_path)
            return [
                {
                    "name": dep.name,
                    "version_spec": dep.version_spec,
                    "source": dep.source
                }
                for dep in dependencies
            ]
        except Exception as e:
            self.logger.error(f"获取插件 {plugin_name} 依赖信息失败: {e}")
            return []
    
    @Slot(str, result='QVariantMap')
    @handle_exceptions("获取环境依赖", show_dialog=False, log_level="ERROR", return_value={})
    def get_environment_dependencies(self, env_name: str) -> Dict[str, str]:
        """获取环境中已安装的依赖"""
        try:
            return self.dependency_manager.get_environment_dependencies(env_name)
        except Exception as e:
            self.logger.error(f"获取环境 {env_name} 依赖信息失败: {e}")
            return {}
    
    @Slot(str, result=bool)
    @handle_exceptions("安装插件依赖", show_dialog=False, log_level="ERROR", return_value=False)
    def install_plugin_dependencies(self, plugin_name: str) -> bool:
        """手动安装插件依赖"""
        try:
            current_env_name = self._get_current_environment()
            return self.dependency_manager.install_dependencies_lazy(current_env_name, plugin_name)
        except Exception as e:
            self.logger.error(f"安装插件 {plugin_name} 依赖失败: {e}")
            return False


# 注册 QML 类型
def register_types():
    """注册 QML 类型"""
    qmlRegisterType(PluginBridge, "PluginBridge", 1, 0, "PluginBridge")


if __name__ == "__main__":
    # 测试代码
    import sys
    from PySide6.QtCore import QCoreApplication
    
    app = QCoreApplication(sys.argv)
    
    bridge = PluginBridge()
    
    # 连接信号
    bridge.pluginsLoaded.connect(lambda plugins: print(f"加载了 {len(plugins)} 个插件"))
    bridge.pluginStatusChanged.connect(lambda name, status: print(f"插件 {name} 状态变为: {status}"))
    bridge.pluginError.connect(lambda name, error: print(f"插件 {name} 错误: {error}"))
    
    print("插件桥接器测试")
    print("按 Ctrl+C 退出")
    
    try:
        app.exec()
    except KeyboardInterrupt:
        print("\n退出测试")
