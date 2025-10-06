#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
插件进程管理器
专门负责插件的进程生命周期管理
"""

from typing import Dict, Optional, Any
from PySide6.QtCore import QObject, Signal, QProcess, QTimer
from PySide6.QtQml import qmlRegisterType

# 导入日志和异常处理模块
from utils.logger import Logger
from utils.exception_handler import ExceptionHandler, handle_process_exceptions


class PluginProcessManager(QObject):
    """插件进程管理器"""
    
    # 信号定义
    processStarted = Signal(str)  # 进程启动成功 (plugin_name)
    processFinished = Signal(str, int, int)  # 进程结束 (plugin_name, exit_code, exit_status)
    processError = Signal(str, str)  # 进程错误 (plugin_name, error_message)
    processOutput = Signal(str, str, str)  # 进程输出 (plugin_name, output_type, output)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.processes: Dict[str, QProcess] = {}  # 存储运行中的进程
        self.process_info: Dict[str, Dict[str, Any]] = {}  # 存储进程信息
        self.starting_processes: set = set()  # 正在启动的进程集合
        self.stopping_processes: set = set()  # 正在停止的进程集合
        
        # 初始化日志管理器
        self.logger = Logger(log_level="INFO", log_dir="logs")
        
        # 初始化异常处理器
        self.exception_handler = ExceptionHandler(self.logger)
        
        # 设置全局异常处理器
        from utils.exception_handler import set_global_exception_handler
        set_global_exception_handler(self.exception_handler)
        
        self.logger.info("插件进程管理器初始化完成")
        
    @handle_process_exceptions("插件进程启动", show_dialog=False, log_level="ERROR", return_value=False)
    def start_plugin(self, plugin_name: str, python_path: str, script_path: str, 
                    working_dir: str, env_vars: Dict[str, str] = None) -> bool:
        """
        启动插件进程
        
        Args:
            plugin_name: 插件名称
            python_path: Python解释器路径
            script_path: 脚本文件路径
            working_dir: 工作目录
            env_vars: 环境变量字典
            
        Returns:
            bool: 是否成功启动
        """
        self.logger.info(f"开始启动插件: {plugin_name}")
        
        # 检查插件是否已经在运行
        if plugin_name in self.processes:
            self.logger.warning(f"插件 {plugin_name} 已经在运行中")
            self.processError.emit(plugin_name, "插件已经在运行中")
            return False
        
        # 创建进程
        process = QProcess(self)
        
        # 设置进程信息
        self.process_info[plugin_name] = {
            'python_path': python_path,
            'script_path': script_path,
            'working_dir': working_dir,
            'env_vars': env_vars or {},
            'start_time': None,
            'pid': None
        }
        
        # 设置进程参数
        process.setProgram(python_path)
        process.setArguments([script_path])
        process.setWorkingDirectory(working_dir)
        
        # 设置环境变量
        if env_vars:
            env = process.processEnvironment()
            for key, value in env_vars.items():
                env.insert(key, value)
            process.setProcessEnvironment(env)
        
        # 先添加到正在启动的进程集合
        self.starting_processes.add(plugin_name)
        
        # 连接信号
        self._connect_process_signals(process, plugin_name)
        
        # 启动进程
        self.logger.info(f"准备启动进程: {plugin_name}")
        start_result = process.start()
        self.logger.info(f"process.start() 返回: {start_result}")
        
        # 处理 start() 返回 None 的情况
        if start_result is None:
            self.logger.warning("process.start() 返回 None，检查进程状态")
            # 如果返回 None，检查进程是否实际启动了
            if process.state() in [QProcess.ProcessState.Starting, QProcess.ProcessState.Running]:
                self.logger.info(f"进程实际已启动，状态: {process.state()}")
                start_result = True
            else:
                self.logger.error(f"进程启动失败，状态: {process.state()}")
                start_result = False
        
        if start_result:
            self.processes[plugin_name] = process
            self.process_info[plugin_name]['pid'] = process.processId()
            self.process_info[plugin_name]['start_time'] = QTimer().remainingTime()
            
            self.logger.info(f"插件 {plugin_name} 进程启动命令已发送，PID: {process.processId()}")
            return True
        else:
            # 只有在 process.start() 返回 False 时才认为是真正的启动失败
            error_msg = f"启动插件失败: {process.errorString()}"
            self.logger.error(error_msg)
            self.processError.emit(plugin_name, error_msg)
            self._cleanup_process(plugin_name)
            return False
    
    @handle_process_exceptions("插件进程停止", show_dialog=False, log_level="ERROR", return_value=False)
    def stop_plugin(self, plugin_name: str) -> bool:
        """
        停止插件进程
        
        Args:
            plugin_name: 插件名称
            
        Returns:
            bool: 是否成功停止
        """
        self.logger.info(f"开始停止插件: {plugin_name}")
        
        if plugin_name not in self.processes:
            self.logger.warning(f"插件 {plugin_name} 不在运行列表中")
            return False
        
        # 添加到正在停止的进程集合
        self.stopping_processes.add(plugin_name)
        
        process = self.processes[plugin_name]
        
        # 尝试优雅停止
        self.logger.info(f"发送终止信号给插件 {plugin_name}")
        process.terminate()
        
        # 等待进程结束
        if not process.waitForFinished(5000):  # 等待5秒
            # 强制杀死进程
            self.logger.warning(f"插件 {plugin_name} 优雅停止超时，强制终止")
            process.kill()
            process.waitForFinished(1000)  # 等待1秒
        
        self.logger.info(f"插件 {plugin_name} 进程已停止")
        return True
    
    def is_plugin_running(self, plugin_name: str) -> bool:
        """
        检查插件是否在运行
        
        Args:
            plugin_name: 插件名称
            
        Returns:
            bool: 是否在运行
        """
        if plugin_name not in self.processes:
            return False
        
        process = self.processes[plugin_name]
        return process.state() == QProcess.ProcessState.Running
    
    def get_plugin_process(self, plugin_name: str) -> Optional[QProcess]:
        """
        获取插件进程对象
        
        Args:
            plugin_name: 插件名称
            
        Returns:
            QProcess: 进程对象，如果不存在则返回None
        """
        return self.processes.get(plugin_name)
    
    def get_plugin_info(self, plugin_name: str) -> Optional[Dict[str, Any]]:
        """
        获取插件进程信息
        
        Args:
            plugin_name: 插件名称
            
        Returns:
            Dict: 进程信息字典
        """
        return self.process_info.get(plugin_name)
    
    def get_all_running_plugins(self) -> list:
        """
        获取所有运行中的插件名称列表
        
        Returns:
            list: 插件名称列表
        """
        return list(self.processes.keys())
    
    def _connect_process_signals(self, process: QProcess, plugin_name: str):
        """连接进程信号"""
        # 进程启动成功
        process.started.connect(lambda: self._on_process_started(plugin_name))
        
        # 进程结束
        process.finished.connect(lambda exit_code, exit_status: self._on_process_finished(plugin_name, exit_code, exit_status))
        
        # 进程错误
        process.errorOccurred.connect(lambda error: self._on_process_error(plugin_name, error))
        
        # 标准输出
        process.readyReadStandardOutput.connect(
            lambda: self._on_process_output(plugin_name, "stdout", process.readAllStandardOutput().data().decode('utf-8', errors='replace'))
        )
        
        # 标准错误输出
        process.readyReadStandardError.connect(
            lambda: self._on_process_output(plugin_name, "stderr", process.readAllStandardError().data().decode('utf-8', errors='replace'))
        )
    
    def _on_process_started(self, plugin_name: str):
        """进程启动成功回调"""
        self.logger.info(f"插件 {plugin_name} 进程启动成功")
        
        # 从正在启动的进程集合中移除
        self.starting_processes.discard(plugin_name)
        
        # 延迟验证进程是否真正启动成功
        QTimer.singleShot(1000, lambda: self._verify_process_startup(plugin_name))
        
        # 立即发送启动信号
        self.processStarted.emit(plugin_name)
    
    def _verify_process_startup(self, plugin_name: str):
        """验证进程是否真正启动成功"""
        if plugin_name not in self.processes:
            self.logger.warning(f"插件 {plugin_name} 在验证时不在进程列表中")
            return
        
        process = self.processes[plugin_name]
        process_state = process.state()
        
        if process_state == QProcess.ProcessState.Running:
            self.logger.info(f"插件 {plugin_name} 启动验证成功，进程正在运行")
            # 确保状态为 running
            self.processStarted.emit(plugin_name)
        else:
            self.logger.warning(f"插件 {plugin_name} 启动验证失败，进程状态: {process_state}")
            # 如果进程没有真正运行，发送错误信号
            self.processError.emit(plugin_name, f"进程启动验证失败，状态: {process_state}")
            self._cleanup_process(plugin_name)
    
    def _on_process_finished(self, plugin_name: str, exit_code: int, exit_status: int):
        """进程结束回调"""
        self.logger.info(f"插件 {plugin_name} 进程结束，退出码: {exit_code}, 状态: {exit_status}")
        self.processFinished.emit(plugin_name, exit_code, exit_status)
        self._cleanup_process(plugin_name)
    
    def _on_process_error(self, plugin_name: str, error: int):
        """进程错误回调"""
        error_type = QProcess.ProcessError(error)
        self.logger.warning(f"插件 {plugin_name} 进程错误: {error} ({error_type})")
        
        # 调试信息：打印启动状态
        self.logger.debug(f"插件 {plugin_name} 启动状态检查: starting_processes={self.starting_processes}")
        
        # 如果进程正在启动中，忽略启动过程中的错误
        if plugin_name in self.starting_processes:
            self.logger.info(f"插件 {plugin_name} 正在启动中，忽略启动过程中的错误: {error_type}")
            return
        
        # 如果进程正在停止中，忽略停止过程中的错误
        if plugin_name in self.stopping_processes:
            self.logger.info(f"插件 {plugin_name} 正在停止中，忽略停止过程中的错误: {error_type}")
            return
        
        # 检查进程是否还在运行
        if plugin_name in self.processes:
            process = self.processes[plugin_name]
            process_state = process.state()
            
            # 如果进程仍在运行或正在启动，忽略错误
            if process_state in [QProcess.ProcessState.Running, QProcess.ProcessState.Starting]:
                self.logger.info(f"插件 {plugin_name} 进程仍在运行/启动中，忽略错误: {error_type}")
                return
            
            # 检查是否是启动过程中的临时错误
            if error_type in [QProcess.ProcessError.FailedToStart, QProcess.ProcessError.Crashed]:
                # 如果进程状态不是 NotRunning，说明进程实际上启动了
                if process_state != QProcess.ProcessState.NotRunning:
                    self.logger.info(f"插件 {plugin_name} 启动过程中的临时错误，进程实际已启动: {error_type}")
                    return
        
        # 只有在进程真正失败时才发送错误信号
        self.logger.error(f"插件 {plugin_name} 进程真正失败: {error_type}")
        self.processError.emit(plugin_name, f"进程错误: {error_type}")
        self._cleanup_process(plugin_name)
    
    def _on_process_output(self, plugin_name: str, output_type: str, output: str):
        """进程输出回调"""
        if output.strip():
            self.logger.debug(f"插件 {plugin_name} {output_type}: {output.strip()}")
            self.processOutput.emit(plugin_name, output_type, output)
    
    def _cleanup_process(self, plugin_name: str):
        """清理进程资源"""
        # 从正在启动的进程集合中移除
        self.starting_processes.discard(plugin_name)
        
        # 从正在停止的进程集合中移除
        self.stopping_processes.discard(plugin_name)
        
        # 清理进程对象
        if plugin_name in self.processes:
            del self.processes[plugin_name]
        
        # 清理进程信息
        if plugin_name in self.process_info:
            del self.process_info[plugin_name]
        
        self.logger.info(f"插件 {plugin_name} 进程资源已清理")


# 注册QML类型
qmlRegisterType(PluginProcessManager, "PluginProcessManager", 1, 0, "PluginProcessManager")
