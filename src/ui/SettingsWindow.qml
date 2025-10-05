import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import ConfigBridge 1.0

ApplicationWindow {
    id: settingsWindow
    title: "设置 - " + (configBridge ? configBridge.appName : "Tuleaj Plugin Aggregator")
    width: Math.min(600, Screen.width * 0.8)
    height: Math.min(650, Screen.height * 0.7)
    minimumWidth: 550
    minimumHeight: 400
    visible: false
    modality: Qt.ApplicationModal
    
    // 当窗口显示时重新居中
    onVisibleChanged: {
        if (visible) {
            centerWindow()
        }
    }
    
    // 窗口居中函数
    function centerWindow() {
        // 确保窗口完全居中显示
        settingsWindow.x = Math.max(0, (Screen.width - settingsWindow.width) / 2)
        settingsWindow.y = Math.max(0, (Screen.height - settingsWindow.height) / 2)
    }
    
    // 窗口居中
    Component.onCompleted: {
        centerWindow()
        
        // 连接配置桥接器信号
        if (configBridge) {
            configBridge.configError.connect(function(errorMessage) {
                console.log("设置错误:", errorMessage)
            })
            
            configBridge.configSaved.connect(function() {
                console.log("设置已保存")
            })
            
            // 连接Python环境管理信号
            configBridge.environmentCreated.connect(function(envName, success, message) {
                console.log("环境创建:", envName, success, message)
                if (success) {
                    // 可以显示成功消息
                } else {
                    // 可以显示错误消息
                }
            })
            
            configBridge.environmentDeleted.connect(function(envName, success, message) {
                console.log("环境删除:", envName, success, message)
                if (success) {
                    // 可以显示成功消息
                } else {
                    // 可以显示错误消息
                }
            })
            
            configBridge.environmentListUpdated.connect(function(environments) {
                console.log("环境列表更新:", environments.length, "个环境")
                // 环境列表更新信号已移动到SettingsPython.qml中处理
            })
            
            configBridge.currentEnvironmentChanged.connect(function(envName) {
                console.log("当前环境切换为:", envName)
            })
            
            // 连接消息提示信号
            configBridge.showSuccessMessageSignal.connect(function(title, content, duration) {
                messageManager.showSuccess(title, content, duration)
            })
            
            configBridge.showErrorMessageSignal.connect(function(title, content, duration) {
                messageManager.showError(title, content, duration)
            })
            
            configBridge.showWarningMessageSignal.connect(function(title, content, duration) {
                messageManager.showWarning(title, content, duration)
            })
            
            configBridge.showInfoMessageSignal.connect(function(title, content, duration) {
                messageManager.showInfo(title, content, duration)
            })
            
            // 连接通用消息信号
            configBridge.showMessageSignal.connect(function(messageType, title, content, duration) {
                if (messageType === "success") {
                    messageManager.showSuccess(title, content, duration)
                } else if (messageType === "error") {
                    messageManager.showError(title, content, duration)
                } else if (messageType === "warning") {
                    messageManager.showWarning(title, content, duration)
                } else if (messageType === "info") {
                    messageManager.showInfo(title, content, duration)
                }
            })
        } else {
            console.log("configBridge不可用，无法连接信号")
        }
    }
    
    Rectangle {
        anchors.fill: parent
        color: "#ffffff"
        
        // 消息管理器
        MessageManager {
            id: messageManager
            anchors.fill: parent
        }
        
        ColumnLayout {
            anchors.fill: parent
            anchors.margins: 20
            spacing: 16
            
            // 设置选项
            ScrollView {
                Layout.fillWidth: true
                Layout.fillHeight: true
                clip: true
                ScrollBar.horizontal.policy: ScrollBar.AlwaysOff
                
                // 自定义滚动条容器
                Rectangle {
                    id: settingsScrollBarContainer
                    width: 6
                    height: parent.height - 8
                    anchors.right: parent.right
                    anchors.rightMargin: 2
                    anchors.top: parent.top
                    anchors.topMargin: 4
                    color: "transparent"
                    visible: settingsListView.contentHeight > settingsListView.height
                    
                    // 滚动条背景
                    Rectangle {
                        id: settingsScrollBarBackground
                        anchors.fill: parent
                        color: "#e8e8e8"
                        radius: 3
                        opacity: settingsScrollBarMouseArea.containsMouse ? 0.8 : 0.4
                        
                        Behavior on opacity {
                            NumberAnimation { duration: 200; easing.type: Easing.OutCubic }
                        }
                    }
                    
                    // 滚动条滑块
                    Rectangle {
                        id: settingsScrollBarHandle
                        width: parent.width
                        height: Math.max(20, (settingsListView.height / settingsListView.contentHeight) * settingsScrollBarContainer.height)
                        x: 0
                        y: (settingsListView.contentY / (settingsListView.contentHeight - settingsListView.height)) * 
                           (settingsScrollBarContainer.height - height)
                        color: settingsScrollBarMouseArea.pressed ? "#1B5E20" : 
                               (settingsScrollBarMouseArea.containsMouse ? "#2E7D32" : "#4CAF50")
                        radius: 3
                        opacity: settingsScrollBarMouseArea.containsMouse ? 1.0 : 0.7
                        
                        // 渐变效果
                        gradient: Gradient {
                            GradientStop { 
                                position: 0.0; 
                                color: settingsScrollBarMouseArea.pressed ? "#0D4A0F" : 
                                       (settingsScrollBarMouseArea.containsMouse ? "#1B5E20" : "#4CAF50")
                            }
                            GradientStop { 
                                position: 1.0; 
                                color: settingsScrollBarMouseArea.pressed ? "#1B5E20" : 
                                       (settingsScrollBarMouseArea.containsMouse ? "#2E7D32" : "#66BB6A")
                            }
                        }
                        
                        // 内阴影效果
                        Rectangle {
                            anchors.fill: parent
                            anchors.margins: 1
                            color: "transparent"
                            border.color: "white"
                            border.width: 1
                            radius: 2
                            opacity: 0.3
                        }
                        
                        // 动画效果
                        Behavior on opacity {
                            NumberAnimation { duration: 200; easing.type: Easing.OutCubic }
                        }
                        
                        Behavior on scale {
                            NumberAnimation { duration: 150; easing.type: Easing.OutCubic }
                        }
                        
                        scale: settingsScrollBarMouseArea.pressed ? 1.1 : 
                               (settingsScrollBarMouseArea.containsMouse ? 1.05 : 1.0)
                    }
                    
                    // 鼠标交互区域
                    MouseArea {
                        id: settingsScrollBarMouseArea
                        anchors.fill: parent
                        hoverEnabled: true
                        acceptedButtons: Qt.LeftButton
                        
                        onPressed: {
                            var clickY = mouseY
                            var handleY = settingsScrollBarHandle.y
                            var handleHeight = settingsScrollBarHandle.height
                            var containerHeight = settingsScrollBarContainer.height
                            
                            if (clickY < handleY) {
                                // 点击滑块上方，向上滚动
                                settingsListView.contentY = Math.max(0, settingsListView.contentY - settingsListView.height * 0.8)
                            } else if (clickY > handleY + handleHeight) {
                                // 点击滑块下方，向下滚动
                                settingsListView.contentY = Math.min(settingsListView.contentHeight - settingsListView.height, 
                                                                      settingsListView.contentY + settingsListView.height * 0.8)
                            } else {
                                // 点击滑块，开始拖拽
                                drag.target = settingsScrollBarHandle
                                drag.axis = Drag.YAxis
                                drag.minimumY = 0
                                drag.maximumY = containerHeight - handleHeight
                            }
                        }
                        
                        onReleased: {
                            drag.target = null
                        }
                        
                        onPositionChanged: {
                            if (drag.target === settingsScrollBarHandle) {
                                var ratio = settingsScrollBarHandle.y / (settingsScrollBarContainer.height - settingsScrollBarHandle.height)
                                settingsListView.contentY = ratio * (settingsListView.contentHeight - settingsListView.height)
                            }
                        }
                    }
                }
                
                ScrollBar.vertical: ScrollBar {
                    id: settingsScrollBar
                    policy: ScrollBar.AlwaysOff  // 隐藏默认滚动条
                }
                
                ListView {
                    id: settingsListView
                    anchors.fill: parent
                    anchors.rightMargin: 12  // 为滚动条留出空间
                    spacing: 16  // 减少间距
                    boundsBehavior: Flickable.StopAtBounds
                    flickableDirection: Flickable.VerticalFlick
                    model: ListModel {
                        id: settingsModel
                        
                        ListElement {
                            type: "title"
                            text: "🎨 主题设置"
                        }
                        ListElement {
                            type: "theme"
                        }
                        ListElement {
                            type: "title"
                            text: "🐍 Python环境配置"
                        }
                        ListElement {
                            type: "python"
                        }
                        ListElement {
                            type: "title"
                            text: "🔌 插件设置"
                        }
                        ListElement {
                            type: "plugin"
                        }
                        ListElement {
                            type: "title"
                            text: "🌐 镜像源设置"
                        }
                        ListElement {
                            type: "mirror"
                        }
                    }
                    
                    delegate: Loader {
                        width: settingsListView.width
                        sourceComponent: {
                            if (model.type === "title") {
                                return titleComponent
                            } else if (model.type === "theme") {
                                return themeComponent
                            } else if (model.type === "python") {
                                return pythonComponent
                            } else if (model.type === "plugin") {
                                return pluginComponent
                            } else if (model.type === "mirror") {
                                return mirrorComponent
                            }
                            return null
                        }
                        
                        // 传递数据给组件
                        property var itemModel: model
                    }
                }
                
                // 标题组件
                Component {
                    id: titleComponent
                    Text {
                        text: itemModel ? itemModel.text : ""
                        font.pixelSize: 18
                        font.bold: true
                        color: "#333333"
                        width: settingsListView.width
                        topPadding: 4
                        bottomPadding: 4
                    }
                }
                
                // 主题设置组件
                Component {
                    id: themeComponent
                    SettingsTheme {
                        width: settingsListView.width
                    }
                }
                
                // Python环境配置组件
                Component {
                    id: pythonComponent
                    SettingsPython {
                        width: settingsListView.width
                    }
                }
                
                // 插件设置组件
                Component {
                    id: pluginComponent
                    SettingsPlugin {
                        width: settingsListView.width
                    }
                }
                
                // 镜像源设置组件
                Component {
                    id: mirrorComponent
                    SettingsMirror {
                        width: settingsListView.width
                        
                        onMirrorHeightChanged: {
                            // 触发ListView重新计算内容高度
                            Qt.callLater(function() {
                                settingsListView.forceLayout()
                            })
                        }
                    }
                }
            }
            
            // 按钮区域
            RowLayout {
                Layout.fillWidth: true
                spacing: 12
                
                Item {
                    Layout.fillWidth: true
                }
                
                Button {
                    text: "取消"
                    width: 80
                    height: 36
                    
                    onClicked: {
                        settingsWindow.close()
                    }
                }
                
                Button {
                    text: "应用"
                    width: 80
                    height: 36
                    highlighted: true
                    
                    onClicked: {
                        console.log("应用设置")
                        if (configBridge) {
                            configBridge.saveConfig()
                        }
                        settingsWindow.close()
                    }
                }
                
                Button {
                    text: "确定"
                    width: 80
                    height: 36
                    highlighted: true
                    
                    onClicked: {
                        console.log("保存设置")
                        if (configBridge) {
                            configBridge.saveConfig()
                        }
                        settingsWindow.close()
                    }
                }
            }
        }
    }
    
    // JavaScript函数
    function installPackage(envName, packageName) {
        console.log("安装包:", packageName, "到环境:", envName)
        var result = configBridge ? configBridge.installPackage(envName, packageName) : false
        if (result) {
            console.log("包安装请求已发送")
        } else {
            console.log("包安装失败")
        }
    }
    
    function uninstallPackage(envName, packageName) {
        console.log("卸载包:", packageName, "从环境:", envName)
        var result = configBridge ? configBridge.uninstallPackage(envName, packageName) : false
        if (result) {
            console.log("包卸载请求已发送")
        } else {
            console.log("包卸载失败")
        }
    }
    
    function syncEnvironment(envName) {
        console.log("同步环境依赖:", envName)
        var result = configBridge ? configBridge.syncEnvironment(envName) : false
        if (result) {
            console.log("环境同步请求已发送")
        } else {
            console.log("环境同步失败")
        }
    }
}