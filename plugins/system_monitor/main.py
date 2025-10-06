#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
系统监控插件主入口
"""

import sys
import os
from PySide6.QtCore import QCoreApplication, QUrl
from PySide6.QtQml import qmlRegisterType, QQmlApplicationEngine
from PySide6.QtGui import QGuiApplication

# 添加当前目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from system_monitor_backend import SystemMonitorBackend, register_types


def main():
    """主函数"""
    # 创建应用程序
    app = QGuiApplication(sys.argv)
    
    # 注册 QML 类型
    register_types()
    
    # 创建 QML 引擎
    engine = QQmlApplicationEngine()
    
    # 加载 QML 文件
    qml_file = os.path.join(os.path.dirname(__file__), "system_monitor.qml")
    engine.load(QUrl.fromLocalFile(qml_file))
    
    # 检查是否成功加载
    if not engine.rootObjects():
        print("错误: 无法加载 QML 文件")
        return -1
    
    print("系统监控插件启动成功")
    print("显示 CPU、内存和网络监控信息")
    
    # 运行应用程序
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
