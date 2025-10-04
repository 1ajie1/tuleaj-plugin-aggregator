import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import QtQuick.Dialogs

ApplicationWindow {
    id: fileSelectorWindow
    title: "选择插件文件"
    width: 550
    height: 500
    minimumWidth: 500
    minimumHeight: 400
    visible: false
    modality: Qt.ApplicationModal
    
    // 信号定义
    signal fileSelected(string filePath)
    signal cancelled()
    
    // 窗口居中
    Component.onCompleted: {
        fileSelectorWindow.x = (parent.width - fileSelectorWindow.width) / 2
        fileSelectorWindow.y = (parent.height - fileSelectorWindow.height) / 2
    }
    
    // 原生文件选择对话框
    FileDialog {
        id: nativeFileDialog
        title: "选择 .whl 文件"
        currentFolder: "file:///C:/Users/tulea"
        nameFilters: [
            "Wheel files (*.whl)",
            "所有文件 (*)"
        ]
        
        onAccepted: {
            var filePath = selectedFile.toString().replace("file:///", "")
            if (filePath.endsWith(".whl")) {
                fileSelectorWindow.fileSelected(filePath)
                fileSelectorWindow.close()
            } else {
                console.log("只支持 .whl 格式文件")
            }
        }
        
        onRejected: {
            console.log("取消选择文件")
        }
    }
    
    Rectangle {
        anchors.fill: parent
        color: "#ffffff"
        
        ColumnLayout {
            anchors.fill: parent
            anchors.margins: 24
            spacing: 20
            
            // 标题
            Text {
                text: "选择插件文件"
                font.pixelSize: 24
                font.bold: true
                color: "#333333"
                Layout.fillWidth: true
            }
            
            // 分隔线
            Rectangle {
                Layout.fillWidth: true
                height: 1
                color: "#e0e0e0"
            }
            
            
            // 文件选择区域
            Rectangle {
                Layout.fillWidth: true
                Layout.fillHeight: true
                color: "#fafafa"
                radius: 12
                border.color: "#e0e0e0"
                border.width: 1
                
                // 添加阴影效果
                Rectangle {
                    anchors.fill: parent
                    anchors.margins: 1
                    color: "transparent"
                    border.color: "white"
                    border.width: 1
                    radius: 11
                    opacity: 0.5
                }
                
                ColumnLayout {
                    anchors.fill: parent
                    anchors.margins: 24
                    anchors.bottomMargin: 32
                    spacing: 20
                    
                    // 拖拽区域
                    Rectangle {
                        id: dropAreaRect
                        Layout.fillWidth: true
                        Layout.preferredHeight: 220
                        color: dropAreaHandler.containsDrag ? "#e3f2fd" : "transparent"
                        radius: 12
                        border.color: dropAreaHandler.containsDrag ? "#2196f3" : "#d0d0d0"
                        border.width: 2
                        
                        // 渐变背景
                        gradient: Gradient {
                            GradientStop { 
                                position: 0.0; 
                                color: dropAreaHandler.containsDrag ? "#e3f2fd" : "#f8f9fa" 
                            }
                            GradientStop { 
                                position: 1.0; 
                                color: dropAreaHandler.containsDrag ? "#bbdefb" : "#ffffff" 
                            }
                        }
                        
                        ColumnLayout {
                            anchors.centerIn: parent
                            spacing: 24
                            
                            Text {
                                text: "📁"
                                font.pixelSize: 56
                                color: dropAreaHandler.containsDrag ? "#2196f3" : "#999999"
                                Layout.alignment: Qt.AlignHCenter
                            }
                            
                            Text {
                                text: dropAreaHandler.containsDrag ? "释放文件以安装插件" : "拖拽文件到此处"
                                font.pixelSize: 16
                                font.bold: true
                                color: dropAreaHandler.containsDrag ? "#2196f3" : "#666666"
                                Layout.alignment: Qt.AlignHCenter
                            }
                        }
                        
                        // 拖拽处理
                        DropArea {
                            id: dropAreaHandler
                            anchors.fill: parent
                            
                            onDropped: {
                                if (drop.hasUrls) {
                                    var filePath = drop.urls[0].toString().replace("file:///", "")
                                    if (filePath.endsWith(".whl")) {
                                        fileSelectorWindow.fileSelected(filePath)
                                        fileSelectorWindow.close()
                                    } else {
                                        console.log("只支持 .whl 格式文件")
                                    }
                                }
                            }
                        }
                    }
                    
                    // 格式说明放在拖拽区域外面
                    Text {
                        text: "只支持 .whl 格式"
                        font.pixelSize: 12
                        color: "#999999"
                        Layout.alignment: Qt.AlignHCenter
                    }
                    
                    // 选择文件按钮
                    Rectangle {
                        Layout.fillWidth: true
                        height: 44
                        radius: 8
                        color: "#4CAF50"
                        border.color: "#45a049"
                        border.width: 1
                        
                        // 渐变效果
                        gradient: Gradient {
                            GradientStop { position: 0.0; color: "#4CAF50" }
                            GradientStop { position: 1.0; color: "#45a049" }
                        }
                        
                        // 阴影效果
                        Rectangle {
                            anchors.fill: parent
                            anchors.margins: 1
                            color: "transparent"
                            border.color: "white"
                            border.width: 1
                            radius: 7
                            opacity: 0.3
                        }
                        
                        Text {
                            text: "选择文件"
                            anchors.centerIn: parent
                            font.pixelSize: 14
                            font.bold: true
                            color: "white"
                        }
                        
                        MouseArea {
                            anchors.fill: parent
                            hoverEnabled: true
                            
                            onClicked: {
                                // 调用原生文件选择器
                                nativeFileDialog.open()
                            }
                            
                            onEntered: {
                                parent.color = "#45a049"
                                parent.border.color = "#2E7D32"
                            }
                            
                            onExited: {
                                parent.color = "#4CAF50"
                                parent.border.color = "#45a049"
                            }
                            
                            onPressed: {
                                parent.color = "#2E7D32"
                                parent.border.color = "#1B5E20"
                            }
                            
                            onReleased: {
                                parent.color = "#45a049"
                                parent.border.color = "#2E7D32"
                            }
                        }
                    }
                }
            }
            
            
        }
    }
    
    // 纯QML文件输入对话框
    Rectangle {
        id: fileInputDialog
        anchors.fill: parent
        color: "#80000000"
        visible: false
        
        Rectangle {
            width: 450
            height: 250
            anchors.centerIn: parent
            color: "#ffffff"
            radius: 8
            border.color: "#e0e0e0"
            border.width: 1
            
            ColumnLayout {
                anchors.fill: parent
                anchors.margins: 20
                spacing: 16
                
                Text {
                    text: "输入文件路径"
                    font.pixelSize: 18
                    font.bold: true
                    color: "#333333"
                    Layout.fillWidth: true
                }
                
                TextField {
                    id: filePathInput
                    placeholderText: "请输入.whl文件的完整路径"
                    Layout.fillWidth: true
                    selectByMouse: true
                    
                    onAccepted: {
                        if (text.trim() !== "" && text.trim().endsWith(".whl")) {
                            fileSelectorWindow.fileSelected(text.trim())
                            fileInputDialog.visible = false
                            fileSelectorWindow.close()
                        } else {
                            console.log("只支持 .whl 格式文件")
                        }
                    }
                }
                
                Text {
                    text: "示例: C:\\Users\\tulea\\Downloads\\my-plugin-1.0.0.whl"
                    font.pixelSize: 12
                    color: "#666666"
                    Layout.fillWidth: true
                }
                
                RowLayout {
                    Layout.fillWidth: true
                    spacing: 12
                    
                    Item {
                        Layout.fillWidth: true
                    }
                    
                    Button {
                        text: "取消"
                        onClicked: {
                            fileInputDialog.visible = false
                        }
                    }
                    
                    Button {
                        text: "确定"
                        highlighted: true
                        enabled: filePathInput.text.trim() !== "" && filePathInput.text.trim().endsWith(".whl")
                        
                        onClicked: {
                            if (filePathInput.text.trim() !== "" && filePathInput.text.trim().endsWith(".whl")) {
                                fileSelectorWindow.fileSelected(filePathInput.text.trim())
                                fileInputDialog.visible = false
                                fileSelectorWindow.close()
                            } else {
                                console.log("只支持 .whl 格式文件")
                            }
                        }
                    }
                }
            }
        }
        
        // 点击背景关闭对话框
        MouseArea {
            anchors.fill: parent
            onClicked: {
                fileInputDialog.visible = false
            }
        }
    }
}
