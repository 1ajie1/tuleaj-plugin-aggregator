# 系统监控插件

一个简单的 PySide6 QML 插件，用于实时监控系统资源使用情况。

## 功能特性

- **CPU 监控**: 实时显示 CPU 使用率
- **内存监控**: 显示内存使用率和详细信息
- **网络监控**: 实时显示网络上传/下载速度
- **美观界面**: 使用 QML 构建的现代化界面

## 安装要求

- Python 3.8+
- PySide6
- psutil

## 安装依赖

```bash
pip install psutil PySide6
```

## 运行插件

```bash
python main.py
```

## 文件结构

```
system_monitor/
├── main.py                    # 主入口文件
├── system_monitor_backend.py  # Python 后端逻辑
├── system_monitor.qml         # QML 前端界面
├── plugin.ini                 # 插件配置
└── README.md                  # 说明文档
```

## 技术实现

### 后端 (Python)
- 使用 `psutil` 库获取系统信息
- 使用 `QTimer` 实现定时更新
- 通过 Qt 信号槽机制与前端通信

### 前端 (QML)
- 使用 `ProgressBar` 显示使用率
- 实时更新文本显示
- 响应式布局设计

## 监控指标

- **CPU 使用率**: 0-100%
- **内存使用率**: 0-100%
- **内存总量**: MB
- **内存已用**: MB
- **网络下载速度**: MB/s
- **网络上传速度**: MB/s

## 更新频率

默认每秒更新一次，可在配置文件中调整。
