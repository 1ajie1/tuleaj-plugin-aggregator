"""
日志管理器
提供统一的日志记录功能，支持多级别日志、文件输出、控制台输出等
"""

import logging
from pathlib import Path
from datetime import datetime
import sys


class Logger:
    """日志管理器"""
    
    def __init__(self, log_level: str = "INFO", log_dir: str = "logs"):
        """
        初始化日志管理器
        
        Args:
            log_level: 日志级别 (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            log_dir: 日志文件目录
        """
        self.log_level = getattr(logging, log_level.upper())
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        
        # 设置日志格式（包含调用位置的文件名和行号）
        self.formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(pathname)s:%(lineno)d - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # 创建根日志器
        self.logger = logging.getLogger("tuleaj_plugin_aggregator")
        self.logger.setLevel(self.log_level)
        
        # 清除现有处理器
        self.logger.handlers.clear()
        
        # 添加控制台处理器
        self._setup_console_handler()
        
        # 添加文件处理器
        self._setup_file_handler()
    
    def _setup_console_handler(self):
        """设置控制台处理器"""
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(self.log_level)
        console_handler.setFormatter(self.formatter)
        self.logger.addHandler(console_handler)
    
    def _setup_file_handler(self):
        """设置文件处理器"""
        # 按日期创建日志文件
        log_file = self.log_dir / f"app_{datetime.now().strftime('%Y%m%d')}.log"
        
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(self.log_level)
        file_handler.setFormatter(self.formatter)
        self.logger.addHandler(file_handler)
    
    def debug(self, message: str):
        """记录调试信息"""
        self._log_with_caller(logging.DEBUG, message)
    
    def info(self, message: str):
        """记录信息"""
        self._log_with_caller(logging.INFO, message)
    
    def warning(self, message: str):
        """记录警告"""
        self._log_with_caller(logging.WARNING, message)
    
    def error(self, message: str):
        """记录错误"""
        self._log_with_caller(logging.ERROR, message)
    
    def critical(self, message: str):
        """记录严重错误"""
        self._log_with_caller(logging.CRITICAL, message)
    
    def _log_with_caller(self, level: int, message: str):
        """使用真正的调用者信息记录日志"""
        # 获取调用者的帧信息
        import inspect
        frame = inspect.currentframe()
        try:
            # 跳过当前方法(_log_with_caller)和Logger方法(info/debug等)，找到真正的调用者
            caller_frame = frame.f_back.f_back
            filename = caller_frame.f_code.co_filename
            lineno = caller_frame.f_lineno
            
            # 创建日志记录
            record = self.logger.makeRecord(
                self.logger.name, level, filename, lineno, message, (), None
            )
            self.logger.handle(record)
        finally:
            del frame
    
    def set_level(self, level: str):
        """设置日志级别"""
        self.log_level = getattr(logging, level.upper())
        self.logger.setLevel(self.log_level)
        for handler in self.logger.handlers:
            handler.setLevel(self.log_level)
    
    def get_log_file_path(self) -> str:
        """获取当前日志文件路径"""
        log_file = self.log_dir / f"app_{datetime.now().strftime('%Y%m%d')}.log"
        return str(log_file)
    
    def clear_old_logs(self, days: int = 7):
        """清理旧日志文件"""
        try:
            current_time = datetime.now()
            for log_file in self.log_dir.glob("app_*.log"):
                file_time = datetime.fromtimestamp(log_file.stat().st_mtime)
                if (current_time - file_time).days > days:
                    log_file.unlink()
                    self.info(f"已删除旧日志文件: {log_file.name}")
        except Exception as e:
            self.error(f"清理旧日志文件失败: {e}")
    
    def create_plugin_logger(self, plugin_name: str) -> logging.Logger:
        """为插件创建专用日志器"""
        plugin_logger = logging.getLogger(f"tuleaj_plugin_aggregator.plugin.{plugin_name}")
        plugin_logger.setLevel(self.log_level)
        
        # 添加插件专用文件处理器
        plugin_log_file = self.log_dir / f"plugin_{plugin_name}_{datetime.now().strftime('%Y%m%d')}.log"
        plugin_handler = logging.FileHandler(plugin_log_file, encoding='utf-8')
        plugin_handler.setLevel(self.log_level)
        plugin_handler.setFormatter(self.formatter)
        plugin_logger.addHandler(plugin_handler)
        
        return plugin_logger
