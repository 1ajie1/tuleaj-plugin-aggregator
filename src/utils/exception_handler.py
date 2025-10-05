"""
异常管理器
提供统一的异常处理功能，包括全局异常捕获、用户友好提示、错误日志记录等
支持装饰器方式使用异常管理
"""

import traceback
import sys
import functools
from typing import Callable, Dict, Any, Optional
from PySide6.QtWidgets import QMessageBox, QApplication
from PySide6.QtCore import QObject, Signal


class ExceptionHandler(QObject):
    """异常管理器"""
    
    # 信号定义
    exception_occurred = Signal(str, str)  # 异常发生 (异常类型, 异常信息)
    plugin_exception_occurred = Signal(str, str, str)  # 插件异常 (插件名, 异常类型, 异常信息)
    process_exception_occurred = Signal(str, str, str)  # 进程异常 (进程名, 异常类型, 异常信息)
    
    def __init__(self, logger=None):
        """
        初始化异常管理器
        
        Args:
            logger: 日志管理器实例
        """
        super().__init__()
        self.logger = logger
        self.error_callbacks = []
        self.exception_count = 0
        self.max_exceptions_per_minute = 10  # 每分钟最大异常数
        self.exception_timestamps = []
        
        # 设置全局异常处理器
        sys.excepthook = self.handle_uncaught_exception
    
    def handle_exceptions(self, 
                         context: str = "", 
                         show_dialog: bool = True,
                         log_level: str = "ERROR",
                         reraise: bool = False,
                         return_value: Any = None):
        """
        异常处理装饰器
        
        Args:
            context: 异常上下文信息
            show_dialog: 是否显示错误对话框
            log_level: 日志级别
            reraise: 是否重新抛出异常
            return_value: 异常时的返回值
        """
        def decorator(func: Callable) -> Callable:
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    # 构建上下文信息
                    full_context = f"{context} - {func.__name__}" if context else func.__name__
                    
                    # 处理异常
                    self._handle_exception_with_options(
                        e, full_context, show_dialog, log_level, reraise
                    )
                    
                    # 返回指定值或None
                    return return_value
            
            return wrapper
        return decorator
    
    def handle_plugin_exceptions(self, 
                                plugin_name: str,
                                show_dialog: bool = True,
                                log_level: str = "ERROR",
                                reraise: bool = False,
                                return_value: Any = None):
        """
        插件异常处理装饰器
        
        Args:
            plugin_name: 插件名称
            show_dialog: 是否显示错误对话框
            log_level: 日志级别
            reraise: 是否重新抛出异常
            return_value: 异常时的返回值
        """
        def decorator(func: Callable) -> Callable:
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    # 处理插件异常
                    self._handle_exception_with_options(
                        e, f"插件 '{plugin_name}' - {func.__name__}", 
                        show_dialog, log_level, reraise
                    )
                    
                    # 发送插件异常信号
                    self.plugin_exception_occurred.emit(
                        plugin_name, type(e).__name__, str(e)
                    )
                    
                    return return_value
            
            return wrapper
        return decorator
    
    def handle_process_exceptions(self, 
                                 process_name: str,
                                 show_dialog: bool = True,
                                 log_level: str = "ERROR",
                                 reraise: bool = False,
                                 return_value: Any = None):
        """
        进程异常处理装饰器
        
        Args:
            process_name: 进程名称
            show_dialog: 是否显示错误对话框
            log_level: 日志级别
            reraise: 是否重新抛出异常
            return_value: 异常时的返回值
        """
        def decorator(func: Callable) -> Callable:
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    # 处理进程异常
                    self._handle_exception_with_options(
                        e, f"进程 '{process_name}' - {func.__name__}", 
                        show_dialog, log_level, reraise
                    )
                    
                    # 发送进程异常信号
                    self.process_exception_occurred.emit(
                        process_name, type(e).__name__, str(e)
                    )
                    
                    return return_value
            
            return wrapper
        return decorator
    
    def silent_exceptions(self, return_value: Any = None):
        """
        静默异常处理装饰器（不显示对话框，不记录日志）
        
        Args:
            return_value: 异常时的返回值
        """
        def decorator(func: Callable) -> Callable:
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                try:
                    return func(*args, **kwargs)
                except Exception:
                    return return_value
            
            return wrapper
        return decorator
    
    def retry_on_exception(self, 
                          max_retries: int = 3,
                          delay: float = 1.0,
                          exceptions: tuple = (Exception,),
                          context: str = ""):
        """
        异常重试装饰器
        
        Args:
            max_retries: 最大重试次数
            delay: 重试延迟时间（秒）
            exceptions: 需要重试的异常类型
            context: 上下文信息
        """
        def decorator(func: Callable) -> Callable:
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                last_exception = None
                
                for attempt in range(max_retries + 1):
                    try:
                        return func(*args, **kwargs)
                    except exceptions as e:
                        last_exception = e
                        
                        if attempt < max_retries:
                            if self.logger:
                                self.logger.warning(
                                    f"重试 {attempt + 1}/{max_retries} - {context or func.__name__}: {e}"
                                )
                            
                            import time
                            time.sleep(delay)
                        else:
                            # 最后一次尝试失败
                            full_context = f"{context} - {func.__name__}" if context else func.__name__
                            self.handle_exception(e, full_context)
                            raise e
                
                # 如果所有重试都失败了
                if last_exception:
                    raise last_exception
            
            return wrapper
        return decorator
    
    def _handle_exception_with_options(self, 
                                      exception: Exception, 
                                      context: str,
                                      show_dialog: bool,
                                      log_level: str,
                                      reraise: bool):
        """
        根据选项处理异常
        
        Args:
            exception: 异常对象
            context: 上下文信息
            show_dialog: 是否显示对话框
            log_level: 日志级别
            reraise: 是否重新抛出异常
        """
        # 检查异常频率限制
        if not self._check_exception_rate_limit():
            return
        
        # 记录日志
        if self.logger:
            exc_type = type(exception).__name__
            exc_message = str(exception)
            
            if log_level.upper() == "DEBUG":
                self.logger.debug(f"异常发生 - {context}: {exc_type}: {exc_message}")
            elif log_level.upper() == "INFO":
                self.logger.info(f"异常发生 - {context}: {exc_type}: {exc_message}")
            elif log_level.upper() == "WARNING":
                self.logger.warning(f"异常发生 - {context}: {exc_type}: {exc_message}")
            elif log_level.upper() == "CRITICAL":
                self.logger.critical(f"异常发生 - {context}: {exc_type}: {exc_message}")
            else:  # ERROR
                self.logger.error(f"异常发生 - {context}: {exc_type}: {exc_message}")
        
        # 发送信号
        self.exception_occurred.emit(type(exception).__name__, str(exception))
        
        # 执行回调函数
        for callback in self.error_callbacks:
            try:
                callback(exception, context)
            except Exception as e:
                if self.logger:
                    self.logger.error(f"错误回调执行失败: {e}")
        
        # 显示错误对话框
        if show_dialog:
            self._show_error_dialog(type(exception).__name__, str(exception), context)
        
        # 重新抛出异常
        if reraise:
            raise exception
    
    def add_error_callback(self, callback: Callable[[Exception, str], None]):
        """
        添加错误回调函数
        
        Args:
            callback: 错误回调函数，接收异常对象和上下文信息
        """
        self.error_callbacks.append(callback)
    
    def remove_error_callback(self, callback: Callable[[Exception, str], None]):
        """
        移除错误回调函数
        
        Args:
            callback: 要移除的回调函数
        """
        if callback in self.error_callbacks:
            self.error_callbacks.remove(callback)
    
    def handle_exception(self, exception: Exception, context: str = ""):
        """
        处理异常
        
        Args:
            exception: 异常对象
            context: 异常发生的上下文信息
        """
        try:
            # 检查异常频率限制
            if not self._check_exception_rate_limit():
                return
            
            # 获取异常信息
            exc_type = type(exception).__name__
            exc_message = str(exception)
            exc_traceback = traceback.format_exc()
            
            # 记录日志
            if self.logger:
                self.logger.error(f"异常发生 - {context}: {exc_type}: {exc_message}")
                self.logger.debug(f"异常堆栈:\n{exc_traceback}")
            
            # 发送信号
            self.exception_occurred.emit(exc_type, exc_message)
            
            # 执行回调函数
            for callback in self.error_callbacks:
                try:
                    callback(exception, context)
                except Exception as e:
                    if self.logger:
                        self.logger.error(f"错误回调执行失败: {e}")
            
            # 显示用户友好的错误信息
            self._show_error_dialog(exc_type, exc_message, context)
            
        except Exception as e:
            # 异常处理器本身出错时的处理
            print(f"异常处理器出错: {e}")
    
    def handle_plugin_exception(self, plugin_name: str, exception: Exception):
        """
        处理插件相关异常
        
        Args:
            plugin_name: 插件名称
            exception: 异常对象
        """
        context = f"插件 '{plugin_name}' 操作"
        
        # 记录插件异常
        if self.logger:
            self.logger.error(f"插件异常 - {plugin_name}: {type(exception).__name__}: {str(exception)}")
        
        # 发送插件异常信号
        self.plugin_exception_occurred.emit(plugin_name, type(exception).__name__, str(exception))
        
        # 处理异常
        self.handle_exception(exception, context)
    
    def handle_process_exception(self, process_name: str, exception: Exception):
        """
        处理进程相关异常
        
        Args:
            process_name: 进程名称
            exception: 异常对象
        """
        context = f"进程 '{process_name}' 操作"
        
        # 记录进程异常
        if self.logger:
            self.logger.error(f"进程异常 - {process_name}: {type(exception).__name__}: {str(exception)}")
        
        # 发送进程异常信号
        self.process_exception_occurred.emit(process_name, type(exception).__name__, str(exception))
        
        # 处理异常
        self.handle_exception(exception, context)
    
    def handle_uncaught_exception(self, exc_type, exc_value, exc_traceback):
        """
        处理未捕获的异常
        
        Args:
            exc_type: 异常类型
            exc_value: 异常值
            exc_traceback: 异常堆栈
        """
        if issubclass(exc_type, KeyboardInterrupt):
            # 不处理键盘中断
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return
        
        # 创建异常对象
        exception = exc_type(exc_value)
        
        # 处理异常
        self.handle_exception(exception, "未捕获的异常")
    
    def _check_exception_rate_limit(self) -> bool:
        """
        检查异常频率限制
        
        Returns:
            bool: 是否允许处理异常
        """
        import time
        current_time = time.time()
        
        # 清理一分钟前的异常记录
        self.exception_timestamps = [
            timestamp for timestamp in self.exception_timestamps
            if current_time - timestamp < 60
        ]
        
        # 检查是否超过频率限制
        if len(self.exception_timestamps) >= self.max_exceptions_per_minute:
            if self.logger:
                self.logger.warning("异常频率过高，已限制异常处理 (每分钟最多 {} 个)".format(self.max_exceptions_per_minute))
            return False
        
        # 记录当前异常时间戳
        self.exception_timestamps.append(current_time)
        return True
    
    def _show_error_dialog(self, exc_type: str, exc_message: str, context: str):
        """
        显示错误对话框
        
        Args:
            exc_type: 异常类型
            exc_message: 异常信息
            context: 上下文信息
        """
        try:
            # 确保有QApplication实例
            app = QApplication.instance()
            if not app:
                print("无法显示错误对话框 - 没有QApplication实例")
                print(f"错误类型: {exc_type}")
                print(f"错误信息: {exc_message}")
                return
            
            msg_box = QMessageBox()
            msg_box.setIcon(QMessageBox.Critical)
            msg_box.setWindowTitle("错误")
            
            if context:
                msg_box.setText(f"在 {context} 时发生错误")
            else:
                msg_box.setText("发生错误")
            
            # 设置详细错误信息
            detailed_text = f"错误类型: {exc_type}\n错误信息: {exc_message}"
            msg_box.setDetailedText(detailed_text)
            
            # 设置按钮
            msg_box.setStandardButtons(QMessageBox.Ok)
            
            # 显示对话框
            msg_box.exec()
            
        except Exception as e:
            # 如果无法显示对话框，则打印到控制台
            print(f"无法显示错误对话框: {e}")
            print(f"错误类型: {exc_type}")
            print(f"错误信息: {exc_message}")
    
    def set_max_exceptions_per_minute(self, max_count: int):
        """
        设置每分钟最大异常处理数量
        
        Args:
            max_count: 最大异常数量
        """
        self.max_exceptions_per_minute = max_count
    
    def get_exception_stats(self) -> Dict[str, Any]:
        """
        获取异常统计信息
        
        Returns:
            Dict: 异常统计信息
        """
        return {
            "total_exceptions": self.exception_count,
            "exceptions_last_minute": len(self.exception_timestamps),
            "max_exceptions_per_minute": self.max_exceptions_per_minute,
            "error_callbacks_count": len(self.error_callbacks)
        }
    
    def reset_stats(self):
        """重置异常统计信息"""
        self.exception_count = 0
        self.exception_timestamps.clear()
    
    def create_plugin_exception_handler(self, plugin_name: str):
        """
        为插件创建专用的异常处理器
        
        Args:
            plugin_name: 插件名称
            
        Returns:
            PluginExceptionHandler: 插件异常处理器
        """
        return PluginExceptionHandler(plugin_name, self)


