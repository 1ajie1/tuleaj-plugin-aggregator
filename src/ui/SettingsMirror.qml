import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import ConfigBridge 1.0

Rectangle {
    id: settingsMirror
    width: parent.width
    height: Math.max(mirrorColumnLayout.implicitHeight + 24, 200)  // 自动适配内容高度
    color: "#f8f9fa"
    radius: 8
    border.color: "#e0e0e0"
    border.width: 1
    
    // 高度变化信号
    signal mirrorHeightChanged()
    
    // 监听高度变化
    onHeightChanged: {
        mirrorHeightChanged()
    }
    
    ColumnLayout {
        id: mirrorColumnLayout
        anchors.fill: parent
        anchors.margins: 12
        spacing: 16
        
        // 镜像源启用设置
        RowLayout {
            CheckBox {
                id: mirrorEnabledCheckBox
                text: "启用镜像源加速"
                checked: configBridge ? configBridge.mirrorEnabled : false
                font.pixelSize: 14
                
                onCheckedChanged: {
                    if (configBridge) {
                        configBridge.setMirrorEnabled(checked)
                    }
                }
            }
        }
        
        // 默认镜像源选择
        RowLayout {
            spacing: 8
            
            Text {
                text: "默认镜像源:"
                font.pixelSize: 14
                color: "#333333"
                Layout.preferredWidth: 100
            }
            
            ComboBox {
                id: defaultMirrorComboBox
                model: configBridge ? configBridge.getMirrorSourceNames() : []
                currentIndex: {
                    if (configBridge) {
                        var sources = configBridge.getMirrorSourceNames()
                        var defaultSource = configBridge.defaultMirrorSource
                        return sources.indexOf(defaultSource)
                    }
                    return 0
                }
                Layout.fillWidth: true
                enabled: mirrorEnabledCheckBox.checked
                
                onCurrentIndexChanged: {
                    if (configBridge) {
                        var sources = configBridge.getMirrorSourceNames()
                        if (currentIndex >= 0 && currentIndex < sources.length) {
                            configBridge.setDefaultMirrorSource(sources[currentIndex])
                        }
                    }
                }
            }
        }
        
        // 镜像源列表
        Rectangle {
            Layout.fillWidth: true
            Layout.preferredHeight: mirrorListLayout.implicitHeight + 16
            color: "#ffffff"
            radius: 6
            border.color: "#d0d0d0"
            border.width: 1
            
            ColumnLayout {
                id: mirrorListLayout
                anchors.fill: parent
                anchors.margins: 8
                spacing: 8
                
                Text {
                    text: "镜像源列表"
                    font.pixelSize: 14
                    font.bold: true
                    color: "#333333"
                }
                
                // 动态镜像源列表
                Repeater {
                    id: mirrorRepeater
                    model: configBridge ? configBridge.mirrorSources : []
                    
                    RowLayout {
                        spacing: 8
                        Layout.fillWidth: true
                        Layout.preferredHeight: 32
                        
                        CheckBox {
                            id: mirrorCheckBox
                            checked: modelData.enabled !== false  // 默认启用
                            enabled: mirrorEnabledCheckBox.checked
                            
                            onCheckedChanged: {
                                // 使用Qt.callLater避免绑定循环，并保存当前值
                                var currentName = modelData ? modelData.name : ""
                                var currentChecked = checked
                                Qt.callLater(function() {
                                    if (configBridge && currentName) {
                                        var result = configBridge.setMirrorSourceEnabled(currentName, currentChecked)
                                        if (result) {
                                            console.log("镜像源启用状态更新成功:", currentName, currentChecked)
                                        } else {
                                            console.log("镜像源启用状态更新失败:", currentName, currentChecked)
                                        }
                                    }
                                })
                            }
                        }
                        
                        Text {
                            text: modelData.name || ""
                            font.pixelSize: 12
                            color: "#333333"
                            Layout.preferredWidth: 80
                        }
                        
                        Text {
                            text: modelData.url || ""
                            font.pixelSize: 10
                            color: "#666666"
                            Layout.fillWidth: true
                        }
                        
                        Text {
                            text: "优先级: " + (modelData.priority || 999)
                            font.pixelSize: 10
                            color: "#4CAF50"
                            Layout.preferredWidth: 60
                        }
                        
                        Button {
                            text: "测试"
                            width: 40
                            height: 20
                            font.pixelSize: 9
                            enabled: mirrorEnabledCheckBox.checked && modelData.url
                            
                            onClicked: {
                                // 保存当前值，避免延迟执行时modelData变为undefined
                                var currentName = modelData ? modelData.name : ""
                                var currentUrl = modelData ? modelData.url : ""
                                console.log("测试镜像源连接:", currentUrl)
                                if (configBridge && currentUrl) {
                                    var result = configBridge.testMirrorConnection(currentUrl)
                                    if (result) {
                                        console.log("镜像源连接测试成功:", currentName)
                                        configBridge.showMessage("success", "连接测试成功", `镜像源 "${currentName}" 连接正常`, 3000)
                                    } else {
                                        console.log("镜像源连接测试失败:", currentName)
                                        configBridge.showMessage("error", "连接测试失败", `镜像源 "${currentName}" 连接失败，请检查网络或URL`, 3000)
                                    }
                                }
                            }
                        }
                        
                        Button {
                            text: "删除"
                            width: 40
                            height: 20
                            font.pixelSize: 9
                            enabled: mirrorEnabledCheckBox.checked && modelData.name !== "pypi"  // 不允许删除默认的pypi源
                            
                            onClicked: {
                                // 保存当前值，避免延迟执行时modelData变为undefined
                                var currentName = modelData ? modelData.name : ""
                                console.log("删除镜像源:", currentName)
                                if (configBridge && currentName) {
                                    var result = configBridge.removeMirrorSource(currentName)
                                    if (result) {
                                        console.log("镜像源删除成功:", currentName)
                                        configBridge.showMessage("success", "删除成功", `镜像源 "${currentName}" 已删除`, 3000)
                                    } else {
                                        console.log("镜像源删除失败:", currentName)
                                        configBridge.showMessage("error", "删除失败", `镜像源 "${currentName}" 删除失败`, 3000)
                                    }
                                }
                            }
                        }
                    }
                }
                
                // 监听镜像源变化信号
                Connections {
                    target: configBridge
                    function onMirrorSourcesChanged() {
                        console.log("镜像源列表更新，数量:", configBridge ? configBridge.mirrorSources.length : 0)
                        // 强制刷新Repeater的模型
                        Qt.callLater(function() {
                            mirrorRepeater.model = configBridge ? configBridge.mirrorSources : []
                        })
                    }
                }
            }
        }
        
        // 添加自定义镜像源
        Rectangle {
            Layout.fillWidth: true
            Layout.preferredHeight: addMirrorLayout.implicitHeight + 16
            color: "#e3f2fd"
            radius: 6
            border.color: "#2196F3"
            border.width: 1
            
            ColumnLayout {
                id: addMirrorLayout
                anchors.fill: parent
                anchors.margins: 8
                spacing: 8
                
                Text {
                    text: "添加自定义镜像源"
                    font.pixelSize: 14
                    font.bold: true
                    color: "#1976D2"
                }
                
                RowLayout {
                    spacing: 8
                    
                    Text {
                        text: "源名称:"
                        font.pixelSize: 12
                        color: "#333333"
                        Layout.preferredWidth: 60
                    }
                    
                    TextField {
                        id: customMirrorNameField
                        placeholderText: "输入镜像源名称"
                        Layout.fillWidth: true
                        height: 28
                        enabled: mirrorEnabledCheckBox.checked
                    }
                }
                
                RowLayout {
                    spacing: 8
                    
                    Text {
                        text: "源地址:"
                        font.pixelSize: 12
                        color: "#333333"
                        Layout.preferredWidth: 60
                    }
                    
                    TextField {
                        id: customMirrorUrlField
                        placeholderText: "https://example.com/simple/"
                        Layout.fillWidth: true
                        height: 28
                        enabled: mirrorEnabledCheckBox.checked
                    }
                }
                
                RowLayout {
                    spacing: 8
                    
                    Text {
                        text: "优先级:"
                        font.pixelSize: 12
                        color: "#333333"
                        Layout.preferredWidth: 60
                    }
                    
                    SpinBox {
                        id: customMirrorPrioritySpinBox
                        from: 1
                        to: 10
                        value: 6
                        Layout.fillWidth: true
                        enabled: mirrorEnabledCheckBox.checked
                    }
                    
                    Item {
                        Layout.preferredWidth: 30
                    }
                }
                
                RowLayout {
                    spacing: 8
                    
                    Item {
                        Layout.fillWidth: true
                    }
                    
                    Button {
                        text: "测试连接"
                        width: 80
                        height: 28
                        font.pixelSize: 11
                        enabled: mirrorEnabledCheckBox.checked && customMirrorNameField.text !== "" && customMirrorUrlField.text !== ""
                        
                        onClicked: {
                            console.log("测试自定义镜像源连接:", customMirrorUrlField.text)
                            if (configBridge) {
                                var result = configBridge.testMirrorConnection(customMirrorUrlField.text)
                                if (result) {
                                    console.log("自定义镜像源连接测试成功")
                                    configBridge.showMessage("success", "连接测试成功", `镜像源 "${customMirrorNameField.text}" 连接正常`, 3000)
                                } else {
                                    console.log("自定义镜像源连接测试失败")
                                    configBridge.showMessage("error", "连接测试失败", `镜像源 "${customMirrorNameField.text}" 连接失败，请检查网络或URL`, 3000)
                                }
                            }
                        }
                    }
                    
                    Button {
                        text: "添加源"
                        width: 80
                        height: 28
                        font.pixelSize: 11
                        highlighted: true
                        enabled: mirrorEnabledCheckBox.checked && customMirrorNameField.text !== "" && customMirrorUrlField.text !== ""
                        
                        onClicked: {
                            console.log("添加自定义镜像源:", customMirrorNameField.text, customMirrorUrlField.text, customMirrorPrioritySpinBox.value)
                            
                            // 实际添加镜像源的逻辑
                            var result = configBridge ? configBridge.addMirrorSource(
                                customMirrorNameField.text,
                                customMirrorUrlField.text,
                                customMirrorPrioritySpinBox.value
                            ) : false
                            
                            if (result) {
                                console.log("镜像源添加成功")
                                console.log("添加后镜像源列表数量:", configBridge ? configBridge.mirrorSources.length : 0)
                                customMirrorNameField.text = ""
                                customMirrorUrlField.text = ""
                                customMirrorPrioritySpinBox.value = 6
                            } else {
                                console.log("镜像源添加失败")
                            }
                        }
                    }
                }
            }
        }
        
        // 高级设置
        Rectangle {
            Layout.fillWidth: true
            Layout.preferredHeight: advancedMirrorLayout.implicitHeight + 16
            color: "#fff3e0"
            radius: 6
            border.color: "#FF9800"
            border.width: 1
            
            ColumnLayout {
                id: advancedMirrorLayout
                anchors.fill: parent
                anchors.margins: 8
                spacing: 8
                
                Text {
                    text: "高级设置"
                    font.pixelSize: 14
                    font.bold: true
                    color: "#E65100"
                }
                
                RowLayout {
                    spacing: 8
                    
                    Text {
                        text: "连接超时:"
                        font.pixelSize: 12
                        color: "#333333"
                        Layout.preferredWidth: 80
                    }
                    
                    SpinBox {
                        id: timeoutSpinBox
                        from: 5
                        to: 120
                        value: configBridge ? configBridge.mirrorTimeout : 30
                        Layout.fillWidth: true
                        enabled: mirrorEnabledCheckBox.checked
                        
                        onValueChanged: {
                            if (configBridge) {
                                configBridge.setMirrorTimeout(value)
                            }
                        }
                    }
                    
                    Text {
                        text: " 秒"
                        font.pixelSize: 12
                        color: "#666666"
                        Layout.preferredWidth: 30
                    }
                }
                
                RowLayout {
                    spacing: 8
                    
                    Text {
                        text: "重试次数:"
                        font.pixelSize: 12
                        color: "#333333"
                        Layout.preferredWidth: 80
                    }
                    
                    SpinBox {
                        id: retrySpinBox
                        from: 1
                        to: 10
                        value: configBridge ? configBridge.mirrorRetryCount : 3
                        Layout.fillWidth: true
                        enabled: mirrorEnabledCheckBox.checked
                        
                        onValueChanged: {
                            if (configBridge) {
                                configBridge.setMirrorRetryCount(value)
                            }
                        }
                    }
                    
                    Item {
                        Layout.preferredWidth: 30
                    }
                }
                
                RowLayout {
                    CheckBox {
                        id: sslVerifyCheckBox
                        text: "验证SSL证书"
                        checked: configBridge ? configBridge.sslVerify : true
                        enabled: mirrorEnabledCheckBox.checked
                        
                        onCheckedChanged: {
                            if (configBridge) {
                                configBridge.setSslVerify(checked)
                            }
                        }
                    }
                }
                
                RowLayout {
                    spacing: 8
                    
                    Item {
                        Layout.fillWidth: true
                    }
                    
                    Button {
                        text: "测试连接"
                        width: 80
                        height: 28
                        font.pixelSize: 11
                        
                        onClicked: {
                            console.log("测试所有镜像源连接")
                            if (configBridge) {
                                var sources = configBridge.mirrorSources
                                var successCount = 0
                                var totalCount = sources.length
                                
                                for (var i = 0; i < sources.length; i++) {
                                    var source = sources[i]
                                    console.log("测试镜像源:", source.name, source.url)
                                    var result = configBridge.testMirrorConnection(source.url)
                                    if (result) {
                                        console.log("镜像源连接测试成功:", source.name)
                                        successCount++
                                    } else {
                                        console.log("镜像源连接测试失败:", source.name)
                                    }
                                }
                                
                                // 显示测试结果汇总
                                if (successCount === totalCount) {
                                    configBridge.showMessage("success", "测试完成", `所有 ${totalCount} 个镜像源连接正常`, 3000)
                                } else if (successCount > 0) {
                                    configBridge.showMessage("warning", "测试完成", `${successCount}/${totalCount} 个镜像源连接正常，${totalCount - successCount} 个连接失败`, 3000)
                                } else {
                                    configBridge.showMessage("error", "测试完成", `所有 ${totalCount} 个镜像源连接失败，请检查网络连接`, 3000)
                                }
                            }
                        }
                    }
                    
                    Button {
                        text: "重置默认"
                        width: 80
                        height: 28
                        font.pixelSize: 11
                        
                        onClicked: {
                            console.log("重置为默认设置")
                            // 重置默认镜像源
                            if (configBridge) {
                                configBridge.setDefaultMirrorSource("pypi")
                            }
                            // 重置超时和重试设置
                            timeoutSpinBox.value = 30
                            retrySpinBox.value = 3
                            sslVerifyCheckBox.checked = true
                            console.log("设置已重置为默认值")
                        }
                    }
                }
            }
        }
    }
}
