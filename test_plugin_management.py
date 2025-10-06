#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试新的插件管理功能
"""

import sys
from pathlib import Path

# 添加src目录到Python路径
sys.path.insert(0, str(Path(__file__).parent / "src"))

from core.plugin_bridge import PluginBridge
from PySide6.QtCore import QCoreApplication

def test_plugin_management():
    """测试插件管理功能"""
    print("=== 测试新的插件管理功能 ===")
    
    # 创建应用程序
    app = QCoreApplication(sys.argv)
    
    # 创建插件桥接器
    bridge = PluginBridge()
    
    # 等待插件加载完成
    print("等待插件加载...")
    app.processEvents()
    
    # 获取插件列表
    plugins = bridge.get_plugins()
    print(f"发现 {len(plugins)} 个插件:")
    for plugin in plugins:
        print(f"  - {plugin['name']}: {plugin['status']}")
    
    if not plugins:
        print("没有找到插件，测试结束")
        return
    
    # 测试第一个插件
    test_plugin = plugins[0]
    plugin_name = test_plugin['name']
    
    print(f"\n测试插件: {plugin_name}")
    
    # 测试启动插件
    print(f"1. 启动插件 {plugin_name}...")
    success = bridge.start_plugin(plugin_name)
    print(f"启动结果: {'成功' if success else '失败'}")
    
    if success:
        # 等待一下
        app.processEvents()
        
        # 测试停止插件
        print(f"2. 停止插件 {plugin_name}...")
        success = bridge.stop_plugin(plugin_name)
        print(f"停止结果: {'成功' if success else '失败'}")
    
    print("\n测试完成")

def main():
    """主函数"""
    print("插件管理功能测试")
    print("=" * 50)
    
    test_plugin_management()

if __name__ == "__main__":
    main()
