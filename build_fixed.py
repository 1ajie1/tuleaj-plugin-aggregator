#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修复版打包脚本 - 解决路径和图标问题
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def main():
    """修复版打包流程"""
    print("🚀 开始打包 Tuleaj Plugin Aggregator (修复版)...")
    
    # 确保在项目根目录
    if not Path("src/main.py").exists():
        print("❌ 错误: 请在项目根目录运行此脚本")
        return False
    
    # 清理旧的构建文件
    print("🧹 清理旧文件...")
    for dir_name in ["build", "dist"]:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)
    
    # 确保必要目录存在
    print("📁 确保目录结构...")
    Path("src/assets").mkdir(exist_ok=True)
    Path("plugins").mkdir(exist_ok=True)
    Path("envs").mkdir(exist_ok=True)
    
    # PyInstaller命令 - 修复版
    cmd = [
        "pyinstaller",
        "--clean",
        "--noconfirm",
        "--onedir",  # 打包成文件夹，兼容性更好
        "--windowed",  # 不显示控制台
        "--name=TuleajPluginAggregator",
        
        # 添加数据文件 - 修复路径问题
        "--add-data=src/ui;ui",
        "--add-data=src/assets;assets",
        
        # WebEngine相关文件
        "--collect-all=PySide6.QtWebEngine",
        "--collect-all=PySide6.QtWebEngineCore",
        "--collect-all=PySide6.QtWebEngineWidgets",
        
        # 隐藏导入 - 确保所有模块都被包含
        "--hidden-import=PySide6.QtCore",
        "--hidden-import=PySide6.QtGui", 
        "--hidden-import=PySide6.QtWidgets",
        "--hidden-import=PySide6.QtQml",
        "--hidden-import=PySide6.QtQuick",
        "--hidden-import=PySide6.QtQuickControls2",
        "--hidden-import=PySide6.QtQuickLayouts",
        "--hidden-import=PySide6.QtWebEngine",
        "--hidden-import=PySide6.QtWebEngineCore",
        "--hidden-import=PySide6.QtWebEngineWidgets",
        
        # 项目模块
        "--hidden-import=core.config_bridge",
        "--hidden-import=core.plugin_bridge",
        "--hidden-import=core.plugin_process_manager", 
        "--hidden-import=core.dependency_manager",
        "--hidden-import=core.config_manager",
        "--hidden-import=utils.logger",
        "--hidden-import=utils.exception_handler",
        
        # 第三方库
        "--hidden-import=toml",
        "--hidden-import=pathlib",
        "--hidden-import=subprocess",
        "--hidden-import=shutil",
        "--hidden-import=json",
        "--hidden-import=logging",
        
        # 排除不需要的模块
        "--exclude-module=tkinter",
        "--exclude-module=matplotlib",
        "--exclude-module=numpy",
        "--exclude-module=pandas",
        "--exclude-module=scipy",
        "--exclude-module=PIL",
        "--exclude-module=cv2",
        "--exclude-module=tensorflow",
        "--exclude-module=torch",
        
        # 主程序文件
        "src/main.py"
    ]
    
    print("🔨 执行打包命令...")
    print("命令:", " ".join(cmd))
    
    try:
        # 执行打包
        result = subprocess.run(cmd, check=True, text=True)
        print("✅ 打包成功！")
        
        # 检查输出目录
        dist_dir = Path("dist/TuleajPluginAggregator")
        if dist_dir.exists():
            print(f"📁 输出目录: {dist_dir.absolute()}")
            print(f"🚀 可执行文件: {dist_dir / 'TuleajPluginAggregator.exe'}")
            
            # 复制配置文件
            if Path("config.toml").exists():
                shutil.copy2("config.toml", dist_dir)
                print("✅ 已复制配置文件")
            
            # 创建启动脚本
            startup_script = dist_dir / "start.bat"
            with open(startup_script, "w", encoding="utf-8") as f:
                f.write("@echo off\n")
                f.write("echo Starting Tuleaj Plugin Aggregator...\n")
                f.write("TuleajPluginAggregator.exe\n")
                f.write("pause\n")
            print("✅ 启动脚本已创建")
            
            # 创建README
            readme_content = """# Tuleaj Plugin Aggregator

## 运行说明

1. 双击 `TuleajPluginAggregator.exe` 启动程序
2. 或双击 `start.bat` 启动程序（会显示启动信息）

## 功能说明

- 插件管理：启动、停止、卸载插件
- 依赖管理：自动管理插件依赖
- 系统托盘：程序可以最小化到系统托盘
- 配置管理：支持配置文件管理

## 注意事项

- 首次运行可能需要较长时间
- 插件文件位于 `plugins` 目录
- 配置文件为 `config.toml`
- 日志文件位于 `logs` 目录

## 系统要求

- Windows 10/11
- 无需安装Python环境
- 建议8GB以上内存

## 技术支持

如有问题，请查看日志文件或联系技术支持。
"""
            
            readme_file = dist_dir / "README.txt"
            with open(readme_file, "w", encoding="utf-8") as f:
                f.write(readme_content)
            print("✅ README文件已创建")
            
            return True
        else:
            print("❌ 错误: 输出目录不存在")
            return False
            
    except subprocess.CalledProcessError as e:
        print("❌ 打包失败")
        print("错误信息:", e.stderr if hasattr(e, 'stderr') else str(e))
        return False
    except Exception as e:
        print("❌ 打包过程中发生错误:", str(e))
        return False

if __name__ == "__main__":
    success = main()
    if success:
        print("\n🎉 打包完成！")
        print("📖 使用说明:")
        print("  1. 进入 dist/TuleajPluginAggregator 目录")
        print("  2. 双击 TuleajPluginAggregator.exe 运行程序")
        print("  3. 程序支持系统托盘功能")
        print("  4. 查看 README.txt 了解详细说明")
    else:
        print("\n❌ 打包失败，请检查错误信息")
    
    sys.exit(0 if success else 1)
