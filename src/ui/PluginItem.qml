import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

Rectangle {
    id: pluginItem
    
    // 属性
    property string pluginName: ""
    property string pluginDescription: ""
    property string pluginStatus: "stopped"
    property string pluginIcon: "📦"
    property bool isSelected: false
    
    // 信号
    signal startClicked()
    signal stopClicked()
    signal uninstallClicked()
    signal itemClicked()
    
    // 状态颜色映射
    property color statusColor: {
        switch(pluginStatus) {
            case "running": return "#4CAF50"
            case "starting": return "#FF9800"
            case "stopped": return "#9E9E9E"
            case "error": return "#F44336"
            default: return "#9E9E9E"
        }
    }
    
    property string statusText: {
        switch(pluginStatus) {
            case "running": return "运行中"
            case "starting": return "启动中"
            case "stopped": return "已停止"
            case "error": return "错误"
            default: return "未知"
        }
    }
    
    // 样式
    color: isSelected ? "#E8F5E8" : "#ffffff"
    border.color: isSelected ? "#4CAF50" : "transparent"
    border.width: isSelected ? 2 : 0
    radius: 8
    
    // 悬停效果
    MouseArea {
        anchors.fill: parent
        hoverEnabled: true
        onClicked: pluginItem.itemClicked()
        
        onEntered: {
            if (!isSelected) {
                pluginItem.color = "#f5f5f5"
            }
        }
        
        onExited: {
            if (!isSelected) {
                pluginItem.color = "#ffffff"
            }
        }
    }
    
    RowLayout {
        anchors.fill: parent
        anchors.margins: 12
        spacing: 12
        
        // 左侧图标
        Rectangle {
            width: 40
            height: 40
            radius: 20
            color: "#E3F2FD"
            
            Text {
                anchors.centerIn: parent
                text: pluginIcon
                font.pixelSize: 20
            }
        }
        
        // 右侧内容区域 (分为两层)
        ColumnLayout {
            Layout.fillWidth: true
            Layout.fillHeight: true
            spacing: 8
            
            // 上层：插件名称和状态灯
            RowLayout {
                spacing: 8
                Layout.fillWidth: true
                
                // 插件名称
                Text {
                    text: pluginName
                    font.pixelSize: 16
                    font.bold: true
                    color: "#333333"
                    elide: Text.ElideRight
                    Layout.fillWidth: true
                }
                
                // 状态指示器
                Rectangle {
                    width: 8
                    height: 8
                    radius: 4
                    color: statusColor
                }
            }
            
            // 下层：左侧运行状态 + 右侧按钮
            RowLayout {
                spacing: 8
                Layout.fillWidth: true
                
                // 左侧运行状态
                Text {
                    text: statusText
                    font.pixelSize: 12
                    color: statusColor
                    Layout.fillWidth: true
                }
                
                // 右侧操作按钮
                RowLayout {
                    spacing: 4
                    
                    Rectangle {
                        width: 40
                        height: 20
                        color: "#FF9800"
                        radius: 4
                        
                        Text {
                            anchors.centerIn: parent
                            text: "卸载"
                            color: "white"
                            font.pixelSize: 10
                        }
                        
                        MouseArea {
                            anchors.fill: parent
                            onClicked: pluginItem.uninstallClicked()
                            hoverEnabled: true
                            onEntered: parent.color = "#E65100"
                            onExited: parent.color = "#FF9800"
                        }
                    }
                    
                    Rectangle {
                        width: 40
                        height: 20
                        color: "#4CAF50"
                        radius: 4
                        
                        Text {
                            anchors.centerIn: parent
                            text: "启动"
                            color: "white"
                            font.pixelSize: 10
                        }
                        
                        MouseArea {
                            anchors.fill: parent
                            onClicked: pluginItem.startClicked()
                            hoverEnabled: true
                            onEntered: parent.color = "#388E3C"
                            onExited: parent.color = "#4CAF50"
                        }
                    }
                    
                    Rectangle {
                        width: 40
                        height: 20
                        color: "#F44336"
                        radius: 4
                        
                        Text {
                            anchors.centerIn: parent
                            text: "停止"
                            color: "white"
                            font.pixelSize: 10
                        }
                        
                        MouseArea {
                            anchors.fill: parent
                            onClicked: pluginItem.stopClicked()
                            hoverEnabled: true
                            onEntered: parent.color = "#D32F2F"
                            onExited: parent.color = "#F44336"
                        }
                    }
                }
            }
        }
    }
}
