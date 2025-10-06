"""
Tuleaj Plugin Aggregator 主程序
PySide6 QML 插件聚合工具的主入口
"""

import sys
import os
from pathlib import Path
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtWidgets import QApplication, QMessageBox

# 添加src目录到Python路径
sys.path.insert(0, str(Path(__file__).parent))

# 导入核心模块
from core.config_bridge import ConfigBridge, register_qml_types
from core.plugin_bridge import register_types as register_plugin_types
from utils.logger import Logger
from utils.exception_handler import ExceptionHandler, set_global_exception_handler


class MainApplication:
    """主应用程序类"""
    
    def __init__(self):
        """初始化应用程序"""
        # 创建应用程序实例
        self.app = QApplication(sys.argv)
        self.app.setApplicationName("Tuleaj Plugin Aggregator")
        self.app.setApplicationVersion("1.0.0")
        self.app.setOrganizationName("Tuleaj")
        
        # 初始化日志和异常处理器
        self.logger = Logger(log_level="INFO")
        self.exception_handler = ExceptionHandler(self.logger)
        set_global_exception_handler(self.exception_handler)
        
        # 初始化配置桥接器
        self.config_bridge = ConfigBridge()
        
        # 注册QML类型
        register_qml_types()
        register_plugin_types()
        
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
        
        self.logger.info("应用程序初始化完成")
    
    def setup_qml_context(self):
        """设置QML上下文属性"""
        # 将配置桥接器暴露给QML
        self.engine.rootContext().setContextProperty("configBridge", self.config_bridge)
        
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
    
    def run(self):
        """运行应用程序"""
        try:
            self.logger.info("启动应用程序")
            
            # 记录启动信息
            self.logger.info(f"欢迎使用 {self.config_bridge.appName} v{self.config_bridge.appVersion}")
            self.logger.info("当前功能: 配置管理, 镜像源设置, 插件管理, Python环境管理")
            
            # 运行应用程序
            self.logger.info("开始运行QML应用程序主循环")
            exit_code = self.app.exec()
            
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
