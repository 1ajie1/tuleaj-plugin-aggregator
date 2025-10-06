import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import ConfigBridge 1.0

ApplicationWindow {
    id: mainWindow
    title: (configBridge ? configBridge.appName : "Tuleaj Plugin Aggregator") + " v" + (configBridge ? configBridge.appVersion : "1.0.0")
    width: Math.min(1200, Screen.width * 0.8)
    height: Math.min(800, Screen.height * 0.7)
    visible: true
    
    // 设置窗口属性
    minimumWidth: 800
    minimumHeight: 600

    // 窗口居中
    Component.onCompleted: {
        console.log("QML主窗口组件加载完成")
        mainWindow.x = (Screen.width - mainWindow.width) / 2
        mainWindow.y = (Screen.height - mainWindow.height) / 2
        
        // 连接配置桥接器信号
        if (configBridge) {
            console.log("configBridge可用，连接信号")
            configBridge.configError.connect(function(errorMessage) {
                console.log("配置错误:", errorMessage)
            })
            
            configBridge.configSaved.connect(function() {
                console.log("配置已保存")
            })
        } else {
            console.log("configBridge不可用")
        }
    }
    
    // 主背景色
    color: "#f8f9fa"
    
    // 设置窗口
    Loader {
        id: settingsLoader
        source: "SettingsWindow.qml"
        active: false
        
        onLoaded: {
            // 设置父窗口
            if (item) {
                // 不需要设置parent，ApplicationWindow会自动处理
            }
        }
    }
    
    // 文件选择器
    Loader {
        id: fileSelectorLoader
        source: "FileSelector.qml"
        active: false
        
        onLoaded: {
            // 连接信号
            if (item) {
                item.fileSelected.connect(function(filePath) {
                    console.log("选择的文件:", filePath)
                    showInfoMessage("插件安装", "正在安装插件: " + filePath, 3000)
                })
                item.cancelled.connect(function() {
                    console.log("取消选择文件")
                })
            }
        }
    }
    
    // 消息管理器
    MessageManager {
        id: messageManager
        anchors.fill: parent
    }
    
    // 消息提示函数
    function showMessage(title, message, type, duration) {
        console.log(title + ":", message)
        messageManager.addMessage(type || "info", title, message, duration || 3000)
    }
    
    // 便捷的消息显示函数
    function showSuccessMessage(title, message, duration) {
        messageManager.showSuccess(title, message, duration || 3000)
    }
    
    function showErrorMessage(title, message, duration) {
        messageManager.showError(title, message, duration || 5000)
    }
    
    function showWarningMessage(title, message, duration) {
        messageManager.showWarning(title, message, duration || 4000)
    }
    
    function showInfoMessage(title, message, duration) {
        messageManager.showInfo(title, message, duration || 3000)
    }
    
    // 显示设置窗口
    function showSettings() {
        settingsLoader.active = true
        if (settingsLoader.item) {
            settingsLoader.item.show()
        }
    }
    
    // 显示文件选择器
    function showFileSelector() {
        fileSelectorLoader.active = true
        if (fileSelectorLoader.item) {
            fileSelectorLoader.item.show()
        }
    }
    
    // 主布局容器
    Rectangle {
        anchors.fill: parent
        color: "#f8f9fa"
        
        RowLayout {
            anchors.fill: parent
            spacing: 0
            
            // 左侧插件列表面板
            PluginListPanel {
                id: pluginPanel
                Layout.preferredWidth: 300
                Layout.fillHeight: true
                messageManager: messageManager
                
                onPluginSelected: function(pluginName) {
                    documentViewer.loadPluginDocument(pluginName)
                }
                
                onPluginStartRequested: function(pluginName) {
                    console.log("主窗口收到启动插件请求:", pluginName)
                    // 只显示操作开始的通知，结果由状态变化通知处理
                    showInfoMessage("正在启动", pluginName + " 正在启动中...", 1500)
                }
                
                onPluginStopRequested: function(pluginName) {
                    console.log("主窗口收到停止插件请求:", pluginName)
                    // 只显示操作开始的通知，结果由状态变化通知处理
                    showInfoMessage("正在停止", pluginName + " 正在停止中...", 1500)
                }
                
                onPluginUninstallRequested: function(pluginName) {
                    console.log("主窗口收到卸载插件请求:", pluginName)
                    // 卸载操作需要特殊处理，因为会直接移除插件
                    showWarningMessage("正在卸载", pluginName + " 正在卸载中...", 2000)
                }
            }
            
            // 分隔线
            Rectangle {
                width: 1
                Layout.fillHeight: true
                color: "#e0e0e0"
            }
            
            // 右侧文档展示区域
            PluginDocumentViewer {
                id: documentViewer
                Layout.fillWidth: true
                Layout.fillHeight: true
                
                onSettingsRequested: {
                    showSettings()
                }
                
                onAddPluginRequested: {
                    showFileSelector()
                }
            }
        }
    }
}
