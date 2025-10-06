#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
依赖管理器
基于虚拟环境的依赖管理，支持版本协商和懒加载
"""

import toml
import subprocess
import os
from pathlib import Path
from typing import Dict, List, Optional, Set
from packaging import specifiers
from PySide6.QtCore import QObject, Signal
from utils.logger import Logger
from utils.exception_handler import ExceptionHandler, handle_exceptions


class DependencyInfo:
    """依赖信息类"""
    
    def __init__(self, name: str, version_spec: str, source: str = ""):
        self.name = name
        self.version_spec = version_spec
        self.source = source  # 来源插件名称
    
    def __str__(self):
        return f"{self.name}{self.version_spec}"
    
    def __repr__(self):
        return f"DependencyInfo(name='{self.name}', version_spec='{self.version_spec}', source='{self.source}')"


class VersionResolver:
    """版本协商器"""
    
    @staticmethod
    def resolve_version_conflict(deps: List[DependencyInfo]) -> Optional[str]:
        """
        解决版本冲突，优先使用高版本要求
        
        Args:
            deps: 依赖信息列表
            
        Returns:
            协商后的版本规范，如果无法协商则返回None
        """
        if not deps:
            return None
        
        if len(deps) == 1:
            return deps[0].version_spec
        
        # 收集所有版本要求
        version_specs = []
        for dep in deps:
            try:
                spec = specifiers.SpecifierSet(dep.version_spec)
                version_specs.append((dep.version_spec, spec))
            except Exception as e:
                print(f"解析版本规范失败: {dep.version_spec}, 错误: {e}")
                continue
        
        if not version_specs:
            return None
        
        # 优先使用高版本策略
        try:
            # 直接选择版本要求最高的规范（优先高版本）
            print("使用高版本优先策略")
            highest_spec = max(version_specs, key=lambda x: VersionResolver._get_version_priority(x[0]))
            print(f"选择最高版本要求: {highest_spec[0]}")
            return highest_spec[0]
            
        except Exception as e:
            print(f"版本协商失败: {e}")
            # 回退到使用第一个规范
            return version_specs[0][0]
    
    @staticmethod
    def _get_version_priority(version_spec: str) -> float:
        """
        获取版本规范的优先级（数值越大优先级越高）
        
        Args:
            version_spec: 版本规范字符串，如 ">=7.1.0", ">=8.0.0"
            
        Returns:
            优先级数值
        """
        try:
            # 提取版本号
            if '>=' in version_spec:
                version_str = version_spec.split('>=')[1]
            elif '>' in version_spec:
                version_str = version_spec.split('>')[1]
            elif '==' in version_spec:
                version_str = version_spec.split('==')[1]
            elif '<=' in version_spec:
                version_str = version_spec.split('<=')[1]
            elif '<' in version_spec:
                version_str = version_spec.split('<')[1]
            else:
                return 0.0
            
            # 将版本号转换为数值进行比较
            from packaging import version
            ver = version.parse(version_str)
            
            # 计算优先级：主版本*10000 + 次版本*100 + 修订版本
            major = ver.major if ver.major is not None else 0
            minor = ver.minor if ver.minor is not None else 0
            micro = ver.micro if ver.micro is not None else 0
            
            priority = major * 10000 + minor * 100 + micro
            print(f"版本 {version_spec} 的优先级: {priority}")
            return priority
            
        except Exception as e:
            print(f"计算版本优先级失败: {version_spec}, 错误: {e}")
            return 0.0
    
    @staticmethod
    def is_compatible(version_spec1: str, version_spec2: str) -> bool:
        """检查两个版本规范是否兼容"""
        try:
            spec1 = specifiers.SpecifierSet(version_spec1)
            spec2 = specifiers.SpecifierSet(version_spec2)
            
            # 检查是否有交集
            intersection = spec1 & spec2
            return bool(intersection)
        except Exception:
            return False


class DependencyManager(QObject):
    """依赖管理器"""
    
    # 信号定义
    dependencyInstalled = Signal(str, str, bool, str)  # 环境名, 包名, 成功状态, 消息
    dependencyConflictResolved = Signal(str, str, str)  # 包名, 原版本, 协商版本
    environmentUpdated = Signal(str)  # 环境名
    dependencySyncStarted = Signal(str)  # 环境名
    dependencySyncCompleted = Signal(str, bool, str)  # 环境名, 成功状态, 消息
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.project_root = Path(__file__).parent.parent.parent
        self.envs_dir = self.project_root / "envs"
        self.plugins_dir = self.project_root / "plugins"
        
        # 初始化日志管理器
        self.logger = Logger(log_level="INFO", log_dir="logs")
        
        # 初始化异常处理器
        self.exception_handler = ExceptionHandler(self.logger)
        
        # 缓存
        self._env_dependencies_cache: Dict[str, Dict[str, DependencyInfo]] = {}
        self._installed_packages_cache: Dict[str, Set[str]] = {}
        
        # 确保环境目录存在
        self.envs_dir.mkdir(exist_ok=True)
    
    def get_environment_python_path(self, env_name: str) -> Path:
        """获取环境中的Python路径"""
        env_path = self.envs_dir / env_name
        
        # 检查是否有 .venv 子目录（uv 创建的环境）
        venv_path = env_path / ".venv"
        if venv_path.exists():
            env_path = venv_path
        
        if os.name == 'nt':  # Windows
            return env_path / "Scripts" / "python.exe"
        else:  # Unix/Linux
            return env_path / "bin" / "python"
    
    def get_environment_pip_path(self, env_name: str) -> Path:
        """获取环境中的pip路径"""
        env_path = self.envs_dir / env_name
        
        # 检查是否有 .venv 子目录（uv 创建的环境）
        venv_path = env_path / ".venv"
        if venv_path.exists():
            env_path = venv_path
        
        if os.name == 'nt':  # Windows
            return env_path / "Scripts" / "pip.exe"
        else:  # Unix/Linux
            return env_path / "bin" / "pip"
    
    @handle_exceptions("读取插件依赖", show_dialog=False, log_level="ERROR", return_value=[])
    def read_plugin_dependencies(self, plugin_path: Path) -> List[DependencyInfo]:
        """读取插件的依赖信息"""
        pyproject_file = plugin_path / "pyproject.toml"
        
        if not pyproject_file.exists():
            self.logger.warning(f"插件 {plugin_path.name} 缺少 pyproject.toml 文件")
            return []
        
        try:
            with open(pyproject_file, 'r', encoding='utf-8') as f:
                data = toml.load(f)
            
            dependencies = []
            project_deps = data.get('project', {}).get('dependencies', [])
            
            for dep in project_deps:
                if isinstance(dep, str):
                    # 解析依赖字符串，如 "psutil>=7.1.0"
                    if '>=' in dep:
                        name, version_spec = dep.split('>=', 1)
                        version_spec = f">={version_spec}"
                    elif '==' in dep:
                        name, version_spec = dep.split('==', 1)
                        version_spec = f"=={version_spec}"
                    elif '>' in dep:
                        name, version_spec = dep.split('>', 1)
                        version_spec = f">{version_spec}"
                    elif '<=' in dep:
                        name, version_spec = dep.split('<=', 1)
                        version_spec = f"<={version_spec}"
                    elif '<' in dep:
                        name, version_spec = dep.split('<', 1)
                        version_spec = f"<{version_spec}"
                    else:
                        name = dep
                        version_spec = ""
                    
                    dependencies.append(DependencyInfo(
                        name=name.strip(),
                        version_spec=version_spec.strip(),
                        source=plugin_path.name
                    ))
            
            self.logger.info(f"从插件 {plugin_path.name} 读取到 {len(dependencies)} 个依赖")
            return dependencies
            
        except Exception as e:
            self.logger.error(f"读取插件 {plugin_path.name} 依赖失败: {e}")
            return []
    
    def collect_all_dependencies(self, env_name: str) -> Dict[str, List[DependencyInfo]]:
        """收集环境中所有插件的依赖"""
        dependencies_map = {}
        
        if not self.plugins_dir.exists():
            return dependencies_map
        
        for plugin_dir in self.plugins_dir.iterdir():
            if plugin_dir.is_dir():
                plugin_deps = self.read_plugin_dependencies(plugin_dir)
                for dep in plugin_deps:
                    if dep.name not in dependencies_map:
                        dependencies_map[dep.name] = []
                    dependencies_map[dep.name].append(dep)
        
        return dependencies_map
    
    def resolve_dependencies(self, env_name: str) -> Dict[str, str]:
        """解决依赖冲突，返回协商后的依赖版本"""
        all_deps = self.collect_all_dependencies(env_name)
        resolved_deps = {}
        
        for package_name, dep_list in all_deps.items():
            if len(dep_list) == 1:
                # 只有一个依赖，直接使用
                resolved_deps[package_name] = dep_list[0].version_spec
            else:
                # 多个依赖，进行版本协商
                resolved_version = VersionResolver.resolve_version_conflict(dep_list)
                if resolved_version:
                    resolved_deps[package_name] = resolved_version
                    
                    # 记录版本协商
                    original_versions = [dep.version_spec for dep in dep_list]
                    self.logger.info(f"包 {package_name} 版本协商: {original_versions} -> {resolved_version}")
                    self.dependencyConflictResolved.emit(
                        package_name, 
                        str(original_versions), 
                        resolved_version
                    )
                else:
                    self.logger.error(f"无法协商包 {package_name} 的版本")
        
        return resolved_deps
    
    @handle_exceptions("同步依赖", show_dialog=False, log_level="ERROR", return_value=False)
    def sync_dependencies_with_uv(self, env_name: str, resolved_deps: Dict[str, str]) -> bool:
        """
        使用 uv sync 同步依赖，只有同步成功后才保留 pyproject.toml
        
        Args:
            env_name: 环境名称
            resolved_deps: 协商后的依赖字典
            
        Returns:
            同步是否成功
        """
        try:
            env_path = self.envs_dir / env_name
            python_path = self.get_environment_python_path(env_name)
            
            if not python_path.exists():
                self.logger.error(f"环境 {env_name} 不存在")
                return False
            
            # 创建临时的 pyproject.toml 文件
            temp_pyproject_path = env_path / "pyproject.toml.temp"
            backup_pyproject_path = env_path / "pyproject.toml.backup"
            original_pyproject_path = env_path / "pyproject.toml"
            
            # 备份原始的 pyproject.toml（如果存在）
            if original_pyproject_path.exists():
                import shutil
                shutil.copy2(original_pyproject_path, backup_pyproject_path)
                self.logger.info(f"备份原始 pyproject.toml 到 {backup_pyproject_path}")
            
            # 创建新的 pyproject.toml 内容
            pyproject_content = self._generate_pyproject_content(resolved_deps)
            
            # 写入临时文件
            with open(temp_pyproject_path, 'w', encoding='utf-8') as f:
                f.write(pyproject_content)
            
            self.logger.info(f"创建临时 pyproject.toml: {temp_pyproject_path}")
            
            # 使用 uv sync 同步依赖
            self.logger.info(f"开始使用 uv sync 同步环境 {env_name} 的依赖")
            self.dependencySyncStarted.emit(env_name)
            
            # 构建 uv sync 命令
            cmd = [
                "uv", "sync",
                "--python", str(python_path),
                "--project", str(env_path)
            ]

            self.logger.info(f"执行 uv sync 命令: {cmd}")
            
            # 执行 uv sync
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300,  # 5分钟超时
                cwd=str(env_path),
                encoding='utf-8',
                errors='replace'  # 遇到编码错误时用替换字符代替
            )
            
            if result.returncode == 0:
                self.logger.info("uv sync 成功完成")
                self.logger.info(f"同步输出: {result.stdout}")
                
                # 同步成功，将临时文件重命名为正式文件
                if original_pyproject_path.exists():
                    original_pyproject_path.unlink()  # 删除现有文件
                temp_pyproject_path.rename(original_pyproject_path)
                self.logger.info("依赖同步成功，保留新的 pyproject.toml")
                
                # 清理备份文件
                if backup_pyproject_path.exists():
                    backup_pyproject_path.unlink()
                    self.logger.info("清理备份文件")
                
                self.dependencySyncCompleted.emit(env_name, True, "依赖同步成功")
                return True
            else:
                self.logger.error(f"uv sync 失败，返回码: {result.returncode}")
                self.logger.error(f"标准输出: {result.stdout}")
                self.logger.error(f"错误输出: {result.stderr}")
                
                # 同步失败，恢复原始文件
                if backup_pyproject_path.exists():
                    shutil.copy2(backup_pyproject_path, original_pyproject_path)
                    self.logger.info("恢复原始 pyproject.toml")
                
                # 清理临时文件
                if temp_pyproject_path.exists():
                    temp_pyproject_path.unlink()
                if backup_pyproject_path.exists():
                    backup_pyproject_path.unlink()
                
                # 提供更详细的错误信息
                error_msg = result.stderr or result.stdout or "未知错误"
                self.dependencySyncCompleted.emit(env_name, False, f"同步失败: {error_msg}")
                return False
                
        except subprocess.TimeoutExpired:
            self.logger.error("uv sync 超时")
            # 清理临时文件
            if temp_pyproject_path.exists():
                temp_pyproject_path.unlink()
            if backup_pyproject_path.exists():
                backup_pyproject_path.unlink()
            self.dependencySyncCompleted.emit(env_name, False, "同步超时")
            return False
        except Exception as e:
            self.logger.error(f"同步依赖时发生错误: {e}")
            # 清理临时文件
            if temp_pyproject_path.exists():
                temp_pyproject_path.unlink()
            if backup_pyproject_path.exists():
                backup_pyproject_path.unlink()
            self.dependencySyncCompleted.emit(env_name, False, f"同步错误: {str(e)}")
            return False
    
    def _generate_pyproject_content(self, resolved_deps: Dict[str, str]) -> str:
        """
        生成 pyproject.toml 内容
        
        Args:
            resolved_deps: 协商后的依赖字典
            
        Returns:
            pyproject.toml 内容字符串
        """
        # 构建依赖列表
        dependencies = []
        for package_name, version_spec in resolved_deps.items():
            if version_spec:
                dependencies.append(f'    "{package_name}{version_spec}",')
            else:
                dependencies.append(f'    "{package_name}",')
        
        # 生成 pyproject.toml 内容
        dependencies_str = '\n'.join(dependencies)
        
        content = "[build-system]\n"
        content += 'requires = ["hatchling"]\n'
        content += 'build-backend = "hatchling.build"\n\n'
        content += "[project]\n"
        content += 'name = "resolved-dependencies"\n'
        content += 'version = "1.0.0"\n'
        content += 'description = "Resolved dependencies for plugin environment"\n'
        content += 'requires-python = ">=3.11"\n'
        content += 'dependencies = [\n'
        content += dependencies_str + '\n'
        content += ']\n\n'
        content += '[tool.hatch.build.targets.wheel]\n'
        content += 'packages = ["."]\n'
        
        return content
    
    def is_package_installed(self, env_name: str, package_name: str) -> bool:
        """检查包是否已安装在环境中"""
        try:
            python_path = self.get_environment_python_path(env_name)
            if not python_path.exists():
                return False
            
            # 使用pip list检查
            result = subprocess.run(
                [str(python_path), "-m", "pip", "list", "--format=json"],
                capture_output=True,
                text=True,
                timeout=30,
                encoding='utf-8',
                errors='replace'
            )
            
            if result.returncode == 0:
                import json
                installed_packages = json.loads(result.stdout)
                return any(pkg['name'].lower() == package_name.lower() for pkg in installed_packages)
            
            return False
            
        except Exception as e:
            self.logger.error(f"检查包 {package_name} 安装状态失败: {e}")
            return False
    
    @handle_exceptions("安装包", show_dialog=False, log_level="ERROR", return_value=False)
    def install_package(self, env_name: str, package_name: str, version_spec: str = "") -> bool:
        """在指定环境中安装包"""
        try:
            python_path = self.get_environment_python_path(env_name)
            if not python_path.exists():
                self.logger.error(f"环境 {env_name} 不存在")
                return False
            
            # 构建安装命令
            package_spec = f"{package_name}{version_spec}" if version_spec else package_name
            
            self.logger.info(f"在环境 {env_name} 中安装包: {package_spec}")
            
            result = subprocess.run(
                [str(python_path), "-m", "pip", "install", package_spec],
                capture_output=True,
                text=True,
                timeout=300,  # 5分钟超时
                encoding='utf-8',
                errors='replace'
            )
            
            if result.returncode == 0:
                self.logger.info(f"成功安装包 {package_spec} 到环境 {env_name}")
                self.dependencyInstalled.emit(env_name, package_name, True, f"成功安装 {package_spec}")
                return True
            else:
                error_msg = result.stderr or result.stdout
                self.logger.error(f"安装包 {package_spec} 失败: {error_msg}")
                self.dependencyInstalled.emit(env_name, package_name, False, f"安装失败: {error_msg}")
                return False
                
        except subprocess.TimeoutExpired:
            self.logger.error(f"安装包 {package_name} 超时")
            self.dependencyInstalled.emit(env_name, package_name, False, "安装超时")
            return False
        except Exception as e:
            self.logger.error(f"安装包 {package_name} 时发生错误: {e}")
            self.dependencyInstalled.emit(env_name, package_name, False, f"安装错误: {e}")
            return False
    
    @handle_exceptions("懒加载安装依赖", show_dialog=False, log_level="ERROR", return_value=False)
    def install_dependencies_lazy(self, env_name: str, plugin_name: str) -> bool:
        """懒加载安装插件依赖（集成 uv sync）"""
        try:
            plugin_path = self.plugins_dir / plugin_name
            if not plugin_path.exists():
                self.logger.error(f"插件 {plugin_name} 不存在")
                return False
            
            # 读取插件依赖
            plugin_deps = self.read_plugin_dependencies(plugin_path)
            if not plugin_deps:
                self.logger.info(f"插件 {plugin_name} 没有依赖")
                return True
            
            # 解决依赖冲突
            resolved_deps = self.resolve_dependencies(env_name)
            
            # 使用 uv sync 同步依赖
            self.logger.info(f"使用 uv sync 同步环境 {env_name} 的依赖")
            sync_success = self.sync_dependencies_with_uv(env_name, resolved_deps)
            
            if sync_success:
                self.logger.info(f"插件 {plugin_name} 的依赖同步成功")
                self.environmentUpdated.emit(env_name)
                return True
            else:
                self.logger.error(f"插件 {plugin_name} 的依赖同步失败")
                return False
                
        except Exception as e:
            self.logger.error(f"懒加载安装插件 {plugin_name} 依赖失败: {e}")
            return False
    
    @handle_exceptions("获取环境依赖", show_dialog=False, log_level="ERROR", return_value={})
    def get_environment_dependencies(self, env_name: str) -> Dict[str, str]:
        """获取环境中已安装的依赖信息"""
        try:
            python_path = self.get_environment_python_path(env_name)
            if not python_path.exists():
                return {}
            
            result = subprocess.run(
                [str(python_path), "-m", "pip", "list", "--format=json"],
                capture_output=True,
                text=True,
                timeout=30,
                encoding='utf-8',
                errors='replace'
            )
            
            if result.returncode == 0:
                import json
                installed_packages = json.loads(result.stdout)
                return {pkg['name']: pkg['version'] for pkg in installed_packages}
            
            return {}
            
        except Exception as e:
            self.logger.error(f"获取环境 {env_name} 依赖信息失败: {e}")
            return {}
    
    def cleanup_unused_dependencies(self, env_name: str) -> int:
        """清理环境中未使用的依赖（可选功能）"""
        # 这里可以实现更复杂的清理逻辑
        # 暂时返回0，表示没有清理任何包
        self.logger.info(f"环境 {env_name} 依赖清理功能暂未实现")
        return 0
