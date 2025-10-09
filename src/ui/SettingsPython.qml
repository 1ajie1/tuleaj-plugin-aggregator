import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import ConfigBridge 1.0

Rectangle {
    id: settingsPython
    width: parent.width
    height: pythonColumnLayout.implicitHeight + 24  // 内容高度 + 边距
    color: "#f8f9fa"
    radius: 8
    border.color: "#e0e0e0"
    border.width: 1
    
    // 创建环境状态管理
    property bool isCreating: false
    property string creatingEnvName: ""
    property int createTimeout: 60000  // 60秒超时
    
    // 创建环境超时定时器
    Timer {
        id: createTimeoutTimer
        repeat: false
        onTriggered: {
            console.log("创建环境超时:", settingsPython.creatingEnvName)
            console.log("超时时间:", settingsPython.createTimeout / 1000, "秒")
            var envName = settingsPython.creatingEnvName
            settingsPython.isCreating = false
            settingsPython.creatingEnvName = ""
            
            console.log("超时定时器触发")
            
            // 重置按钮状态
            resetButtonState()
            
            // 显示超时消息
            console.log("环境创建超时，请检查网络连接或重试")
        }
    }
    
    ColumnLayout {
        id: pythonColumnLayout
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.top: parent.top
        anchors.bottom: parent.bottom
        anchors.leftMargin: 24  // 增加左右边距
        anchors.rightMargin: 24
        anchors.topMargin: 12
        anchors.bottomMargin: 12
        spacing: 16  // 增加间距以适应更多内容
        
        // 当前虚拟环境信息
        Rectangle {
            Layout.fillWidth: true
            height: currentEnvLayout.implicitHeight + 16
            color: "#e8f5e8"
            radius: 6
            border.color: "#4CAF50"
            border.width: 1
            
            ColumnLayout {
                id: currentEnvLayout
                anchors.fill: parent
                anchors.margins: 8
                spacing: 8
                
                Text {
                    text: "当前虚拟环境"
                    font.pixelSize: 14
                    font.bold: true
                    color: "#2E7D32"
                }
                
                RowLayout {
                    spacing: 8
                    
                    Text {
                        text: "环境名称:"
                        font.pixelSize: 12
                        color: "#333333"
                        Layout.preferredWidth: 80
                    }
                    
                    Text {
                        text: {
                            if (!configBridge) return "空"
                            var envName = configBridge.currentEnvironmentName
                            return envName && envName.trim() !== "" ? envName : "空"
                        }
                        font.pixelSize: 12
                        color: "#666666"
                        Layout.fillWidth: true
                    }
                    
                    Button {
                        text: "环境管理"
                        width: 80
                        height: 24
                        font.pixelSize: 10
                        
                        onClicked: {
                            showEnvironmentManagement()
                        }
                    }
                }
                
                RowLayout {
                    spacing: 8
                    
                    Text {
                        text: "Python版本:"
                        font.pixelSize: 12
                        color: "#333333"
                        Layout.preferredWidth: 80
                    }
                    
                    Text {
                        text: {
                            if (!configBridge) return "空"
                            var pythonVersion = configBridge.currentPythonVersion
                            return pythonVersion && pythonVersion.trim() !== "" ? pythonVersion : "空"
                        }
                        font.pixelSize: 12
                        color: "#666666"
                        Layout.fillWidth: true
                    }
                    
                    Button {
                        text: "刷新"
                        width: 60
                        height: 24
                        font.pixelSize: 10
                        
                        onClicked: {
                            if (configBridge) {
                                configBridge.refreshEnvironments()
                            }
                        }
                    }
                }
            }
        }
        
        // 创建新虚拟环境
        Rectangle {
            Layout.fillWidth: true
            height: newEnvLayout.implicitHeight + 16
            color: "#fff3e0"
            radius: 6
            border.color: "#FF9800"
            border.width: 1
            
            ColumnLayout {
                id: newEnvLayout
                anchors.fill: parent
                anchors.margins: 8
                spacing: 8
                
                Text {
                    text: "创建新虚拟环境"
                    font.pixelSize: 14
                    font.bold: true
                    color: "#E65100"
                }
                
                RowLayout {
                    spacing: 8
                    
                    Text {
                        text: "环境名称:"
                        font.pixelSize: 12
                        color: "#333333"
                        Layout.preferredWidth: 80
                    }
                    
                    TextField {
                        id: newEnvNameField
                        placeholderText: "输入环境名称"
                        Layout.fillWidth: true
                        height: 28
                    }
                }
                
                RowLayout {
                    spacing: 8
                    
                    Text {
                        text: "Python版本:"
                        font.pixelSize: 12
                        color: "#333333"
                        Layout.preferredWidth: 80
                    }
                    
                    ComboBox {
                        id: pythonVersionComboBox
                        model: ["3.8", "3.9", "3.10", "3.11", "3.12"]
                        currentIndex: 3
                        Layout.fillWidth: true
                    }
                }
                
                RowLayout {
                    spacing: 8
                    
                    Text {
                        text: "超时时间:"
                        font.pixelSize: 12
                        color: "#333333"
                        Layout.preferredWidth: 80
                    }
                    
                    SpinBox {
                        id: timeoutSpinBox
                        from: 30
                        to: 300
                        value: 30
                        Layout.preferredWidth: 120
                        
                        onValueChanged: {
                            settingsPython.createTimeout = value * 1000  // 转换为毫秒
                        }
                        
                        Component.onCompleted: {
                            // 确保初始值被设置
                            settingsPython.createTimeout = value * 1000
                        }
                    }
                    
                    Text {
                        text: "秒"
                        font.pixelSize: 12
                        color: "#333333"
                    }
                    
                    Item {
                        Layout.fillWidth: true
                    }
                }
                
                    RowLayout {
                        spacing: 8
                        
                        Item {
                            Layout.fillWidth: true
                        }
                        
                        // 创建进度指示器
                        BusyIndicator {
                            id: createProgressIndicator
                            width: 20
                            height: 20
                            visible: isCreating
                            running: isCreating
                        }
                        
                        Button {
                            id: createEnvButton
                            text: "创建环境"
                            width: 100
                            height: 28
                            font.pixelSize: 11
                            highlighted: true
                            enabled: newEnvNameField.text.trim() !== ""
                            
                            onClicked: {
                                // 立即更新按钮状态
                                createEnvButton.text = "创建中..."
                                createEnvButton.enabled = false
                                console.log("按钮状态立即更新为: 创建中...")
                                
                                // 启动创建过程
                                startCreateEnvironment()
                            }
                        }
                    }
            }
        }
    }
    
    // 环境管理窗口加载器
    Loader {
        id: environmentManagementLoader
        source: "EnvironmentManagementWindow.qml"
        active: false
        
        onLoaded: {
            // 设置父窗口
            if (item) {
                // ApplicationWindow会自动处理父窗口关系
            }
        }
    }
    
    // 连接信号
    Component.onCompleted: {
        if (configBridge) {
            // 连接环境创建完成信号
            configBridge.environmentCreated.connect(finishCreateEnvironment)
        }
    }
    
    // JavaScript函数
    function startCreateEnvironment() {
        var envName = newEnvNameField.text.trim()
        var pythonVersion = pythonVersionComboBox.currentText.replace("Python ", "")
        
        if (envName === "") {
            console.log("环境名称不能为空")
            // 恢复按钮状态
            createEnvButton.text = "创建环境"
            createEnvButton.enabled = true
            return
        }
        
        // 设置创建状态（用于其他组件，如BusyIndicator）
        isCreating = true
        creatingEnvName = envName
        
        console.log("开始创建新环境:", envName, pythonVersion)
        console.log("超时时间设置为:", createTimeout / 1000, "秒")
        
        // 启动超时定时器
        createTimeoutTimer.interval = createTimeout
        createTimeoutTimer.start()
        
        // 发送创建请求
        var result = configBridge ? configBridge.createEnvironment(envName, pythonVersion, createTimeout / 1000) : false
        
        if (result) {
            console.log("环境创建请求已发送")
        } else {
            console.log("环境创建失败")
            // 创建失败，重置状态
            resetButtonState()
        }
    }
    
    function resetButtonState() {
        createEnvButton.text = "创建环境"
        createEnvButton.enabled = newEnvNameField.text.trim() !== ""
        console.log("按钮状态重置为: 创建环境")
    }
    
    function finishCreateEnvironment(success, message) {
        // 停止超时定时器
        createTimeoutTimer.stop()
        
        // 重置状态
        isCreating = false
        var envName = creatingEnvName
        creatingEnvName = ""
        
        console.log("finishCreateEnvironment 被调用")
        
        // 重置按钮状态
        resetButtonState()
        
        if (success) {
            console.log("环境创建成功:", envName)
            // 清空输入框
            newEnvNameField.text = ""
            pythonVersionComboBox.currentIndex = 3
        } else {
            console.log("环境创建失败:", message)
        }
    }
    
    function showEnvironmentManagement() {
        console.log("显示环境管理")
        
        // 获取所有可用环境（不需要重复刷新，因为启动时已经扫描过了）
        var environments = configBridge ? configBridge.environmentsList : []
        console.log("可用环境:", environments.length, "个")
        
        // 即使没有环境也显示环境管理窗口，让用户可以创建新环境
        console.log("显示环境管理窗口")
        
        // 显示环境管理窗口
        environmentManagementLoader.active = true
        if (environmentManagementLoader.item) {
            environmentManagementLoader.item.show()
        }
    }
}
