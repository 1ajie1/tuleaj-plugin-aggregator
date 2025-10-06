import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import SystemMonitor 1.0

ApplicationWindow {
    id: mainWindow
    title: "系统监控"
    width: 400
    height: 300
    visible: true
    
    // 系统监控后端
    SystemMonitorBackend {
        id: systemMonitor
        
        onCpuUsageChanged: function(usage) {
            cpuProgressBar.value = usage
            cpuLabel.text = "CPU: " + usage.toFixed(1) + "%"
        }
        
        onMemoryUsageChanged: function(usage) {
            memoryProgressBar.value = usage
            memoryLabel.text = "内存: " + usage.toFixed(1) + "%"
        }
        
        onMemoryTotalChanged: function(total) {
            memoryTotalLabel.text = "总内存: " + total + " MB"
        }
        
        onMemoryUsedChanged: function(used) {
            memoryUsedLabel.text = "已用: " + used + " MB"
        }
        
        onNetworkSpeedChanged: function(download, upload) {
            downloadLabel.text = "下载: " + download.toFixed(2) + " MB/s"
            uploadLabel.text = "上传: " + upload.toFixed(2) + " MB/s"
        }
    }
    
    Rectangle {
        anchors.fill: parent
        color: "#f5f5f5"
        
        ColumnLayout {
            anchors.fill: parent
            anchors.margins: 20
            spacing: 20
            
            // 标题
            Text {
                text: "🖥️ 系统监控"
                font.pixelSize: 24
                font.bold: true
                color: "#333333"
                Layout.alignment: Qt.AlignHCenter
            }
            
            // CPU 监控
            Rectangle {
                Layout.fillWidth: true
                height: 80
                color: "#ffffff"
                radius: 8
                border.color: "#e0e0e0"
                border.width: 1
                
                ColumnLayout {
                    anchors.fill: parent
                    anchors.margins: 15
                    spacing: 8
                    
                    Text {
                        id: cpuLabel
                        text: "CPU: 0.0%"
                        font.pixelSize: 16
                        font.bold: true
                        color: "#333333"
                    }
                    
                    ProgressBar {
                        id: cpuProgressBar
                        Layout.fillWidth: true
                        from: 0
                        to: 100
                        value: 0
                    }
                }
            }
            
            // 内存监控
            Rectangle {
                Layout.fillWidth: true
                height: 120
                color: "#ffffff"
                radius: 8
                border.color: "#e0e0e0"
                border.width: 1
                
                ColumnLayout {
                    anchors.fill: parent
                    anchors.margins: 15
                    spacing: 8
                    
                    Text {
                        id: memoryLabel
                        text: "内存: 0.0%"
                        font.pixelSize: 16
                        font.bold: true
                        color: "#333333"
                    }
                    
                    ProgressBar {
                        id: memoryProgressBar
                        Layout.fillWidth: true
                        from: 0
                        to: 100
                        value: 0
                    }
                    
                    RowLayout {
                        Layout.fillWidth: true
                        spacing: 20
                        
                        Text {
                            id: memoryTotalLabel
                            text: "总内存: 0 MB"
                            font.pixelSize: 12
                            color: "#666666"
                        }
                        
                        Text {
                            id: memoryUsedLabel
                            text: "已用: 0 MB"
                            font.pixelSize: 12
                            color: "#666666"
                        }
                    }
                }
            }
            
            // 网络监控
            Rectangle {
                Layout.fillWidth: true
                height: 80
                color: "#ffffff"
                radius: 8
                border.color: "#e0e0e0"
                border.width: 1
                
                ColumnLayout {
                    anchors.fill: parent
                    anchors.margins: 15
                    spacing: 8
                    
                    Text {
                        text: "🌐 网络速度"
                        font.pixelSize: 16
                        font.bold: true
                        color: "#333333"
                    }
                    
                    RowLayout {
                        Layout.fillWidth: true
                        spacing: 20
                        
                        ColumnLayout {
                            spacing: 4
                            
                            Text {
                                text: "下载"
                                font.pixelSize: 12
                                color: "#666666"
                            }
                            
                            Text {
                                id: downloadLabel
                                text: "0.00 MB/s"
                                font.pixelSize: 14
                                font.bold: true
                                color: "#4CAF50"
                            }
                        }
                        
                        ColumnLayout {
                            spacing: 4
                            
                            Text {
                                text: "上传"
                                font.pixelSize: 12
                                color: "#666666"
                            }
                            
                            Text {
                                id: uploadLabel
                                text: "0.00 MB/s"
                                font.pixelSize: 14
                                font.bold: true
                                color: "#FF9800"
                            }
                        }
                    }
                }
            }
            
            // 底部信息
            RowLayout {
                Layout.fillWidth: true
                spacing: 20
                
                Text {
                    text: "🔄 实时更新"
                    font.pixelSize: 12
                    color: "#666666"
                }
                
                Text {
                    text: "📊 系统监控插件 v1.0"
                    font.pixelSize: 12
                    color: "#666666"
                }
            }
        }
    }
}
