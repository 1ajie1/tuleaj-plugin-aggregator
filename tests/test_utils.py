#!/usr/bin/env python3
"""
测试日志和异常管理器
"""

import sys
from pathlib import Path

# 添加src目录到Python路径
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from utils.logger import Logger
from utils.exception_handler import ExceptionHandler


def test_logger():
    """测试日志管理器"""
    print("=== 测试日志管理器 ===")
    
    # 创建日志管理器
    logger = Logger(log_level="DEBUG", log_dir="test_logs")
    
    # 测试不同级别的日志
    logger.debug("这是一条调试信息")
    logger.info("这是一条信息")
    logger.warning("这是一条警告")
    logger.error("这是一条错误")
    logger.critical("这是一条严重错误")
    
    # 测试日志级别设置
    logger.set_level("WARNING")
    logger.debug("这条调试信息不应该显示")
    logger.warning("这条警告应该显示")
    
    # 测试插件日志器
    plugin_logger = logger.create_plugin_logger("test_plugin")
    plugin_logger.info("这是插件日志信息")
    
    # 测试日志文件路径
    log_file = logger.get_log_file_path()
    print(f"日志文件路径: {log_file}")
    
    # 测试异常统计
    stats = logger.get_exception_stats() if hasattr(logger, 'get_exception_stats') else "无统计功能"
    print(f"日志统计: {stats}")
    
    print("日志管理器测试完成\n")


def test_exception_handler():
    """测试异常管理器"""
    print("=== 测试异常管理器 ===")
    
    # 创建日志和异常管理器
    logger = Logger(log_level="DEBUG", log_dir="test_logs")
    exception_handler = ExceptionHandler(logger)
    
    # 测试基本异常处理
    try:
        raise ValueError("这是一个测试异常")
    except ValueError as e:
        exception_handler.handle_exception(e, "测试上下文")
    
    # 测试插件异常处理
    try:
        raise RuntimeError("这是插件异常")
    except RuntimeError as e:
        exception_handler.handle_plugin_exception("test_plugin", e)
    
    # 测试进程异常处理
    try:
        raise FileNotFoundError("这是进程异常")
    except FileNotFoundError as e:
        exception_handler.handle_process_exception("test_process", e)
    
    # 测试异常统计
    stats = exception_handler.get_exception_stats()
    print(f"异常统计: {stats}")
    
    # 测试插件专用异常处理器
    plugin_handler = exception_handler.create_plugin_exception_handler("my_plugin")
    try:
        raise KeyError("这是插件专用异常")
    except KeyError as e:
        plugin_handler.handle_exception(e, "插件操作")
    
    plugin_stats = plugin_handler.get_stats()
    print(f"插件异常统计: {plugin_stats}")
    
    # 测试异常频率限制
    print("测试异常频率限制...")
    for i in range(15):  # 超过默认的10个限制
        try:
            raise Exception(f"频率测试异常 {i}")
        except Exception as e:
            exception_handler.handle_exception(e, f"频率测试 {i}")
    
    print("异常管理器测试完成\n")


def test_error_callback():
    """测试错误回调功能"""
    print("=== 测试错误回调功能 ===")
    
    logger = Logger(log_level="INFO", log_dir="test_logs")
    exception_handler = ExceptionHandler(logger)
    
    # 定义回调函数
    callback_called = False
    callback_exception = None
    callback_context = None
    
    def test_callback(exception, context):
        nonlocal callback_called, callback_exception, callback_context
        callback_called = True
        callback_exception = exception
        callback_context = context
        print(f"回调函数被调用: {type(exception).__name__} - {context}")
    
    # 添加回调函数
    exception_handler.add_error_callback(test_callback)
    
    # 触发异常
    try:
        raise ValueError("测试回调异常")
    except ValueError as e:
        exception_handler.handle_exception(e, "回调测试")
    
    # 验证回调是否被调用
    if callback_called:
        print("✅ 错误回调功能正常")
    else:
        print("❌ 错误回调功能异常")
    
    # 移除回调函数
    exception_handler.remove_error_callback(test_callback)
    
    print("错误回调功能测试完成\n")


if __name__ == "__main__":
    print("开始测试日志和异常管理器...\n")
    
    try:
        test_logger()
        test_exception_handler()
        test_error_callback()
        
        print("✅ 所有测试完成！")
        
    except Exception as e:
        print(f"❌ 测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()
