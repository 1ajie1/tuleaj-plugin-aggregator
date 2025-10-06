#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试插件 - 用于验证插件管理功能
"""

import time
import sys
from PySide6.QtCore import QCoreApplication, QTimer

def main():
    """测试插件主函数"""
    print("测试插件启动")
    print("插件将运行10秒后自动退出")
    
    # 创建应用程序实例
    app = QCoreApplication(sys.argv)
    
    # 设置定时器，10秒后退出
    timer = QTimer()
    timer.timeout.connect(app.quit)
    timer.start(10000)  # 10秒
    
    print("测试插件正在运行...")
    
    # 运行应用程序
    app.exec()
    
    print("测试插件正常退出")

if __name__ == "__main__":
    main()
