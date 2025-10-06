import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import ConfigBridge 1.0

ApplicationWindow {
    id: environmentManagementWindow
    title: "Python环境管理"
    width: 600
    height: 500
    minimumWidth: 500
    minimumHeight: 400
    visible: false
    modality: Qt.ApplicationModal
    
    // 窗口居中函数
    function centerWindow() {
        // 确保窗口完全居中显示
        environmentManagementWindow.x = Math.max(0, (Screen.width - environmentManagementWindow.width) / 2)
        environmentManagementWindow.y = Math.max(0, (Screen.height - environmentManagementWindow.height) / 2)
    }
    
    // 窗口初始化和信号连接
    Component.onCompleted: {
        centerWindow()
        
        // 连接全局消息信号
        if (configBridge) {
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
        }
    }
    
    // 当窗口显示时重新居中
    onVisibleChanged: {
        if (visible) {
            centerWindow()
            // 确保环境信息是最新的
            if (configBridge) {
                configBridge.refreshEnvironments()
            }
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
            
            // 标题和统计信息
            RowLayout {
                Layout.fillWidth: true
                spacing: 8
            
                Text {
                    text: "可用环境列表"
                    font.pixelSize: 16
                    font.bold: true
                    color: "#333333"
                }
            
                Item {
                    Layout.fillWidth: true
                }
                
                Text {
                    text: "共 " + (configBridge ? configBridge.environmentsList.length : 0) + " 个环境"
                    font.pixelSize: 12
                    color: "#666666"
                }
            }
            
            // 环境列表
            ScrollView {
                Layout.fillWidth: true
                Layout.fillHeight: true
                clip: true
                
                ListView {
                    id: environmentManagementList
                    model: configBridge ? configBridge.environmentsList : []
                    spacing: 8
                    
                    Component.onCompleted: {
                        console.log("环境管理ListView完成，模型数据:", configBridge ? configBridge.environmentsList : [])
                        console.log("模型数据长度:", configBridge ? configBridge.environmentsList.length : 0)
                    }
                    
                    delegate: Rectangle {
                        width: environmentManagementList.width
                        height: envManagementItemLayout.implicitHeight + 16
                        color: (modelData.is_active || false) ? "#e8f5e8" : "#ffffff"
                        radius: 6
                        border.color: (modelData.is_active || false) ? "#4CAF50" : "#e0e0e0"
                        border.width: 1
                        
                        Component.onCompleted: {
                            console.log("环境项完成，模型数据:", model)
                            console.log("环境名称:", modelData.name)
                            console.log("Python版本:", modelData.python_version)
                            console.log("模型数据类型:", typeof model)
                            console.log("模型数据键:", Object.keys(model))
                        }
                        
                        ColumnLayout {
                            id: envManagementItemLayout
                            anchors.fill: parent
                            anchors.margins: 8
                            spacing: 8
                            
                            // 环境基本信息
                            RowLayout {
                                Layout.fillWidth: true
                                spacing: 8
                            
                                ColumnLayout {
                                    Layout.fillWidth: true
                                    spacing: 4
                                
                                    Text {
                                        text: modelData.name || "未知环境"
                                        font.pixelSize: 14
                                        font.bold: modelData.is_active || false
                                        color: (modelData.is_active || false) ? "#2E7D32" : "#333333"
                                    }
                                    
                                    Text {
                                        text: (modelData.python_version || "未知版本") + " | " + (modelData.packages_count || 0) + " 包 | " + (modelData.size_mb || 0) + " MB"
                                        font.pixelSize: 11
                                        color: "#666666"
                                    }
                                    
                                    Text {
                                        text: "路径: " + (modelData.path || "")
                                        font.pixelSize: 10
                                        color: "#999999"
                                        wrapMode: Text.WordWrap
                                        Layout.fillWidth: true
                                    }
                                }
                                
                                // 当前环境标识
                                Text {
                                    text: (modelData.is_active || false) ? "当前环境" : ""
                                    font.pixelSize: 10
                                    color: "#4CAF50"
                                    font.bold: true
                                    visible: modelData.is_active || false
                                }
                            }
                        
                            // 操作按钮
                            RowLayout {
                                Layout.fillWidth: true
                                spacing: 8
                                
                                Button {
                                    text: "切换"
                                    width: 60
                                    height: 28
                                    font.pixelSize: 10
                                    enabled: !(modelData.is_active || false)
                                
                                    onClicked: {
                                        if (configBridge) {
                                            // 显示切换中消息
                                            messageManager.showInfo("切换环境", "正在切换到环境: " + modelData.name, 2000)
                                            
                                            var result = configBridge.switchEnvironment(modelData.name)
                                            if (result) {
                                                console.log("环境切换成功")
                                                // 成功消息由 configBridge.switchEnvironment 内部处理
                                            } else {
                                                console.log("环境切换失败")
                                                // 显示错误消息
                                                messageManager.showError("切换失败", "切换到环境 '" + modelData.name + "' 时发生错误", 3000)
                                            }
                                        }
                                    }
                                }
                                
                                Button {
                                    text: "详情"
                                    width: 60
                                    height: 28
                                    font.pixelSize: 10
                                    
                                    onClicked: {
                                        showEnvironmentDetails(modelData.name)
                                    }
                                }
                                
                                Button {
                                    text: "包管理"
                                    width: 70
                                    height: 28
                                    font.pixelSize: 10
                                    
                                    onClicked: {
                                        showPackageManager(modelData.name)
                                    }
                                }
                                
                                Button {
                                    text: "删除"
                                    width: 60
                                    height: 28
                                    font.pixelSize: 10
                                    enabled: !(modelData.is_active || false)
                                    
                                    onClicked: {
                                        deleteEnvironment(modelData.name)
                                    }
                                }
                                
                                Item {
                                    Layout.fillWidth: true
                                }
                            }
                        }
                    }
                }
            }
            
            // 底部按钮
            RowLayout {
                Layout.fillWidth: true
                spacing: 8
                
                Button {
                    text: "刷新列表"
                    onClicked: {
                        if (configBridge) {
                            // 显示刷新中消息
                            messageManager.showInfo("刷新列表", "正在刷新环境列表...", 1500)
                            configBridge.refreshEnvironments()
                            // 刷新完成后显示成功消息
                            Qt.callLater(function() {
                                messageManager.showSuccess("刷新完成", "环境列表已更新", 2000)
                            })
                        }
                    }
                }
                
                Item {
                    Layout.fillWidth: true
                }
                
                Button {
                    text: "关闭"
                    onClicked: {
                        environmentManagementWindow.close()
                    }
                }
            }
        }
    }
    
    // JavaScript函数
    function showEnvironmentDetails(envName) {
        var envInfo = configBridge ? configBridge.getEnvironmentInfo(envName) : null
        if (envInfo) {
            console.log("环境详情:", envInfo)
            // 显示环境详情对话框
            environmentDetailsDialog.envInfo = envInfo
            environmentDetailsDialog.open()
        } else {
            console.log("未找到环境信息:", envName)
        }
    }
    
    function deleteEnvironment(envName) {
        console.log("确认删除环境:", envName)
        
        // 显示确认对话框
        deleteConfirmDialog.envNameToDelete = envName
        deleteConfirmDialog.open()
    }
    
    function performDelete(envName) {
        console.log("执行删除环境:", envName)
        
        // 显示删除中消息
        messageManager.showInfo("删除环境", "正在删除环境: " + envName, 2000)
        
        var result = configBridge ? configBridge.deleteEnvironment(envName) : false
        if (result) {
            console.log("环境删除请求已发送")
            // 删除成功后自动刷新环境列表
            if (configBridge) {
                configBridge.refreshEnvironments()
            }
        } 
    }
    
    function showPackageManager(envName) {
        console.log("显示包管理器:", envName)
        // 获取环境中的包列表
        var packages = configBridge ? configBridge.getEnvironmentPackages(envName) : []
        console.log("环境包列表:", packages)
        
        // 这里可以显示一个包管理对话框
        // 暂时在控制台输出包列表
        for (var i = 0; i < packages.length; i++) {
            var pkg = packages[i]
            console.log("包:", pkg.name, "版本:", pkg.version)
        }
    }
    
    // 删除确认对话框
    Dialog {
        id: deleteConfirmDialog
        title: "确认删除"
        width: 400
        height: 200
        modal: true
        
        property string envNameToDelete: ""
        
        ColumnLayout {
            anchors.fill: parent
            spacing: 16
            
            Text {
                text: "确定要删除环境 '" + deleteConfirmDialog.envNameToDelete + "' 吗？"
                font.pixelSize: 14
                wrapMode: Text.WordWrap
                Layout.fillWidth: true
            }
            
            Text {
                text: "此操作不可撤销！"
                font.pixelSize: 12
                color: "#f44336"
                font.bold: true
                Layout.fillWidth: true
            }
            
            RowLayout {
                Layout.fillWidth: true
                spacing: 8
                
                Item {
                    Layout.fillWidth: true
                }
                
                Button {
                    text: "取消"
                    onClicked: {
                        deleteConfirmDialog.close()
                    }
                }
                
                Button {
                    text: "删除"
                    highlighted: true
                    onClicked: {
                        deleteConfirmDialog.close()
                        // 执行删除操作
                        performDelete(deleteConfirmDialog.envNameToDelete)
                    }
                }
            }
        }
    }
    
    // 环境详情对话框
    Dialog {
        id: environmentDetailsDialog
        title: "环境详情"
        width: 500
        height: 400
        modal: true
        
        property var envInfo: null
        
        ColumnLayout {
            anchors.fill: parent
            spacing: 16
            
            // 环境基本信息
            GroupBox {
                title: "基本信息"
                Layout.fillWidth: true
                
                ColumnLayout {
                    anchors.fill: parent
                    spacing: 8
                    
                    RowLayout {
                        Text {
                            text: "环境名称:"
                            font.pixelSize: 14
                            font.bold: true
                            Layout.preferredWidth: 100
                        }
                        Text {
                            text: environmentDetailsDialog.envInfo ? environmentDetailsDialog.envInfo.name : ""
                            font.pixelSize: 14
                            Layout.fillWidth: true
                        }
                    }
                    
                    RowLayout {
                        Text {
                            text: "Python版本:"
                            font.pixelSize: 14
                            font.bold: true
                            Layout.preferredWidth: 100
                        }
                        Text {
                            text: environmentDetailsDialog.envInfo ? environmentDetailsDialog.envInfo.python_version : ""
                            font.pixelSize: 14
                            Layout.fillWidth: true
                        }
                    }
                    
                    RowLayout {
                        Text {
                            text: "环境路径:"
                            font.pixelSize: 14
                            font.bold: true
                            Layout.preferredWidth: 100
                        }
                        Text {
                            text: environmentDetailsDialog.envInfo ? environmentDetailsDialog.envInfo.path : ""
                            font.pixelSize: 12
                            color: "#666666"
                            Layout.fillWidth: true
                            wrapMode: Text.WordWrap
                        }
                    }
                    
                    RowLayout {
                        Text {
                            text: "包数量:"
                            font.pixelSize: 14
                            font.bold: true
                            Layout.preferredWidth: 100
                        }
                        Text {
                            text: environmentDetailsDialog.envInfo ? environmentDetailsDialog.envInfo.packages_count + " 个" : ""
                            font.pixelSize: 14
                            Layout.fillWidth: true
                        }
                    }
                    
                    RowLayout {
                        Text {
                            text: "环境大小:"
                            font.pixelSize: 14
                            font.bold: true
                            Layout.preferredWidth: 100
                        }
                        Text {
                            text: environmentDetailsDialog.envInfo ? environmentDetailsDialog.envInfo.size_mb + " MB" : ""
                            font.pixelSize: 14
                            Layout.fillWidth: true
                        }
                    }
                    
                    RowLayout {
                        Text {
                            text: "创建时间:"
                            font.pixelSize: 14
                            font.bold: true
                            Layout.preferredWidth: 100
                        }
                        Text {
                            text: environmentDetailsDialog.envInfo ? 
                                  new Date(environmentDetailsDialog.envInfo.created_time * 1000).toLocaleString() : ""
                            font.pixelSize: 12
                            color: "#666666"
                            Layout.fillWidth: true
                        }
                    }
                    
                    RowLayout {
                        Text {
                            text: "激活状态:"
                            font.pixelSize: 14
                            font.bold: true
                            Layout.preferredWidth: 100
                        }
                        Text {
                            text: environmentDetailsDialog.envInfo && environmentDetailsDialog.envInfo.is_active ? "已激活" : "未激活"
                            font.pixelSize: 14
                            color: environmentDetailsDialog.envInfo && environmentDetailsDialog.envInfo.is_active ? "#4CAF50" : "#666666"
                            Layout.fillWidth: true
                        }
                    }
                }
            }
            
            // 操作按钮
            RowLayout {
                Layout.fillWidth: true
                spacing: 8
                
                Item {
                    Layout.fillWidth: true
                }
                
                Button {
                    text: "关闭"
                    onClicked: {
                        environmentDetailsDialog.close()
                    }
                }
                
                // Button {
                //     text: "切换到此环境"
                //     highlighted: true
                //     enabled: environmentDetailsDialog.envInfo && !environmentDetailsDialog.envInfo.is_active
                    
                //     onClicked: {
                //         if (configBridge && environmentDetailsDialog.envInfo) {
                //             var result = configBridge.switchEnvironment(environmentDetailsDialog.envInfo.name)
                //             if (result) {
                //                 console.log("环境切换成功")
                //                 environmentDetailsDialog.close()
                //             } else {
                //                 console.log("环境切换失败")
                //             }
                //         }
                //     }
                // }
            }
        }
    }
}