class PluginExceptionHandler:
    """插件专用异常处理器"""
    
    def __init__(self, plugin_name: str, main_handler: ExceptionHandler):
        """
        初始化插件异常处理器
        
        Args:
            plugin_name: 插件名称
            main_handler: 主异常处理器
        """
        self.plugin_name = plugin_name
        self.main_handler = main_handler
        self.plugin_exception_count = 0
    
    def handle_exception(self, exception: Exception, context: str = ""):
        """
        处理插件异常
        
        Args:
            exception: 异常对象
            context: 上下文信息
        """
        self.plugin_exception_count += 1
        self.main_handler.handle_plugin_exception(self.plugin_name, exception)
    
    def get_stats(self) -> Dict[str, Any]:
        """
        获取插件异常统计信息
        
        Returns:
            Dict: 插件异常统计信息
        """
        return {
            "plugin_name": self.plugin_name,
            "exception_count": self.plugin_exception_count
        }


# 全局异常处理器实例
_global_exception_handler: Optional[ExceptionHandler] = None


def set_global_exception_handler(handler: ExceptionHandler):
    """设置全局异常处理器"""
    global _global_exception_handler
    _global_exception_handler = handler


def get_global_exception_handler() -> Optional[ExceptionHandler]:
    """获取全局异常处理器"""
    return _global_exception_handler


