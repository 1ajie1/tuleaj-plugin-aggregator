"""
配置管理器
负责管理应用程序的配置文件，包括加载、保存、验证配置项等功能
使用装饰器异常管理
"""

import toml
from pathlib import Path
from typing import Dict, Any, Optional, List
from PySide6.QtCore import QObject, Signal

# 导入异常管理装饰器
from utils.exception_handler import (
    handle_exceptions as config_handle_exceptions,
    silent_exceptions
)


class ConfigManager(QObject):
    """配置管理器"""
    
    # 信号定义
    config_loaded = Signal()           # 配置加载完成
    config_saved = Signal()             # 配置保存完成
    config_changed = Signal(str, Any)   # 配置项变化 (键, 值)
    config_error = Signal(str)          # 配置错误 (错误信息)
    
    def __init__(self, config_file: str = "config.toml"):
        super().__init__()
        self.config_file = Path(config_file)
        self.config = {}
        self.default_config = self._get_default_config()
        self._backup_config = None
        
    def _get_default_config(self) -> Dict[str, Any]:
        """获取默认配置"""
        return {
            "app": {
                "name": "Tuleaj Plugin Aggregator",
                "version": "1.0.0",
                "description": "PySide6 QML 插件聚合工具",
                "author": "Tuleaj"
            },
            "ui": {
                "theme": "light",
                "language": "zh_CN",
                "window_width": 1200,
                "window_height": 800,
                "window_maximized": False,
                "remember_window_state": True
            },
            "environments": {
                "default": "python3.11",
                "available": ["python3.11", "python3.12"]
            },
            "plugins": {
                "directory": "plugins",
                "auto_scan": True,
                "plugin_timeout_seconds": 30,
                "installed_plugins": []
            },
            "mirrors": {
                "enabled": True,
                "default_source": "pypi",
                "sources": [
                    {"name": "pypi", "url": "https://pypi.org/simple/", "priority": 1},
                    {"name": "tsinghua", "url": "https://pypi.tuna.tsinghua.edu.cn/simple/", "priority": 2},
                    {"name": "aliyun", "url": "https://mirrors.aliyun.com/pypi/simple/", "priority": 3},
                    {"name": "douban", "url": "https://pypi.douban.com/simple/", "priority": 4},
                    {"name": "ustc", "url": "https://pypi.mirrors.ustc.edu.cn/simple/", "priority": 5}
                ],
                "timeout_seconds": 30,
                "retry_count": 3,
                "verify_ssl": True
            },
            "logging": {
                "enable_file_logging": True,
                "enable_console_logging": True,
                "log_format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                "date_format": "%Y-%m-%d %H:%M:%S",
                "enable_plugin_logs": True,
                "plugin_log_dir": "logs/plugins",
                "log_level": "INFO",
                "log_dir": "logs",
                "max_log_files": 10,
                "log_file_size_mb": 10
            },
            "advanced": {
                "debug_mode": False,
                "enable_metrics": True,
                "metrics_retention_days": 30,
                "enable_telemetry": False
            }
        }
    
    @config_handle_exceptions(context="配置加载", show_dialog=False, log_level="ERROR", return_value=False)
    def load_config(self) -> bool:
        """加载配置文件"""
        if self.config_file.exists():
            with open(self.config_file, 'r', encoding='utf-8') as f:
                loaded_config = toml.load(f)
                # 合并默认配置和加载的配置
                self.config = self._merge_configs(self.default_config, loaded_config)
        else:
            self.config = self.default_config.copy()
            self.save_config()
        
        # 验证配置
        if not self._validate_config():
            self.config_error.emit("配置文件验证失败")
            return False
        
        # 创建备份
        self._backup_config = self.config.copy()
        
        self.config_loaded.emit()
        return True
    
    @config_handle_exceptions(context="配置保存", show_dialog=False, log_level="ERROR", return_value=False)
    def save_config(self) -> bool:
        """保存配置文件"""
        # 确保配置目录存在
        self.config_file.parent.mkdir(parents=True, exist_ok=True)
        
        # 验证配置
        if not self._validate_config():
            self.config_error.emit("配置验证失败，无法保存")
            return False
        
        # 创建备份
        if self.config_file.exists():
            backup_file = self.config_file.with_suffix('.toml.backup')
            with open(self.config_file, 'r', encoding='utf-8') as src:
                with open(backup_file, 'w', encoding='utf-8') as dst:
                    dst.write(src.read())
        
        # 保存配置
        with open(self.config_file, 'w', encoding='utf-8') as f:
            toml.dump(self.config, f)
        
        # 更新备份
        self._backup_config = self.config.copy()
        
        self.config_saved.emit()
        return True
    
    @silent_exceptions(return_value=None)
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
    
    @config_handle_exceptions(context="设置配置", show_dialog=False, log_level="WARNING", return_value=False)
    def set(self, key: str, value: Any) -> bool:
        """设置配置值"""
        keys = key.split('.')
        config = self.config
        
        # 导航到目标位置
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        # 设置值
        old_value = config.get(keys[-1])
        config[keys[-1]] = value
        
        # 发送变化信号
        if old_value != value:
            self.config_changed.emit(key, value)
        
        return True
    
    @config_handle_exceptions(context="重置配置", show_dialog=False, log_level="INFO", return_value=False)
    def reset_to_default(self) -> bool:
        """重置为默认配置"""
        self.config = self.default_config.copy()
        self.config_changed.emit("config", "reset")
        return True
    
    @config_handle_exceptions(context="恢复备份", show_dialog=False, log_level="WARNING", return_value=False)
    def restore_backup(self) -> bool:
        """恢复备份配置"""
        if self._backup_config:
            self.config = self._backup_config.copy()
            self.config_changed.emit("config", "restored")
            return True
        else:
            self.config_error.emit("没有可用的备份配置")
            return False
    
    def has_changes(self) -> bool:
        """检查是否有未保存的更改"""
        return self.config != self._backup_config
    
    def _merge_configs(self, default: Dict[str, Any], loaded: Dict[str, Any]) -> Dict[str, Any]:
        """合并配置"""
        result = default.copy()
        
        for key, value in loaded.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._merge_configs(result[key], value)
            else:
                result[key] = value
        
        return result
    
    def _validate_config(self) -> bool:
        """验证配置"""
        try:
            # 验证应用配置
            app_config = self.config.get("app", {})
            if not isinstance(app_config.get("name"), str):
                return False
            
            # 验证日志级别
            log_level = app_config.get("log_level", "INFO")
            if log_level not in ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]:
                return False
            
            # 验证环境配置
            env_config = self.config.get("environments", {})
            if not isinstance(env_config.get("available"), list):
                return False
            
            # 验证镜像源配置
            mirror_config = self.config.get("mirrors", {})
            if not isinstance(mirror_config.get("sources"), list):
                return False
            
            for source in mirror_config.get("sources", []):
                if not all(key in source for key in ["name", "url", "priority"]):
                    return False
                if not isinstance(source["priority"], int) or source["priority"] < 1:
                    return False
            
            # 验证插件配置
            plugin_config = self.config.get("plugins", {})
            if not isinstance(plugin_config.get("installed_plugins"), list):
                return False
            
            return True
            
        except Exception:
            return False
    
    # 镜像源管理方法
    def get_mirror_sources(self) -> List[Dict[str, Any]]:
        """获取镜像源列表"""
        return self.get("mirrors.sources", [])
    
    @config_handle_exceptions(context="添加镜像源", show_dialog=False, log_level="WARNING", return_value=False)
    def add_mirror_source(self, name: str, url: str, priority: int) -> bool:
        """添加镜像源"""
        sources = self.get_mirror_sources()
        
        # 检查是否已存在
        for source in sources:
            if source["name"] == name:
                self.config_error.emit(f"镜像源 '{name}' 已存在")
                return False
        
        # 添加新源
        new_source = {
            "name": name,
            "url": url,
            "priority": priority
        }
        sources.append(new_source)
        
        # 按优先级排序
        sources.sort(key=lambda x: x["priority"])
        
        return self.set("mirrors.sources", sources)
    
    @config_handle_exceptions(context="移除镜像源", show_dialog=False, log_level="INFO", return_value=False)
    def remove_mirror_source(self, name: str) -> bool:
        """移除镜像源"""
        sources = self.get_mirror_sources()
        sources = [s for s in sources if s["name"] != name]
        return self.set("mirrors.sources", sources)
    
    @config_handle_exceptions(context="更新镜像源", show_dialog=False, log_level="WARNING", return_value=False)
    def update_mirror_source(self, name: str, url: str = None, priority: int = None) -> bool:
        """更新镜像源"""
        sources = self.get_mirror_sources()
        
        for source in sources:
            if source["name"] == name:
                if url is not None:
                    source["url"] = url
                if priority is not None:
                    source["priority"] = priority
                break
        else:
            self.config_error.emit(f"镜像源 '{name}' 不存在")
            return False
        
        # 按优先级排序
        sources.sort(key=lambda x: x["priority"])
        
        return self.set("mirrors.sources", sources)
    
    @config_handle_exceptions(context="设置镜像源启用状态", show_dialog=False, log_level="INFO", return_value=False)
    def set_mirror_source_enabled(self, name: str, enabled: bool) -> bool:
        """设置镜像源启用状态"""
        sources = self.get_mirror_sources()
        
        for source in sources:
            if source["name"] == name:
                source["enabled"] = enabled
                return self.set("mirrors.sources", sources)
        
        self.config_error.emit(f"镜像源 '{name}' 不存在")
        return False
    
    def get_default_mirror_source(self) -> str:
        """获取默认镜像源"""
        return self.get("mirrors.default_source", "pypi")
    
    @config_handle_exceptions(context="设置默认镜像源", show_dialog=False, log_level="WARNING", return_value=False)
    def set_default_mirror_source(self, source_name: str) -> bool:
        """设置默认镜像源"""
        sources = self.get_mirror_sources()
        source_names = [s["name"] for s in sources]
        
        if source_name not in source_names:
            self.config_error.emit(f"镜像源 '{source_name}' 不存在")
            return False
        
        return self.set("mirrors.default_source", source_name)
    
    # 插件管理方法
    def get_installed_plugins(self) -> List[Dict[str, Any]]:
        """获取已安装插件列表"""
        return self.get("plugins.installed_plugins", [])
    
    @config_handle_exceptions(context="添加插件", show_dialog=False, log_level="WARNING", return_value=False)
    def add_plugin(self, plugin_info: Dict[str, Any]) -> bool:
        """添加插件到配置"""
        plugins = self.get_installed_plugins()
        
        # 检查是否已存在
        plugin_name = plugin_info.get("name")
        if not plugin_name:
            self.config_error.emit("插件名称不能为空")
            return False
        
        for plugin in plugins:
            if plugin.get("name") == plugin_name:
                self.config_error.emit(f"插件 '{plugin_name}' 已存在")
                return False
        
        # 添加插件
        plugins.append(plugin_info)
        return self.set("plugins.installed_plugins", plugins)
    
    @config_handle_exceptions(context="移除插件", show_dialog=False, log_level="INFO", return_value=False)
    def remove_plugin(self, plugin_name: str) -> bool:
        """从配置中移除插件"""
        plugins = self.get_installed_plugins()
        plugins = [p for p in plugins if p.get("name") != plugin_name]
        return self.set("plugins.installed_plugins", plugins)
    
    @config_handle_exceptions(context="更新插件", show_dialog=False, log_level="WARNING", return_value=False)
    def update_plugin(self, plugin_name: str, updates: Dict[str, Any]) -> bool:
        """更新插件信息"""
        plugins = self.get_installed_plugins()
        
        for plugin in plugins:
            if plugin.get("name") == plugin_name:
                plugin.update(updates)
                return self.set("plugins.installed_plugins", plugins)
        
        self.config_error.emit(f"插件 '{plugin_name}' 不存在")
        return False
    
    def get_plugin_info(self, plugin_name: str) -> Optional[Dict[str, Any]]:
        """获取插件信息"""
        plugins = self.get_installed_plugins()
        for plugin in plugins:
            if plugin.get("name") == plugin_name:
                return plugin
        return None
    
    # 环境管理方法
    def get_available_environments(self) -> List[str]:
        """获取可用环境列表"""
        return self.get("environments.available", [])
    
    @config_handle_exceptions(context="添加环境", show_dialog=False, log_level="INFO", return_value=False)
    def add_environment(self, env_name: str) -> bool:
        """添加环境"""
        envs = self.get_available_environments()
        if env_name not in envs:
            envs.append(env_name)
            return self.set("environments.available", envs)
        return True
    
    @config_handle_exceptions(context="移除环境", show_dialog=False, log_level="WARNING", return_value=False)
    def remove_environment(self, env_name: str) -> bool:
        """移除环境"""
        envs = self.get_available_environments()
        envs = [e for e in envs if e != env_name]
        return self.set("environments.available", envs)
    
    @config_handle_exceptions(context="设置默认环境", show_dialog=False, log_level="WARNING", return_value=False)
    def set_default_environment(self, env_name: str) -> bool:
        """设置默认环境"""
        envs = self.get_available_environments()
        if env_name not in envs:
            self.config_error.emit(f"环境 '{env_name}' 不存在")
            return False
        return self.set("environments.default", env_name)
    
    # 日志配置方法
    def get_log_level(self) -> str:
        """获取日志级别"""
        return self.get("app.log_level", "INFO")
    
    def get_log_dir(self) -> str:
        """获取日志目录"""
        return self.get("app.log_dir", "logs")
    
    def set_log_dir(self, log_dir: str) -> bool:
        """设置日志目录"""
        return self.set("app.log_dir", log_dir)
    
    # UI配置方法
    def get_theme(self) -> str:
        """获取主题"""
        return self.get("ui.theme", "light")
    
    def get_window_size(self) -> tuple:
        """获取窗口大小"""
        width = self.get("ui.window_width", 1200)
        height = self.get("ui.window_height", 800)
        return (width, height)
    
    def get_default_environment(self) -> str:
        """获取默认环境"""
        return self.get("environments.default", "python3.11")
    
    def get_mirror_retry_count(self) -> int:
        """获取镜像源重试次数"""
        return self.get("mirrors.retry_count", 3)
    
    @config_handle_exceptions(context="设置日志级别", show_dialog=False, log_level="WARNING", return_value=False)
    def set_log_level(self, level: str) -> bool:
        """设置日志级别"""
        if level not in ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]:
            self.config_error.emit(f"无效的日志级别: {level}")
            return False
        return self.set("logging.log_level", level)
    
    @config_handle_exceptions(context="设置主题", show_dialog=False, log_level="WARNING", return_value=False)
    def set_theme(self, theme: str) -> bool:
        """设置主题"""
        if theme not in ["light", "dark", "auto"]:
            self.config_error.emit(f"无效的主题: {theme}")
            return False
        return self.set("ui.theme", theme)
    
    @config_handle_exceptions(context="设置窗口大小", show_dialog=False, log_level="WARNING", return_value=False)
    def set_window_size(self, width: int, height: int) -> bool:
        """设置窗口大小"""
        if width < 800 or height < 600:
            self.config_error.emit("窗口大小不能小于 800x600")
            return False
        self.set("ui.window_width", width)
        self.set("ui.window_height", height)
        return True
    
    # 高级配置方法
    def is_debug_mode(self) -> bool:
        """是否启用调试模式"""
        return self.get("advanced.debug_mode", False)
    
    def set_debug_mode(self, enabled: bool) -> bool:
        """设置调试模式"""
        return self.set("advanced.debug_mode", enabled)
    
    def is_mirror_enabled(self) -> bool:
        """是否启用镜像源"""
        return self.get("mirrors.enabled", True)
    
    def set_mirror_enabled(self, enabled: bool) -> bool:
        """设置镜像源启用状态"""
        return self.set("mirrors.enabled", enabled)
    
    def get_mirror_timeout(self) -> int:
        """获取镜像源超时时间"""
        return self.get("mirrors.timeout_seconds", 30)
    
    @config_handle_exceptions(context="设置镜像源超时", show_dialog=False, log_level="WARNING", return_value=False)
    def set_mirror_timeout(self, timeout: int) -> bool:
        """设置镜像源超时时间"""
        if timeout < 5 or timeout > 300:
            self.config_error.emit("超时时间必须在 5-300 秒之间")
            return False
        return self.set("mirrors.timeout_seconds", timeout)
    
    @config_handle_exceptions(context="设置镜像源重试次数", show_dialog=False, log_level="WARNING", return_value=False)
    def set_mirror_retry_count(self, count: int) -> bool:
        """设置镜像源重试次数"""
        if count < 1 or count > 10:
            self.config_error.emit("重试次数必须在 1-10 之间")
            return False
        return self.set("mirrors.retry_count", count)
    
    def is_ssl_verify_enabled(self) -> bool:
        """是否启用SSL验证"""
        return self.get("mirrors.verify_ssl", True)
    
    def set_ssl_verify_enabled(self, enabled: bool) -> bool:
        """设置SSL验证启用状态"""
        return self.set("mirrors.verify_ssl", enabled)
    
    # 导出和导入配置
    @config_handle_exceptions(context="导出配置", show_dialog=False, log_level="ERROR", return_value=False)
    def export_config(self, file_path: str) -> bool:
        """导出配置到文件"""
        export_path = Path(file_path)
        with open(export_path, 'w', encoding='utf-8') as f:
            toml.dump(self.config, f)
        return True
    
    @config_handle_exceptions(context="导入配置", show_dialog=False, log_level="ERROR", return_value=False)
    def import_config(self, file_path: str) -> bool:
        """从文件导入配置"""
        import_path = Path(file_path)
        if not import_path.exists():
            self.config_error.emit(f"配置文件不存在: {file_path}")
            return False
        
        with open(import_path, 'r', encoding='utf-8') as f:
            imported_config = toml.load(f)
        
        # 合并配置
        self.config = self._merge_configs(self.default_config, imported_config)
        
        # 验证配置
        if not self._validate_config():
            self.config_error.emit("导入的配置文件验证失败")
            return False
        
        self.config_changed.emit("config", "imported")
        return True
    
    # 配置统计信息
    def get_config_stats(self) -> Dict[str, Any]:
        """获取配置统计信息"""
        return {
            "total_sections": len(self.config),
            "mirror_sources_count": len(self.get_mirror_sources()),
            "installed_plugins_count": len(self.get_installed_plugins()),
            "available_environments_count": len(self.get_available_environments()),
            "has_changes": self.has_changes(),
            "config_file_exists": self.config_file.exists(),
            "config_file_size": self.config_file.stat().st_size if self.config_file.exists() else 0
        }
