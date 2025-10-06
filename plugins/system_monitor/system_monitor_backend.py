#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
系统监控插件后端
读取 CPU、内存和网络速度信息
"""

import psutil
import time
import threading
from PySide6.QtCore import QObject, Signal, QTimer
from PySide6.QtQml import qmlRegisterType


class SystemMonitorBackend(QObject):
    """系统监控后端类"""
    
    # 信号定义
    cpuUsageChanged = Signal(float)  # CPU 使用率
    memoryUsageChanged = Signal(float)  # 内存使用率
    memoryTotalChanged = Signal(int)  # 总内存 (MB)
    memoryUsedChanged = Signal(int)  # 已用内存 (MB)
    networkSpeedChanged = Signal(float, float)  # 下载速度, 上传速度 (MB/s)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # 初始化网络监控
        self.last_bytes_sent = 0
        self.last_bytes_recv = 0
        self.last_time = time.time()
        
        # 创建定时器
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_system_info)
        self.timer.start(1000)  # 每秒更新一次
        
        # 初始化网络统计
        self.init_network_stats()
        
        # 立即更新一次
        self.update_system_info()
    
    def init_network_stats(self):
        """初始化网络统计"""
        net_io = psutil.net_io_counters()
        self.last_bytes_sent = net_io.bytes_sent
        self.last_bytes_recv = net_io.bytes_recv
        self.last_time = time.time()
    
    def update_system_info(self):
        """更新系统信息"""
        try:
            # 更新 CPU 使用率
            cpu_percent = psutil.cpu_percent(interval=0.1)
            self.cpuUsageChanged.emit(cpu_percent)
            
            # 更新内存信息
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            memory_total_mb = memory.total // (1024 * 1024)
            memory_used_mb = memory.used // (1024 * 1024)
            
            self.memoryUsageChanged.emit(memory_percent)
            self.memoryTotalChanged.emit(memory_total_mb)
            self.memoryUsedChanged.emit(memory_used_mb)
            
            # 更新网络速度
            self.update_network_speed()
            
        except Exception as e:
            print(f"更新系统信息时出错: {e}")
    
    def update_network_speed(self):
        """更新网络速度"""
        try:
            current_time = time.time()
            net_io = psutil.net_io_counters()
            
            # 计算时间差
            time_diff = current_time - self.last_time
            if time_diff > 0:
                # 计算速度 (字节/秒)
                bytes_sent_diff = net_io.bytes_sent - self.last_bytes_sent
                bytes_recv_diff = net_io.bytes_recv - self.last_bytes_recv
                
                # 转换为 MB/s
                upload_speed = (bytes_sent_diff / time_diff) / (1024 * 1024)
                download_speed = (bytes_recv_diff / time_diff) / (1024 * 1024)
                
                self.networkSpeedChanged.emit(download_speed, upload_speed)
            
            # 更新统计信息
            self.last_bytes_sent = net_io.bytes_sent
            self.last_bytes_recv = net_io.bytes_recv
            self.last_time = current_time
            
        except Exception as e:
            print(f"更新网络速度时出错: {e}")
    
    def get_cpu_count(self):
        """获取 CPU 核心数"""
        return psutil.cpu_count()
    
    def get_cpu_freq(self):
        """获取 CPU 频率"""
        try:
            freq = psutil.cpu_freq()
            return freq.current if freq else 0
        except:
            return 0
    
    def get_boot_time(self):
        """获取系统启动时间"""
        try:
            return psutil.boot_time()
        except:
            return 0


# 注册 QML 类型
def register_types():
    """注册 QML 类型"""
    qmlRegisterType(SystemMonitorBackend, "SystemMonitor", 1, 0, "SystemMonitorBackend")


if __name__ == "__main__":
    # 测试代码
    import sys
    from PySide6.QtCore import QCoreApplication
    
    app = QCoreApplication(sys.argv)
    
    monitor = SystemMonitorBackend()
    
    # 连接信号到打印函数
    monitor.cpuUsageChanged.connect(lambda x: print(f"CPU: {x:.1f}%"))
    monitor.memoryUsageChanged.connect(lambda x: print(f"内存: {x:.1f}%"))
    monitor.networkSpeedChanged.connect(lambda d, u: print(f"网络: 下载 {d:.2f} MB/s, 上传 {u:.2f} MB/s"))
    
    print("系统监控插件测试")
    print("按 Ctrl+C 退出")
    
    try:
        app.exec()
    except KeyboardInterrupt:
        print("\n退出测试")
