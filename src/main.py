"""
Tuleaj Plugin Aggregator 主程序
PySide6 QML 插件聚合工具的主入口
"""

import sys
import os
from pathlib import Path
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtWidgets import QApplication, QMessageBox
from PySide6.QtCore import QEvent, QResource
from PySide6.QtGui import QIcon, QAction
from PySide6.QtWidgets import QSystemTrayIcon, QMenu

# 添加src目录到Python路径
sys.path.insert(0, str(Path(__file__).parent))

# 导入核心模块
from core.config_bridge import ConfigBridge, register_qml_types
from core.plugin_bridge import PluginBridge, register_types as register_plugin_types
from utils.logger import Logger
from utils.exception_handler import ExceptionHandler, set_global_exception_handler


class MainApplication(QApplication):
    """主应用程序类"""
    
    def __init__(self):
        """初始化应用程序"""
        # 调用父类构造函数
        super().__init__(sys.argv)
        self.setApplicationName("Tuleaj Plugin Aggregator")
        self.setApplicationVersion("1.0.0")
        self.setOrganizationName("Tuleaj")
        
        # 初始化日志和异常处理器
        self.logger = Logger(log_level="INFO")
        self.exception_handler = ExceptionHandler(self.logger)
        set_global_exception_handler(self.exception_handler)
        
        # 初始化配置桥接器
        self.config_bridge = ConfigBridge()
        
        # 初始化插件桥接器
        self.plugin_bridge = PluginBridge()
        
        # 验证进程管理器实例
        if hasattr(self.plugin_bridge, 'process_manager') and self.plugin_bridge.process_manager:
            pm = self.plugin_bridge.process_manager
            self.logger.info(f"✅ 插件桥接器中的进程管理器对象ID: {id(pm)}")
            self.logger.info(f"✅ 进程管理器 processes 字典对象ID: {id(pm.processes)}")
            
            # 获取实例统计信息
            pm_instance_info = pm.get_instance_info()
            self.logger.info(f"✅ PluginProcessManager 实例统计: {pm_instance_info}")
        else:
            self.logger.error("❌ 插件桥接器中没有进程管理器")
        
        # 获取PluginBridge实例统计信息
        bridge_instance_info = self.plugin_bridge.get_instance_info()
        self.logger.info(f"✅ PluginBridge 实例统计: {bridge_instance_info}")
        
        # 注册QML类型
        register_qml_types()
        register_plugin_types()
        # 注意：PluginProcessManager不需要QML注册，因为它只通过PluginBridge在QML中使用
        
        # 创建QML引擎
        self.engine = QQmlApplicationEngine()
        
        # 连接QML错误信号
        self.engine.warnings.connect(self.handle_qml_warnings)
        
        # 设置QML上下文属性
        self.setup_qml_context()
        
        # 加载主QML文件
        self.load_main_qml()
        
        # 设置全局异常处理
        self.setup_global_exception_handling()
        
        # 设置退出处理标志
        self._is_exiting = False
        
        # 设置应用程序图标
        self.setup_app_icon()
        
        # 初始化系统托盘
        self.setup_system_tray()
        
        self.logger.info("应用程序初始化完成")
    
    def setup_app_icon(self):
        """设置应用程序图标"""
        try:
            # 注册资源文件
            resources_path = Path(__file__).parent / "resources.qrc"
            if resources_path.exists():
                QResource.registerResource(str(resources_path))
                self.logger.info(f"资源文件已注册: {resources_path}")
            
            # 设置应用程序图标
            icon_path = Path(__file__).parent / "assets" / "app_icon.svg"
            if icon_path.exists():
                app_icon = QIcon(str(icon_path))
                self.setWindowIcon(app_icon)
                self.logger.info(f"应用程序图标已设置: {icon_path}")
            else:
                # 使用默认图标
                default_icon = self.style().standardIcon(self.style().SP_ComputerIcon)
                self.setWindowIcon(default_icon)
                self.logger.warning("未找到应用程序图标文件，使用默认图标")
                
        except Exception as e:
            self.logger.error(f"设置应用程序图标失败: {e}")
    
    def setup_system_tray(self):
        """设置系统托盘"""
        try:
            # 检查系统是否支持托盘
            if not QSystemTrayIcon.isSystemTrayAvailable():
                self.logger.warning("系统不支持托盘功能")
                return
            
            # 创建托盘图标
            self.tray_icon = QSystemTrayIcon(self)
            
            # 设置托盘图标（使用应用程序图标）
            icon_path = Path(__file__).parent / "assets" / "app_icon.svg"
            if icon_path.exists():
                self.tray_icon.setIcon(QIcon(str(icon_path)))
            else:
                # 使用默认图标
                self.tray_icon.setIcon(self.style().standardIcon(self.style().SP_ComputerIcon))
            
            # 设置托盘提示
            self.tray_icon.setToolTip("Tuleaj Plugin Aggregator")
            
            # 创建托盘菜单
            tray_menu = QMenu()
            
            # 显示/隐藏主窗口
            show_action = QAction("显示主窗口", self)
            show_action.triggered.connect(self.show_main_window)
            tray_menu.addAction(show_action)
            
            # 分隔线
            tray_menu.addSeparator()
            
            # 退出程序
            quit_action = QAction("退出程序", self)
            quit_action.triggered.connect(self.quit_application)
            tray_menu.addAction(quit_action)
            
            # 设置托盘菜单
            self.tray_icon.setContextMenu(tray_menu)
            
            # 托盘图标双击事件
            self.tray_icon.activated.connect(self.on_tray_icon_activated)
            
            # 显示托盘图标
            self.tray_icon.show()
            
            self.logger.info("系统托盘初始化完成")
            
        except Exception as e:
            self.logger.error(f"设置系统托盘失败: {e}")
    
    def show_main_window(self):
        """显示主窗口"""
        try:
            # 获取主窗口
            main_window = None
            for window in self.allWindows():
                if window.objectName() == "mainWindow":
                    main_window = window
                    break
            
            if main_window:
                main_window.show()
                main_window.raise_()
                # 对于QML窗口，使用requestActivate而不是activateWindow
                if hasattr(main_window, 'requestActivate'):
                    main_window.requestActivate()
                self.logger.info("主窗口已显示")
            else:
                self.logger.warning("未找到主窗口")
                
        except Exception as e:
            self.logger.error(f"显示主窗口失败: {e}")
    
    def hide_main_window(self):
        """隐藏主窗口到托盘"""
        try:
            # 获取主窗口
            main_window = None
            for window in self.allWindows():
                if window.objectName() == "mainWindow":
                    main_window = window
                    break
            
            if main_window:
                main_window.hide()
                self.logger.info("主窗口已隐藏到托盘")
            else:
                # 如果没有找到主窗口，尝试隐藏所有窗口
                windows = self.allWindows()
                if windows:
                    for window in windows:
                        if hasattr(window, 'hide'):
                            window.hide()
                    self.logger.info("所有窗口已隐藏到托盘")
                else:
                    self.logger.warning("未找到任何窗口")
                
        except Exception as e:
            self.logger.error(f"隐藏主窗口失败: {e}")
    
    def on_tray_icon_activated(self, reason):
        """托盘图标激活事件"""
        if reason == QSystemTrayIcon.DoubleClick:
            self.show_main_window()
    
    def quit_application(self):
        """退出应用程序"""
        try:
            self.logger.info("用户从托盘菜单退出程序")
            
            # 设置退出标志
            self._is_exiting = True
            
            # 检测运行中的插件
            running_plugins = self.get_running_plugins()
            if running_plugins:
                self.logger.info(f"检测到 {len(running_plugins)} 个正在运行的插件: {running_plugins}")
                
                # 询问用户是否要停止插件并退出
                if self.show_exit_confirmation_dialog(running_plugins):
                    self.logger.info("用户确认退出，开始停止所有插件")
                    
                    # 停止所有插件
                    if self.stop_all_plugins(running_plugins):
                        self.logger.info("所有插件已安全停止")
                    else:
                        self.logger.warning("部分插件未能正常停止")
                else:
                    self.logger.info("用户取消退出")
                    # 重置退出标志
                    self._is_exiting = False
                    return
            
            # 隐藏托盘图标
            if hasattr(self, 'tray_icon'):
                self.tray_icon.hide()
            
            # 退出应用程序
            self.quit()
            
        except Exception as e:
            self.logger.error(f"退出应用程序失败: {e}")
            # 强制退出
            self.quit()
    
    def setup_qml_context(self):
        """设置QML上下文属性"""
        # 将配置桥接器暴露给QML
        self.engine.rootContext().setContextProperty("configBridge", self.config_bridge)
        
        # 将插件桥接器暴露给QML
        self.engine.rootContext().setContextProperty("pluginBridge", self.plugin_bridge)
        
        # 设置其他全局属性
        self.engine.rootContext().setContextProperty("appName", "Tuleaj Plugin Aggregator")
        self.engine.rootContext().setContextProperty("appVersion", "1.0.0")
        
        self.logger.info("QML上下文设置完成")
    
    def load_main_qml(self):
        """加载主QML文件"""
        try:
            # 获取QML文件路径
            qml_file = Path(__file__).parent / "ui" / "main.qml"
            
            if not qml_file.exists():
                raise FileNotFoundError(f"QML文件不存在: {qml_file}")
            
            # 加载QML文件
            self.engine.load(str(qml_file))
            
            # 检查是否成功加载
            if not self.engine.rootObjects():
                raise RuntimeError("QML文件加载失败")
            
            self.logger.info(f"QML文件加载成功: {qml_file}")
            
        except Exception as e:
            self.logger.error(f"加载QML文件失败: {e}")
            self.show_error_dialog("加载失败", f"无法加载主界面文件:\n{e}")
            sys.exit(1)
    
    def setup_global_exception_handling(self):
        """设置全局异常处理"""
        def handle_exception(exc_type, exc_value, exc_traceback):
            """全局异常处理器"""
            if issubclass(exc_type, KeyboardInterrupt):
                # 不处理键盘中断
                sys.__excepthook__(exc_type, exc_value, exc_traceback)
                return
            
            # 记录异常
            self.logger.critical(f"未捕获的异常: {exc_type.__name__}: {exc_value}")
            
            # 显示错误对话框
            self.show_error_dialog(
                "应用程序错误",
                f"发生未处理的异常:\n\n{exc_type.__name__}: {exc_value}\n\n应用程序将退出。"
            )
            
            # 保存配置
            try:
                self.config_bridge.saveConfig()
            except Exception:
                pass
            
            sys.exit(1)
        
        # 设置全局异常处理器
        sys.excepthook = handle_exception
        
        self.logger.info("全局异常处理设置完成")
    
    
    
    def notify(self, receiver, event):
        """重写 notify 方法，在事件处理前进行拦截"""
        # 检查是否是关闭事件
        if event.type() == QEvent.Close:
            self.logger.info("检测到窗口关闭事件")
            
            # 确保 _is_exiting 属性存在
            if not hasattr(self, '_is_exiting'):
                self._is_exiting = False
            
            # 如果还没有处理过退出，则隐藏到托盘
            if not self._is_exiting:
                self._is_exiting = True
                
                # 检测运行中的插件
                running_plugins = self.get_running_plugins()
                
                if running_plugins:
                    self.logger.info(f"检测到 {len(running_plugins)} 个正在运行的插件: {running_plugins}")
                    self.logger.info("直接隐藏到托盘，插件将继续在后台运行")
                else:
                    self.logger.info("没有正在运行的插件，直接隐藏到托盘")
                
                # 直接隐藏主窗口到托盘（不停止插件）
                self.hide_main_window()
                
                # 重置退出标志，允许下次关闭
                self._is_exiting = False
                
                # 阻止窗口关闭
                return False
        
        # 对于其他事件，正常处理
        return super().notify(receiver, event)
    
    def show_message_box(self, title, message, icon, buttons):
        """显示消息框"""
        try:
            msg_box = QMessageBox()
            msg_box.setIcon(icon)
            msg_box.setWindowTitle(title)
            msg_box.setText(message)
            msg_box.setStandardButtons(buttons)
            msg_box.setDefaultButton(QMessageBox.Yes)
            
            result = msg_box.exec()
            return result
            
        except Exception as e:
            self.logger.error(f"显示消息框失败: {e}")
            return QMessageBox.No
    
    def show_hide_confirmation_dialog(self, running_plugins):
        """显示隐藏到托盘确认对话框"""
        try:
            plugin_list = "\n".join([f"• {plugin}" for plugin in running_plugins])
            message = f"检测到 {len(running_plugins)} 个插件正在运行：\n\n{plugin_list}\n\n是否要隐藏到托盘？\n\n插件将继续在后台运行，您可以通过托盘图标重新打开界面。"
            
            reply = self.show_message_box(
                "隐藏到托盘",
                message,
                QMessageBox.Question,
                QMessageBox.Yes | QMessageBox.No
            )
            
            return reply == QMessageBox.Yes
            
        except Exception as e:
            self.logger.error(f"显示隐藏确认对话框失败: {e}")
            return True  # 默认隐藏
    
    def handle_qml_warnings(self, warnings):
        """处理QML警告"""
        for warning in warnings:
            self.logger.warning(f"QML警告: {warning}")
    
    def show_error_dialog(self, title: str, message: str):
        """显示错误对话框"""
        try:
            msg_box = QMessageBox()
            msg_box.setIcon(QMessageBox.Critical)
            msg_box.setWindowTitle(title)
            msg_box.setText(message)
            msg_box.setStandardButtons(QMessageBox.Ok)
            msg_box.exec()
        except Exception:
            # 如果无法显示对话框，则打印到控制台
            print(f"错误: {title}")
            print(f"消息: {message}")
    
    def show_info_dialog(self, title: str, message: str):
        """显示信息对话框"""
        try:
            msg_box = QMessageBox()
            msg_box.setIcon(QMessageBox.Information)
            msg_box.setWindowTitle(title)
            msg_box.setText(message)
            msg_box.setStandardButtons(QMessageBox.Ok)
            msg_box.exec()
        except Exception:
            print(f"信息: {title}")
            print(f"消息: {message}")
    
    def get_running_plugins(self):
        """获取正在运行的插件列表"""
        try:
            # 直接从进程管理器获取运行中的插件
            if hasattr(self.plugin_bridge, 'process_manager') and self.plugin_bridge.process_manager:
                running_plugins = self.plugin_bridge.process_manager.get_all_running_plugins()
                return running_plugins
            else:
                self.logger.warning("进程管理器不可用，尝试从插件桥接器获取")
                # 备用方案：从插件桥接器获取
                running_plugins = []
                for plugin_info in self.plugin_bridge.plugins_info:
                    plugin_name = plugin_info.get('name', '')
                    plugin_status = self.plugin_bridge.get_plugin_status(plugin_name)
                    if plugin_status == "running":
                        running_plugins.append(plugin_name)
                return running_plugins
        except Exception as e:
            self.logger.error(f"获取运行插件列表失败: {e}")
            return []
    
    def stop_all_plugins(self, plugin_list: list = None):
        """停止所有正在运行的插件"""
        try:
            if plugin_list is None:
                plugin_list = self.get_running_plugins()
            
            if not plugin_list:
                return True
            
            self.logger.info(f"开始停止 {len(plugin_list)} 个正在运行的插件")
            
            # 逐个停止插件
            for plugin_name in plugin_list:
                try:
                    self.logger.info(f"正在停止插件: {plugin_name}")
                    success = self.plugin_bridge.stop_plugin(plugin_name)
                    if success:
                        self.logger.info(f"插件 {plugin_name} 停止成功")
                    else:
                        self.logger.warning(f"插件 {plugin_name} 停止失败")
                except Exception as e:
                    self.logger.error(f"停止插件 {plugin_name} 时发生错误: {e}")
            
            # 等待所有插件完全停止
            import time
            time.sleep(2)  # 等待2秒让插件完全停止
            
            return True
            
        except Exception as e:
            self.logger.error(f"停止插件时发生错误: {e}")
            return False
    
    def _cleanup_process_manager(self):
        """清理进程管理器资源"""
        self.logger.info("清理进程管理器资源")
        try:
            if hasattr(self.plugin_bridge, 'process_manager') and self.plugin_bridge.process_manager:
                # 先停止所有进程
                processes_keys = list(self.plugin_bridge.process_manager.processes.keys())
                self.logger.info(f"准备清理 {len(processes_keys)} 个进程: {processes_keys}")
                
                for plugin_name in processes_keys:
                    try:
                        self.logger.info(f"正在停止插件: {plugin_name}")
                        self.plugin_bridge.process_manager.stop_plugin(plugin_name)
                    except Exception as e:
                        self.logger.warning(f"停止插件 {plugin_name} 时发生错误: {e}")
                
                # 清理所有进程
                processes_keys = list(self.plugin_bridge.process_manager.processes.keys())
                self.logger.info(f"准备清理 {len(processes_keys)} 个进程: {processes_keys}")
                
                for plugin_name in processes_keys:
                    self.logger.info(f"正在清理插件: {plugin_name}")
                    self.plugin_bridge.process_manager._cleanup_process(plugin_name)
                
                self.logger.info("进程管理器资源清理完成")
        except Exception as e:
            self.logger.warning(f"清理进程管理器时发生错误: {e}")
    
    def show_exit_confirmation_dialog(self, running_plugins):
        """显示退出确认对话框"""
        try:
            msg_box = QMessageBox()
            msg_box.setIcon(QMessageBox.Question)
            msg_box.setWindowTitle("确认退出")
            
            if running_plugins:
                plugin_list = "\n".join([f"• {name}" for name in running_plugins])
                msg_box.setText(f"检测到以下插件正在运行:\n\n{plugin_list}\n\n退出前将自动停止这些插件。\n\n是否确认退出？")
                msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
                msg_box.setDefaultButton(QMessageBox.Yes)
            else:
                msg_box.setText("确认退出应用程序？")
                msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
                msg_box.setDefaultButton(QMessageBox.Yes)
            
            result = msg_box.exec()
            return result == QMessageBox.Yes
            
        except Exception as e:
            self.logger.error(f"显示退出确认对话框失败: {e}")
            return True  # 如果对话框显示失败，默认允许退出
    
    def run(self):
        """运行应用程序"""
        try:
            self.logger.info("启动应用程序")
            
            # 记录启动信息
            self.logger.info(f"欢迎使用 {self.config_bridge.appName} v{self.config_bridge.appVersion}")
            self.logger.info("当前功能: 配置管理, 镜像源设置, 插件管理, Python环境管理")
            
            # 运行应用程序
            self.logger.info("开始运行QML应用程序主循环")
            exit_code = self.exec()
            
            # 保存配置
            self.config_bridge.saveConfig()
            
            self.logger.info(f"应用程序退出，退出码: {exit_code}")
            return exit_code
            
        except Exception as e:
            self.logger.critical(f"应用程序运行失败: {e}")
            self.show_error_dialog("运行失败", f"应用程序运行失败:\n{e}")
            return 1


def main():
    """主函数"""
    try:
        # 创建并运行应用程序
        app = MainApplication()
        return app.run()
        
    except Exception as e:
        print(f"启动失败: {e}")
        return 1


if __name__ == "__main__":
    # 设置环境变量
    os.environ.setdefault("QT_QPA_PLATFORM_PLUGIN_PATH", "")
    
    # 运行主程序
    sys.exit(main())
