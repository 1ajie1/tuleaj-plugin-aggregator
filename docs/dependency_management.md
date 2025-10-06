# 基于虚拟环境的依赖管理系统

## 功能概述

本系统实现了基于虚拟环境的依赖管理，支持以下核心功能：

1. **依赖管理策略** - 基于虚拟环境的依赖管理
2. **启动策略** - 动态依赖安装（懒加载）****
3. **依赖冲突处理** - 版本协商（优先使用高版本）
4. **性能优化** - 懒加载机制

## 核心组件

### 1. DependencyManager（依赖管理器）

负责管理虚拟环境中的依赖包，主要功能：

- 读取插件的 `pyproject.toml` 文件
- 收集所有插件的依赖信息
- 解决依赖版本冲突
- 在指定环境中安装/卸载包
- 懒加载安装插件依赖

### 2. VersionResolver（版本协商器）

处理多个插件对同一包的不同版本要求：

- 分析版本规范兼容性
- 选择最优版本（优先高版本）
- 处理版本冲突

### 3. PluginBridge（插件桥接器）

集成依赖管理功能到插件系统：

- 启动插件前自动安装依赖
- 提供依赖管理相关的QML接口
- 处理依赖安装状态和错误

## 使用方法

### 1. 插件依赖配置

在插件的 `pyproject.toml` 文件中配置依赖：

```toml
[project]
name = "my-plugin"
version = "1.0.0"
dependencies = [
    "psutil>=7.1.0",
    "pyside6>=6.9.3",
    "requests>=2.28.0",
]

[plugin-metadata]
name = "我的插件"
version = "1.0.0"
entry_point = "main.py"
```

### 2. 启动插件

插件启动时会自动：

1. 读取插件的依赖配置
2. 检查环境中是否已安装所需依赖
3. 解决与其他插件的版本冲突
4. 安装缺失的依赖
5. 启动插件

### 3. 版本协商示例

假设有两个插件：

**插件A** 需要 `psutil>=7.0.0`
**插件B** 需要 `psutil>=7.1.0`

系统会自动选择 `psutil>=7.1.0`（更高版本要求），确保两个插件都能正常工作。

## 配置选项

在 `config.toml` 中可以配置依赖管理行为：

```toml
[dependencies]
# 是否启用懒加载依赖安装
lazy_loading_enabled = true
# 依赖安装超时时间（秒）
install_timeout_seconds = 300
# 是否在启动时显示依赖安装进度
show_install_progress = true
# 版本协商策略：strict（严格）、loose（宽松）
version_resolution_strategy = "strict"
# 是否自动清理未使用的依赖
auto_cleanup_unused = false
```

## API 接口

### QML 接口

```qml
// 获取插件依赖信息
var deps = pluginBridge.getPluginDependencies("plugin_name")

// 获取环境依赖信息
var envDeps = pluginBridge.getEnvironmentDependencies("env_name")

// 手动安装插件依赖
var success = pluginBridge.installPluginDependencies("plugin_name")
```

### Python 接口

```python
# 创建依赖管理器
dm = DependencyManager()

# 读取插件依赖
deps = dm.read_plugin_dependencies(plugin_path)

# 解决依赖冲突
resolved_deps = dm.resolve_dependencies(env_name)

# 懒加载安装依赖
success = dm.install_dependencies_lazy(env_name, plugin_name)
```

## 工作流程

1. **插件扫描** - 扫描所有插件目录
2. **依赖收集** - 读取每个插件的 `pyproject.toml`
3. **版本协商** - 解决依赖版本冲突
4. **懒加载安装** - 启动插件时安装缺失依赖
5. **环境运行** - 在指定虚拟环境中运行插件

## 优势

1. **环境隔离** - 每个虚拟环境独立管理依赖
2. **智能协商** - 自动解决版本冲突
3. **懒加载** - 按需安装，提高启动速度
4. **统一管理** - 集中管理所有插件的依赖
5. **错误处理** - 完善的错误处理和日志记录

## 测试

运行测试脚本验证功能：

```bash
python test_dependency_manager.py
```

测试内容包括：

- 版本协商器功能
- 依赖管理器功能
- 环境操作功能