# 便捷的全局装饰器函数
def handle_exceptions(context: str = "", 
                     show_dialog: bool = True,
                     log_level: str = "ERROR",
                     reraise: bool = False,
                     return_value: Any = None):
    """
    全局异常处理装饰器
    
    Args:
        context: 异常上下文信息
        show_dialog: 是否显示错误对话框
        log_level: 日志级别
        reraise: 是否重新抛出异常
        return_value: 异常时的返回值
    """
    def decorator(func: Callable) -> Callable:
        if _global_exception_handler:
            return _global_exception_handler.handle_exceptions(
                context, show_dialog, log_level, reraise, return_value
            )(func)
        else:
            # 如果没有全局异常处理器，使用简单的异常处理
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    print(f"异常发生 - {context or func.__name__}: {e}")
                    if reraise:
                        raise e
                    return return_value
            return wrapper
    return decorator


def handle_plugin_exceptions(plugin_name: str,
                            show_dialog: bool = True,
                            log_level: str = "ERROR",
                            reraise: bool = False,
                            return_value: Any = None):
    """
    全局插件异常处理装饰器
    
    Args:
        plugin_name: 插件名称
        show_dialog: 是否显示错误对话框
        log_level: 日志级别
        reraise: 是否重新抛出异常
        return_value: 异常时的返回值
    """
    def decorator(func: Callable) -> Callable:
        if _global_exception_handler:
            return _global_exception_handler.handle_plugin_exceptions(
                plugin_name, show_dialog, log_level, reraise, return_value
            )(func)
        else:
            # 如果没有全局异常处理器，使用简单的异常处理
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    print(f"插件异常 - {plugin_name} - {func.__name__}: {e}")
                    if reraise:
                        raise e
                    return return_value
            return wrapper
    return decorator


