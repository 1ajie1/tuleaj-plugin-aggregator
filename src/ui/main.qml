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
                    showMessage("插件安装", "正在安装插件: " + filePath)
                })
                item.cancelled.connect(function() {
                    console.log("取消选择文件")
                })
            }
        }
    }
    
    // 消息提示函数
    function showMessage(title, message) {
        // 简单的消息提示，可以后续优化为更好的通知组件
        console.log(title + ":", message)
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
                
                onPluginSelected: function(pluginName) {
                    documentViewer.loadPluginDocument(pluginName)
                }
                
                onPluginStartRequested: function(pluginName) {
                    console.log("启动插件:", pluginName)
                    // TODO: 实现插件启动逻辑
                }
                
                onPluginStopRequested: function(pluginName) {
                    console.log("停止插件:", pluginName)
                    // TODO: 实现插件停止逻辑
                }
                
                onPluginUninstallRequested: function(pluginName) {
                    console.log("卸载插件:", pluginName)
                    // TODO: 实现插件卸载逻辑
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
