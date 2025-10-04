import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

ApplicationWindow {
    id: settingsWindow
    title: "设置"
    width: Math.min(600, Screen.width * 0.8)
    height: Math.min(650, Screen.height * 0.7)
    minimumWidth: 550
    minimumHeight: 400
    visible: false
    modality: Qt.ApplicationModal
    
    // 窗口居中
    Component.onCompleted: {
        settingsWindow.x = (Screen.width - settingsWindow.width) / 2
        settingsWindow.y = (Screen.height - settingsWindow.height) / 2
    }
    
    Rectangle {
        anchors.fill: parent
        color: "#ffffff"
        
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
                        text: parent.itemModel.text
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
                    Rectangle {
                        width: settingsListView.width
                        height: themeColumnLayout.implicitHeight + 24  // 内容高度 + 边距
                        color: "#f8f9fa"
                        radius: 8
                        border.color: "#e0e0e0"
                        border.width: 1
                        
                        ColumnLayout {
                            id: themeColumnLayout
                            anchors.left: parent.left
                            anchors.right: parent.right
                            anchors.top: parent.top
                            anchors.bottom: parent.bottom
                            anchors.leftMargin: 24  // 增加左右边距
                            anchors.rightMargin: 24
                            anchors.topMargin: 12
                            anchors.bottomMargin: 12
                            spacing: 12  // 减少间距
                            
                            RowLayout {
                                spacing: 8  // 添加间距
                                
                                Text {
                                    text: "主题模式:"
                                    font.pixelSize: 14
                                    color: "#333333"
                                    Layout.preferredWidth: 80
                                }
                                
                                ComboBox {
                                    id: themeComboBox
                                    model: ["浅色模式", "深色模式", "自动"]
                                    currentIndex: 0
                                    Layout.fillWidth: true
                                }
                            }
                        }
                    }
                }
                
                // Python环境配置组件
                Component {
                    id: pythonComponent
                    Rectangle {
                        width: settingsListView.width
                        height: pythonColumnLayout.implicitHeight + 24  // 内容高度 + 边距
                        color: "#f8f9fa"
                        radius: 8
                        border.color: "#e0e0e0"
                        border.width: 1
                        
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
                                            text: "tuleaj-plugin-aggregator"
                                            font.pixelSize: 12
                                            color: "#666666"
                                            Layout.fillWidth: true
                                        }
                                        
                                        Button {
                                            text: "查看详情"
                                            width: 80
                                            height: 24
                                            font.pixelSize: 10
                                            
                                            onClicked: {
                                                console.log("查看当前环境详情")
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
                                            text: "Python 3.11.0"
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
                                                console.log("刷新环境信息")
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
                                            model: ["Python 3.8", "Python 3.9", "Python 3.10", "Python 3.11", "Python 3.12"]
                                            currentIndex: 3
                                            Layout.fillWidth: true
                                        }
                                    }
                                    
                                    RowLayout {
                                        spacing: 8
                                        
                                        Item {
                                            Layout.fillWidth: true
                                        }
                                        
                                        Button {
                                            text: "创建环境"
                                            width: 100
                                            height: 28
                                            font.pixelSize: 11
                                            highlighted: true
                                            
                                            onClicked: {
                                                console.log("创建新环境:", newEnvNameField.text, pythonVersionComboBox.currentText)
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
                
                // 插件设置组件
                Component {
                    id: pluginComponent
                    Rectangle {
                        width: settingsListView.width
                        height: pluginColumnLayout.implicitHeight + 24  // 内容高度 + 边距
                        color: "#f8f9fa"
                        radius: 8
                        border.color: "#e0e0e0"
                        border.width: 1
                        
                        ColumnLayout {
                            id: pluginColumnLayout
                            anchors.left: parent.left
                            anchors.right: parent.right
                            anchors.top: parent.top
                            anchors.bottom: parent.bottom
                            anchors.leftMargin: 24  // 增加左右边距
                            anchors.rightMargin: 24
                            anchors.topMargin: 12
                            anchors.bottomMargin: 12
                            spacing: 12  // 减少间距
                            
                            RowLayout {
                                CheckBox {
                                    id: autoStartCheckBox
                                    text: "自动启动已安装的插件"
                                    checked: false
                                }
                            }
                            
                            RowLayout {
                                CheckBox {
                                    id: updateCheckBox
                                    text: "自动检查插件更新"
                                    checked: true
                                }
                            }
                            
                            RowLayout {
                                spacing: 8  // 添加间距
                                
                                Text {
                                    text: "插件安装路径:"
                                    font.pixelSize: 14
                                    color: "#333333"
                                    Layout.preferredWidth: 100
                                }
                                
                                TextField {
                                    id: pluginPathField
                                    text: "C:\\Users\\tulea\\Desktop\\tmp\\code\\tuleaj-plugin-aggregator\\plugins"
                                    Layout.fillWidth: true
                                }
                                
                                Button {
                                    text: "浏览"
                                    width: 60
                                    onClicked: {
                                        // TODO: 实现文件夹选择
                                        console.log("选择插件安装路径")
                                    }
                                }
                            }
                            
                            RowLayout {
                                CheckBox {
                                    id: debugModeCheckBox
                                    text: "启用调试模式"
                                    checked: false
                                }
                            }
                            
                            RowLayout {
                                CheckBox {
                                    id: autoUpdateCheckBox
                                    text: "自动下载插件更新"
                                    checked: true
                                }
                            }
                            
                            RowLayout {
                                spacing: 8  // 添加间距
                                
                                Text {
                                    text: "插件超时时间:"
                                    font.pixelSize: 14
                                    color: "#333333"
                                    Layout.preferredWidth: 100
                                }
                                
                                SpinBox {
                                    from: 5
                                    to: 60
                                    value: 30
                                    Layout.fillWidth: true
                                }
                                
                                Text {
                                    text: " 秒"
                                    font.pixelSize: 12
                                    color: "#666666"
                                    Layout.preferredWidth: 30
                                }
                            }
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
                        // TODO: 保存设置
                        console.log("应用设置")
                        settingsWindow.close()
                    }
                }
                
                Button {
                    text: "确定"
                    width: 80
                    height: 36
                    highlighted: true
                    
                    onClicked: {
                        // TODO: 保存设置
                        console.log("保存设置")
                        settingsWindow.close()
                    }
                }
            }
        }
    }
}