def handle_process_exceptions(process_name: str,
                             show_dialog: bool = True,
                             log_level: str = "ERROR",
                             reraise: bool = False,
                             return_value: Any = None):
    """
    全局进程异常处理装饰器
    
    Args:
        process_name: 进程名称
        show_dialog: 是否显示错误对话框
        log_level: 日志级别
        reraise: 是否重新抛出异常
        return_value: 异常时的返回值
    """
    def decorator(func: Callable) -> Callable:
        if _global_exception_handler:
            return _global_exception_handler.handle_process_exceptions(
                process_name, show_dialog, log_level, reraise, return_value
            )(func)
        else:
            # 如果没有全局异常处理器，使用简单的异常处理
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    print(f"进程异常 - {process_name} - {func.__name__}: {e}")
                    if reraise:
                        raise e
                    return return_value
            return wrapper
    return decorator


def silent_exceptions(return_value: Any = None):
    """
    全局静默异常处理装饰器
    
    Args:
        return_value: 异常时的返回值
    """
    def decorator(func: Callable) -> Callable:
        if _global_exception_handler:
            return _global_exception_handler.silent_exceptions(return_value)(func)
        else:
            # 如果没有全局异常处理器，使用简单的异常处理
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                try:
                    return func(*args, **kwargs)
                except Exception:
                    return return_value
            return wrapper
    return decorator


def retry_on_exception(max_retries: int = 3,
                      delay: float = 1.0,
                      exceptions: tuple = (Exception,),
                      context: str = ""):
    """
    全局异常重试装饰器
    
    Args:
        max_retries: 最大重试次数
        delay: 重试延迟时间（秒）
        exceptions: 需要重试的异常类型
        context: 上下文信息
    """
    def decorator(func: Callable) -> Callable:
        if _global_exception_handler:
            return _global_exception_handler.retry_on_exception(
                max_retries, delay, exceptions, context
            )(func)
        else:
            # 如果没有全局异常处理器，使用简单的重试逻辑
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                last_exception = None
                
                for attempt in range(max_retries + 1):
                    try:
                        return func(*args, **kwargs)
                    except exceptions as e:
                        last_exception = e
                        
                        if attempt < max_retries:
                            print(f"重试 {attempt + 1}/{max_retries} - {context or func.__name__}: {e}")
                            import time
                            time.sleep(delay)
                        else:
                            raise e
                
                if last_exception:
                    raise last_exception
            
            return wrapper
    return decorator
